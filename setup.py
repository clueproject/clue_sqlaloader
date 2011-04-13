import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'SQLAlchemy >= 0.6.1',
    'PyYAML',
    ]

setup(name='clue_sqlaloader',
      version='0.1',
      description='Data loader for SQLAlchemy',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "License :: OSI Approved :: BSD License",
        ],
      license='BSD',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://github.com/clueproject/clue_sqlaloader',
      keywords='sqlalchemy clue yaml sql',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite="clue_sqlaloader.tests",
      )
