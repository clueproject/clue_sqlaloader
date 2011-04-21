import argparse
import yaml
import sys
import zope.dottedname.resolve
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger('clue_sqlaloader')


class Reference(object):

    def __init__(self, loader, refname):
        self.__reference_loader__ = loader
        self.__reference_refname__ = refname

    @property
    def __reference_obj__(self):
        v = self.__reference_refname__.value
        return self.__reference_loader__.references[v]

    def __getattr__(self, k):
        return getattr(self.__reference_obj__, k)

    def __repr__(self):
        return '<Reference refname=%s>' % self.__reference_refname__.value


class Loader(yaml.Loader):

    dotted = staticmethod(zope.dottedname.resolve.resolve)
    open = staticmethod(open)

    def __init__(self, session):
        self.session = session
        self.yaml_constructors = dict(yaml.Loader.yaml_constructors)

        self.yaml_constructors[u'tag:yaml.org,2002:str'] = \
            self.construct_yaml_str
        self.yaml_constructors[u'tag:yaml.org,2002:refname'] = \
            self.construct_refname
        self.yaml_constructors[u'tag:yaml.org,2002:ref'] = self.construct_ref

        self.references = {}

    def construct_yaml_str(self, loader, node):
        # Override the default string handling function
        # to always return unicode objects
        return loader.construct_scalar(node)

    def construct_refname(self, loader, node):
        return node.value

    def construct_ref(self, loader, node):
        return Reference(self, node)

    def load_from_list(self, data):
        for record in data:
            model = self.dotted(record['model'])
            fields = record.get('fields', {})

            for k, v in fields.items():
                if isinstance(v, Reference):
                    fields[k] = v.__reference_obj__
                    self.session.flush()

            obj = model(**fields)
            for fname, value in record.get('execute', {}).items():
                f = getattr(obj, fname)
                f(value)

            args = ['%s=%s' % (k, v) for k, v in fields.items()]

            logger.debug('New object: %s(%s)' %
                         (obj.__class__.__name__, ','.join(args)))
            self.session.add(obj)

            refname = record.get('refname')
            if refname:
                self.references[refname] = obj

        self.session.flush()

    def load_from_yamls(self, s):
        data = yaml.load(s, self)
        return self.load_from_list(data)

    def load_from_yamlf(self, filename):
        f = None
        try:
            f = self.open(filename)
            return self.load_from_yamls(f)
        finally:
            f.close()

    def __call__(self, s):
        yaml.Loader.__init__(self, s)
        return self


class Main(object):

    create_engine = staticmethod(create_engine)
    sessionmaker = staticmethod(sessionmaker)
    loader_factory = staticmethod(Loader)
    parser_factory = staticmethod(argparse.ArgumentParser)

    def load(self, engine_url, *filenames):
        engine = self.create_engine(engine_url)
        session = self.sessionmaker(engine)()
        loader = self.loader_factory(session)
        for filename in filenames:
            loader.load_from_yamlf(filename)
        session.commit()

    def __call__(self, args=sys.argv[1:]):
        parser = self.parser_factory(prog='sqlaloader')
        parser.add_argument('engine_url',
                            help='SQLAlchemy url to connect with')
        parser.add_argument('filenames', metavar='file',
                            help='Files to load', nargs='+')
        ns = parser.parse_args(args)
        self.load(ns.engine_url, *ns.filenames)

main = Main()
load = main.load

if __name__ == '__main__': main()
