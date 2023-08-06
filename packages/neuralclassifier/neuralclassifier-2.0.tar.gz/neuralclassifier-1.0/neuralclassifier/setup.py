from setuptools import setup, find_packages
setup( 
    name='neuralclassifier', 
    version='1.0', 
    packages=find_packages() + ['data'],
    
    include_package_data=True
)