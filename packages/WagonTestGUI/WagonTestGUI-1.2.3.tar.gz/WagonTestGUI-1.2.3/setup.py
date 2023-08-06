from setuptools import setup, find_packages
from pathlib import Path

print("\n\n\n\n\n{}\n\n\n\n".format( find_packages(where='.')))

this_directory = Path(__file__).parent


setup(
    name='WagonTestGUI',
    version='1.2.3', 
    description='Python scripts to be located on the user interface computer.',
    long_description = (this_directory / "README.md").read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/UMN-CMS/WagonTestGUI',
    author='Garrett Schindler, Andrew Kirzeder, & Bryan Crossman',
    author_email='none@gmail.com',
    packages= find_packages(
            where='.',
            ),
    include_package_data = True,
    package_data = {
        "": ["*.png", "*.json"]
    },
    install_requires=[
            'numpy',
            'matplotlib',
            'multiprocessing',
            'subprocess',
            'socket',
            'audioop',
            'logging',
            'json'
            ]
    

)
