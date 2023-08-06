from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup( 
    name='neuralclassifier', 
    version='1.0', 
    packages=find_packages() + ['neuralclassifier/data'],
    
    include_package_data=True
)