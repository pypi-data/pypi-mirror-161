from setuptools import setup, find_packages

VERSION = '0.1'
DESCRIPTION = 'A dice rolling simulator'
LONG_DESCRIPTION = 'Asks for the amount of dice rolls and prints the rolls to screen'

# Setting up
setup(
    name="numofdicerolls",
    version=VERSION,
    author="Dean",
#    author_email="<>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'dice', 'random'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
