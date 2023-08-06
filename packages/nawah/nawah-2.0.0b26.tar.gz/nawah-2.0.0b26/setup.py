"""Python package setup for Nawah Framework"""

from distutils.command.install import install

import setuptools

from nawah import __version__


class Version(install):
    """Provides setup command to print Nawah Framework version"""

    def run(self):
        print(__version__)


class ApiLevel(install):
    """Provides setup command to print Nawah Framework API Level"""

    def run(self):
        print(".".join(__version__.split(".")[:2]))


with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

with open("./requirements.txt", "r", encoding="UTF-8") as f:
    requirements = f.readlines()

with open("./dev_requirements.txt", "r", encoding="UTF-8") as f:
    dev_requirements = f.readlines()

packages = setuptools.find_packages(exclude=["tests*"])

package_data = {package: ["py.typed"] for package in packages}
package_data["nawah"].append("version.txt")

setuptools.setup(
    name="nawah",
    version=__version__,
    author="Mahmoud Abduljawad",
    author_email="mahmoud@masaar.com",
    description="Nawah framework--Rapid app development framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nawah-io/nawah_framework",
    package_data=package_data,
    packages=packages,
    project_urls={
        "Docs: Github": "https://github.com/nawah-io/nawah_docs",
        "GitHub: issues": "https://github.com/nawah-io/nawah_framework/issues",
        "GitHub: repo": "https://github.com/nawah-io/nawah_framework",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.10.2",
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    cmdclass={
        "version": Version,
        "api_level": ApiLevel,
    },
    entry_points={
        "console_scripts": {
            "nawah = nawah.__main__:main",
        }
    },
    zip_safe=False,
)
