from setuptools import setup, find_packages

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="PyHa-test", 
        version="0.0.11",
        author="Jacob Ayers, Sean Perry, Sam Prestrelski, Vannessa Salgado",
        #author_email="<youremail@email.com>",
        description="A python package for automatically detecting species and comparing to ground truth",
        #long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)