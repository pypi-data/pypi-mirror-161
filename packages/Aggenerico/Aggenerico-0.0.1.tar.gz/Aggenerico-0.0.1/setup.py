#from setuptools import setup
#find_packagesVERSION = '0.0.1'
#DESCRIPTION = 'My first Python package'
#LONG_DESCRIPTION = 'My first Python package with a slightly longer description'
## Setting upsetup(       
## the name must match the folder name 'verysimplemodule'        
#name="aggenerico",         
#version='0.0.1',        
#author="Marcyhel da Silva Menezes",        
#author_email="h.marcyhel2012@gmail.com",       
#description=DESCRIPTION,        
#long_description=LONG_DESCRIPTION,        
##packages=find_packages(),        
#install_requires=[], # add any additional packages that         
## needs to be installed along with your package. 
#Eg: 'caer'                
#keywords=['python', 'first package'],        
#classifiers= [  "Development Status :: 3 - Alpha", "Intended Audience :: Education",   "Programming Language :: Python :: 2",  "Programming Language :: Python :: 3",   "Operating System :: MacOS :: MacOS X",   "Operating System :: Microsoft :: Windows", ] 


from setuptools import setup


setup(name='Aggenerico',
    version='0.0.1',
    #url='https://github.com/caiocarneloz/pacotepypi',
    license='MIT License',
    author='Marcyhel da Silva Menezes',
    long_description='My first Python package with a slightly longer description',
    long_description_content_type="text/markdown",
    author_email='h.marcyhel2012@gmail.com',
    keywords='Pacote',
    description=u'Exemplo de pacote PyPI',
    packages=['aggenerico'],
    install_requires=[],)

