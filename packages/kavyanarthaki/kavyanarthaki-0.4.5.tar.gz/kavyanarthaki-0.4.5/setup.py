## sudo apt-get install python3.8-venv
## sudo -H pip3 install build
## sudo -H pip3 install twine
## python3 -m build
## python3 -m twine upload --repository pypi dist/*

from setuptools import setup, find_packages


setup(
    name='kavyanarthaki',
    version='0.4.5',
    license='MIT',
    author="Prof. Achuthsankar S Nair, Vinod M P",
    author_email='sankar.achuth@gmail.com, mpvinod625@gmail.com',
    packages=find_packages('src'),
    include_package_data=True,
    package_data={
        "": ["*.txt"],
        "kavyanarthaki": ["data/*.csv","data/*.matrix"],
    },
    package_dir={'': 'src'},
    url='https://github.com/dcbfoss/vritham',
    keywords='kavyanarthaki malayalam meter analysis',
    install_requires=[],
)
