from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent


VERSION = '0.0.7'
DESCRIPTION = 'A basic gradio class, class function, and functional decorator'
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="gradioWrapper",
    version=VERSION,
    author="Luca Vivona",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    url="https://github.com/LVivona/GradioWrapper",
    install_requires=['gradio'],
    keywords=['python', 'sockets', 'artificial intelligence', 'machine learning', 'visualization', 'wrapper', 'decorator', 'testing'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)