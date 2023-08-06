from setuptools import setup, find_packages

VERSION = '1.0.2' 
DESCRIPTION = 'My first PPSD package'
LONG_DESCRIPTION = 'My first Python package with a slightly longer description'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="ppsd", 
        version=VERSION,
        author="Ankit Kumar Honey",
        author_email="test@email.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        url='https://github.com/dsp-testing/ppsd',
        project_urls={
          "Documentation": "https://github.com/dsp-testing/ppsd",
          "Source Code": "https://github.com/dsp-testing/ppsd",
        },
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        keywords=['python', 'first package'],
)
