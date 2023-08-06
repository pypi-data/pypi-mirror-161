import versioneer
from setuptools import setup, find_packages
from pathlib import Path


install_requires = [
    "aiohttp",
    "chardet",
    "gevent",
    "pybreaker",
    "PyYAML",
    "redis",
    "retrying",
    "requests",
]

tests_require = [
    "Contexts",
    "fakeredis",
    "freezegun",
    "HTTPretty==0.8.10",
]

extras = {
    "test": tests_require,
}

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="AtomicPuppy",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    package_data={"atomicpuppy": ["py.typed"]},
    install_requires=install_requires,
    tests_require=tests_require,
    url="https://github.com/madedotcom/atomicpuppy",
    description="A service-activator component for eventstore",
    author="Bob Gregory",
    author_email="bob@made.com",
    keywords=["eventstore"],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
