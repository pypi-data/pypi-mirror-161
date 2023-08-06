from setuptools import setup, find_packages

VERSION = '0.3.2' 
DESCRIPTION = 'Integration/E2E test tools for SDVI Rally'
LONG_DESCRIPTION = 'A set of tools for running and verifying results for presets/supply chains in SDVI Rally'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="rallytt", 
        version=VERSION,
        author="Carson O'Ffill",
        author_email="offillcarson@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["requests","colorama"],
        keywords=['python', 'sdvi rally', 'integration test', 'end to end test', 'e2e test', 'testing tools'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows"
        ]
)