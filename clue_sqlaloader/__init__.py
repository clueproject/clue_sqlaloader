import argparse
import yaml
import sys
import zope.dottedname.resolve
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger('clue_sqlaloader')


class YamlParser(yaml.Loader):
    pass


def construct_yaml_str(self, node):
    # Override the default string handling function
    # to always return unicode objects
    return self.construct_scalar(node)
YamlParser.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


class Loader(object):

    resolve = staticmethod(zope.dottedname.resolve.resolve)
    open = staticmethod(open)

    def __init__(self, session):
        self.session = session

    def load_from_list(self, data):
        for record in data:
            model = self.resolve(record['model'])
            fields = record.get('fields', {})
            obj = model(**fields)
            for fname, value in record.get('execute', {}).items():
                f = getattr(obj, fname)
                f(value)

            args = ['%s=%s' % (k, v) for k, v in fields.items()]

            logger.debug('New object: %s(%s)' %
                         (obj.__class__.__name__, ','.join(args)))
            self.session.add(obj)

        self.session.flush()

    def load_from_yamls(self, s):
        data = yaml.load(s, YamlParser)
        return self.load_from_list(data)

    def load_from_yamlf(self, filename):
        f = None
        try:
            f = self.open(filename)
            return self.load_from_yamls(f)
        finally:
            f.close()


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
