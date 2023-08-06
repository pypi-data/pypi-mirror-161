import setuptools
import os

VERSION = "0.0.1"
ROOT = os.path.dirname(__file__)
PACKAGE_DIR = os.path.join(ROOT, '.')


def get_requirements():
    """Reads the requirements from ``requirements.txt``.

    :returns: a list of requirements
    """
    path = os.path.join(ROOT, 'requirements.txt')
    with open(path, 'r') as f:
        return list(line.strip() for line in f)


setuptools.setup(
        name="enabler",
        version=VERSION,
        author="MatthieuRU",
        description="An efficient way to enable python pipeline.",
        packages=setuptools.find_packages(PACKAGE_DIR),
        url="https://github.com/MatthieuRu/enabler",
        install_requires=get_requirements(),
        package_dir={"": PACKAGE_DIR},
)
