from setuptools import setup
import ad_notify

DESCRIPTION = "notify library"
NAME = 'ad_notify'
AUTHOR = 'Toshiaki Kosuga'
AUTHOR_EMAIL = 'toshiaki.kosuga@gmail.com'
URL = 'https://github.com/ad-developer-tk'
LICENSE = 'BSD License'
DOWNLOAD_URL = 'https://github.com/ad-developer-tk/notify'
VERSION = ad_notify.__version__
PYTHON_REQUIRES = ">=3.6"

INSTALL_REQUIRES = []

EXTRAS_REQUIRE = {
    'tutorial': []
}

PACKAGES = ['ad_notify']

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3.6',
]

with open('README.md', 'r', encoding="utf-8") as fp:
    readme = fp.read()

long_description = readme

setup(name=NAME,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=AUTHOR,
      maintainer_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=long_description,
      license=LICENSE,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      python_requires=PYTHON_REQUIRES,
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      packages=PACKAGES,
      classifiers=CLASSIFIERS
    )