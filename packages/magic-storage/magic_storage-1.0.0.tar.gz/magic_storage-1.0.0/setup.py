#!/usr/bin/python3
import re
from pathlib import Path
from typing import Any, List, Union

from setuptools import find_packages, setup

REPOSITORY_ROOT_DIR = Path(__file__).parent
PACKAGE_NAME = "magic_storage"
SOURCE_DIR = REPOSITORY_ROOT_DIR / "source"
PACKAGE_CODE_DIR = SOURCE_DIR / PACKAGE_NAME

# Regular expression is used to extract version from magic_storage/__init__.py file
VERSION_REGEX = re.compile(r'''__version__.*?=.*?"(\d+\.\d+\.\d+.*?)"''')


def fetch_utf8_content(file_path: Union[str, Path]) -> str:
    """Acquire utf-8 encoded content from file given by file_path."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def fetch_requirements(file_path: Union[str, Path]) -> list[str]:
    """Fetch list of required modules from `requirements.txt`."""
    requirements_list: List[str] = []
    with open(file_path, "r", encoding="utf-8") as file:
        for requirement in file.readlines():
            requirement = requirement.strip()

            if requirement.startswith("#"):
                continue

            if requirement.startswith("-r"):
                requirements_list.extend(
                    fetch_requirements(
                        REPOSITORY_ROOT_DIR / requirement.lstrip("-r").strip()
                    )
                )
            else:
                requirements_list.append(requirement)

        return requirements_list


def fetch_version(init_file: Path) -> str:
    """Fetch package version from root `__init__.py` file."""
    with init_file.open("r", encoding="utf-8") as file:
        version_math = VERSION_REGEX.search(file.read())
        assert version_math is not None
        return version_math.group(1)


NAME = PACKAGE_NAME
VERSION = fetch_version(PACKAGE_CODE_DIR / "__init__.py")
LICENSE_NAME = "MIT"
SHORT_DESCRIPTION = (
    "Small Python 3 library providing wrapper classes for storage (caching) "
    "of test resources (and unintentionally other types of resources too)."
)
LONG_DESCRIPTION = fetch_utf8_content("README.md")
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
INSTALL_REQUIRES = fetch_requirements(REPOSITORY_ROOT_DIR / "requirements.txt")

AUTHOR = "argmaster.world@gmail.com"
AUTHOR_EMAIL = "argmaster.world@gmail.com"
URL = "https://github.com/Argmaster/magic-storage"

CLASSIFIERS = [
    # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    "Intended Audience :: Developers",
    "Operating System :: Unix",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Utilities",
]
PROJECT_URLS = {
    "GitHub": "https://github.com/Argmaster/magic-storage",
}
KEYWORDS = [
    "python-3",
    "python-3.9",
    "python-3.10",
]
EXTRAS_REQUIRE = {
    "dev": fetch_requirements(REPOSITORY_ROOT_DIR / "requirements-dev.txt"),
}
ENTRY_POINTS: dict[str, Any] = {}
PYTHON_REQUIREMENTS = ">=3.9"

PACKAGES = find_packages(where="source")
PACKAGE_DIR = {"": "source"}
ZIP_SAFE = False


def run_setup_script() -> None:
    """Run setup(...) with all constants set in this module."""
    setup(
        # look-nice stuff
        name=NAME,
        version=VERSION,
        license=LICENSE_NAME,
        description=SHORT_DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        project_urls=PROJECT_URLS,
        entry_points=ENTRY_POINTS,
        # requires
        python_requires=PYTHON_REQUIREMENTS,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        # packaging (important) stuff
        packages=PACKAGES,
        package_dir=PACKAGE_DIR,
        zip_safe=ZIP_SAFE,
        include_package_data=True,
    )


if __name__ == "__main__":
    run_setup_script()
