from setuptools import setup, find_packages


package_name = "api-safebooru"
VERSION =  "0.0.1"
DESCRIPTION = "Basic safebooru.org API wrapper."


setup(
    author="salad",
    author_email="salad.devel@gmail.com",
    name=package_name,
    version=VERSION,
    description="A basic safebooru API wrapper module.",
    license="General Public License V3",
    url="https://github.com/sa-lad/safebooru/",
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    keywords="safebooru",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Utilities"
    ],
)