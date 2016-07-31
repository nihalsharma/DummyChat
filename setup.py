from setuptools import setup
from os import getcwd, path

if not path.dirname(__file__):
    _dir_name = getcwd()
else:
    _dir_name = path.dirname(path.dirname(__file__))


def read(name, default=None, debug=True):
    try:
        filename = path.join(_dir_name, name)
        with open(filename) as f:
            return f.read()
    except Exception as e:
        err = "%s: %s" % (type(e), str(e))
        if debug:
            print(err)
        return default


def lines(name):
    txt = read(name)
    return map(
        lambda l: l.lstrip().rstrip(),
        filter(lambda t: not t.startswith('#'), txt.splitlines() if txt else [])
    )


install_requires = [i for i in lines("requirements.txt") if '-e' not in i]

setup(
    name='nikki_chat',
    version='1.0.0',
    author='Nihal',
    url='',
    description='nikki_chat',
    packages=['chat'],
    install_requires=install_requires
)
