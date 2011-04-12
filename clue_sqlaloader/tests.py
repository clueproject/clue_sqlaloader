from StringIO import StringIO
import unittest


class LoaderTests(unittest.TestCase):

    def setUp(self):
        from clue_sqlaloader import Loader
        self.session = MockSession()
        self.loader = Loader(self.session)

    def test_load_from_list(self):
        self.loader.load_from_list([
                {'model': 'clue_sqlaloader.tests.MockDataObject',
                 'fields': {'abc': 'ghi'},
                 'execute': {'set_foo': 1}}
                ])
        self.assertEqual(self.session.objects,
                         [MockDataObject(abc='ghi',
                                         foo=1)])

    def test_load_from_yamls(self):
        self.loader.load_from_yamls(
            '- model: clue_sqlaloader.tests.MockDataObject')
        self.assertEqual(self.session.objects,
                         [MockDataObject()])

    def test_load_from_yamlf(self):
        data = '- model: clue_sqlaloader.tests.MockDataObject'

        def mockfile(filename, data=data):
            return MockFile(filename, data)
        self.loader.open = mockfile

        self.loader.load_from_yamlf('foo.yaml')
        self.assertEqual(self.session.objects,
                         [MockDataObject()])


class MainTests(unittest.TestCase):

    def setUp(self):
        from clue_sqlaloader import Main
        self.main = Main()

        class MockParser(object):
            def add_argument(self, *args, **kwargs):
                pass

            def parse_args(self, argv):
                return MockDataObject(engine_url='foo',
                                      filenames=[])

        self.main.parser_factory = lambda prog: MockParser()
        self.main.create_engine = lambda url: None

        class MockLoader(object):
            def __init__(self, o):
                pass

            def load_from_yamlf(self, f):
                pass

        self.main.loader_factory = MockLoader

    def test_load(self):
        self.main.load('foo', 'abc.yaml')

    def test_main(self):
        self.main()


class MockSession(object):

    def __init__(self):
        self.objects = []

    def flush(self):
        pass

    def add(self, o):
        self.objects.append(o)


class MockDataObject(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def set_foo(self, v):
        self.foo = v

    def __cmp__(self, obj):
        return cmp(self.__dict__, obj.__dict__)


class MockFile(object):
    def __init__(self, name, data=''):
        self.name = name
        self.data = StringIO(data)

    def close(self):
        pass

    def read(self, *args, **kwargs):
        return self.data.read(*args, **kwargs)
