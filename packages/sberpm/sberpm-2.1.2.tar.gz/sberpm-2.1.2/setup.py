import setuptools
import re
from pathlib import Path
this_directory = Path(__file__).parent


version_file = "sberpm/_version.py"


def get_version(version_file):
    version_line = open(version_file, "rt").read()
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    result = re.search(pattern, version_line, re.M)
    if result:
        return result.group(1)
    else:
        raise RuntimeError(f"Unable to find version string in {version_file}.")


def get_packages():
    packages_list = ['sberpm',
                     'sberpm.bpmn',
                     'sberpm.bpmn._bpmn_graph_to_file',
                     'sberpm.graph_stats',
                     'sberpm.metrics',
                     'sberpm.miners',
                     'sberpm.ml',
                     'sberpm.ml.utils',
                     'sberpm.visual',
                     'sberpm.ml.chronometrage'
                     ]

    return packages_list


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setuptools.setup(
    name="sberpm",
    version=get_version(version_file),
    author="Sberbank Process Mining Team",
    author_email="AABugaenko@sberbank.ru",
    description="Library for Process Mining",
    long_description = (this_directory / "README.md").read_text(),
    long_description_content_type='text/markdown',
    packages=get_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    install_requires=parse_requirements('requirements.txt'),
)
