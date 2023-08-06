#######################################################################################
#
#   An Example Package For The Book
#	Developper:	Abdulkadir GÜNGÖR (abdulkadir_gungor@outlook.com)
#	Date:	08/2022
#	All Rights Reserved (Tüm Hakları Saklıdır)
#
#######################################################################################
from setuptools import setup, find_packages

# [1] Constant variable(s)
NAME = "gungor_package"
VERSION = '0.0.4'
AUTHOR = "Abdulkadir Gungor"
AUTHOR_EMAIL = "abdulkadir_gungor@outlook.com"
DESCRIPTION = 'An Example Package For The Book'
LONG_DESCRIPTION = 'A package that contains a function that says Turkish "Hi Everybody"'

# [2] Setting Up
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'python3', 'Turkish', 'Turkish', 'hello', 'gungor', 'an example package' ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
