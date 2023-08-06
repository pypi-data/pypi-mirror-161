from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Hello world.'
LONG_DESCRIPTION = 'A package that says Hello world! My first pypi package.'

setup(
    name="helloworldcdaly",
    version=VERSION,
    author="caolan947 (Caolán Daly)",
    author_email="<caolan.day94@gmail.com>",
    description=DESCRIPTION,
     long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'helloworld', 'hello', 'world'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
