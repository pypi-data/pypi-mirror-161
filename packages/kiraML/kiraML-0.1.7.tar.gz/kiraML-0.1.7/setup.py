from setuptools import find_packages, setup
import sys
sys.path.append('kiraML')
from _version import __version__ 
# from pathlib import Path
# this_directory = Path(__file__).parent
# long_description = (this_directory / "kiraML/README.md").read_text()

long_description = """This is the KiraML Library, used for Kira-Learning AI courses."""

setup(
    name='kiraML',
    packages=find_packages(include=['kiraML']),
    version=__version__,
    description='The KiraML library',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Kira Learning',
    license='MIT',
    install_requires=['scikit-learn', 'matplotlib'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
