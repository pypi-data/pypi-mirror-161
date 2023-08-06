from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="xtlearn",
    version="0.0.25",
    url="https://github.com/emdemor/xtlearn",
    license="MIT License",
    author="Eduardo M. de Morais",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="emdemor415@gmail.com",
    keywords="preprocessing",
    description=u"This is a package with classes to be used in sklearn pipelines with pandas dataframes",
    packages=["xtlearn"],
    install_requires=["numpy", "scipy", "pandas", "setuptools", "tqdm", "scikit-learn"],
)
