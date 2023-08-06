import sys

from setuptools import setup, find_packages

number_of_arguments = len(sys.argv)
version_parameter = sys.argv[-1]
version_provided = version_parameter.find("version=")

if version_provided > -1:
    version = version_parameter.split("version=")[1]
    sys.argv = sys.argv[0:number_of_arguments-1]
else:
    version = '0.0.1'

NAME = "kdp-python-connector"
DESCRIPTION = 'Python Connector for KDP Platform'
LONG_DESCRIPTION = 'Python Connector For Interacting with KDP Platform for various ingestion and retrieval tasks'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name=NAME,
        version=version,
        author="Koverse development team",
        author_email="developer@koverse.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['pandas', 'numpy', 'kdp-api-python-client'], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'

        keywords=['python', 'kdp'],
        # classifiers= [
        #     "Development Status :: 3 - Alpha",
        #     "Intended Audience :: Science/Research",
        #     "Intended Audience :: Developers",
        #     "Programming Language :: Python :: 3.8",
        #     "Operating System :: MacOS :: MacOS X",
        # ]
)
