from distutils.core import setup


setup(
    name='syncli',
    version='0.0.2',
    author='Sumeet Singh',
    author_email='singhsays@gmail.com',
    packages=['syncli'],
    url='http://pypi.python.org/pypi/syncli/',
    license='LICENSE.txt',
    description='Python CLI for Synology DSM.',
    long_description=open('README.txt').read(),
    install_requires=[
      "PyYaml >= 3.10",
      "requests >= 1.2.3",
    ],
    entry_points={
      'console_scripts': [
        'syncli = syncli.syncli:main'
      ]
    }
)

