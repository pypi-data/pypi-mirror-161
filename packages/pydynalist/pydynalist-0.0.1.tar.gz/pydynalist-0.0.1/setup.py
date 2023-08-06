from setuptools import setup, find_packages


setup(
    name="pydynalist",
    version="0.0.1",
    license="MIT",
    author="Roman Smolnyk",
    author_email="poma23324@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://gitlab.com/roman-smolnyk/dynalist",
    keywords="Dynalist",
    install_requires=[
        "requests",
    ],
)
