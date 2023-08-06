#!/usr/bin/env python

#
# Copyright (c) 2019-2022 Knuth Project
#

from setuptools import setup
from setuptools.command.install import install
import subprocess
import os

__title__ = "kthbuild"
__summary__ = "Knuth node build tools"
__uri__ = "https://github.com/k-nuth/kthbuild"
__version__ = "1.0.8"
__author__ = "Fernando Pelliccioni"
__email__ = "fpelliccioni@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2019-2022 Knuth Project"


install_requires = [
    "conan >= 1.51.0",
    "microarch >= 0.0.3",
]

def running_in_cpt_context():
    # -e CONAN_UPLOAD="https://knuth.jfrog.io/artifactory/api/conan/knuth@True@upload_repo"
    # -e CONAN_REMOTES="https://knuth.jfrog.io/artifactory/api/conan/knuth@True@upload_repo,https://api.bintray.com/conan/bitprim/bitprim@True@remote1"
    # -e CONAN_REFERENCE="kth-infrastructure/0.6.0@kth/feature-ci-marchs"
    # -e CPT_PROFILE="@@include(default)@@@@[settings]@@arch=x86_64@@build_type=Release@@compiler=gcc@@compiler.version=9@@[options]@@kth-infrastructure:shared=False@@kth-infrastructure:march_id=4fZKi37a595hP@@kth-infrastructure:with_tests=False@@kth-infrastructure:with_examples=False@@[env]@@KTH_BRANCH=feature-ci-marchs@@KTH_CONAN_CHANNEL=feature-ci-marchs@@KTH_FULL_BUILD=0@@KTH_CONAN_VERSION=0.6.0@@[build_requires]@@@@"
    return (os.getenv("CONAN_UPLOAD", None) != None or
           os.getenv("CONAN_REMOTES", None) != None or
           os.getenv("CONAN_REFERENCE", None) != None or
           os.getenv("CPT_PROFILE", None) != None)

class PostInstallCommand(install):
    """Override Install
    """
    def run(self):
        install.run(self)
        if not running_in_cpt_context():
            self.__setup_conan_remote("kthbuild_kth_temp_",     'https://knuth.jfrog.io/artifactory/api/conan/knuth')
            # self.__setup_conan_remote("kthbuild_tao_temp_",    'https://taocpp.jfrog.io/artifactory/api/conan/tao')
            self.__setup_conan_remote("tao",                    'https://taocpp.jfrog.io/artifactory/api/conan/tao')

    def __setup_conan_remote(self, remote_alias, remote_url):
        try:
            # remote_alias = "kthbuild_kth_temp_"
            # remote_url = 'https://knuth.jfrog.io/artifactory/api/conan/knuth'
            params = ["conan", "remote", "add", remote_alias, remote_url]
            res = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = res.communicate()
            if output:
                if res.returncode == 0:
                    # return output.decode("utf-8")
                    print("OK in __setup_conan_remote")

            print("Error in __setup_conan_remote 0")
            # return default
        except OSError: # as e:
            print("Error in __setup_conan_remote 1")
            # return default
        except:
            print("Error in __setup_conan_remote 2")
            # return default

setup(
    name = __title__,
    version = __version__,
    description = __summary__,
    long_description=open("./README.rst").read(),
    license = __license__,
    url = __uri__,
    author = __author__,
    author_email = __email__,

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],

    # What does your project relate to?
    keywords='knuth kth crypto bitcoin btc bch cash build tool',

    py_modules=["kthbuild"],

    install_requires=install_requires,
    # setup_requires=setup_requires,


    dependency_links=[
        'https://testpypi.python.org/pypi',
    ],

    cmdclass={'install': PostInstallCommand},

    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },
)

