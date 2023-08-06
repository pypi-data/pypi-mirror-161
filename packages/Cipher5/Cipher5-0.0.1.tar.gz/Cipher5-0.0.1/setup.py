from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'A package with 5 simple ciphers'
LONG_DESCRIPTION = 'Contains 5 ciphers: the Affine cipher, the Bacon cipher, the Caeser cipher, the greek square cipher, and the rail fence cipher'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Cipher5", 
        version=VERSION,
        author="Vikram Fox and Jacob Friedman",
        author_email="vikramsfox@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'cipher', 'encryption', 'decryption'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)