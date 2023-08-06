from setuptools import setup

setup(
    name='pyckaged',
    version='1.2.2',
    entry_points={
        #the only files are __main__.py and __init__.py so 'pyckaged:main' is the only entry point
        #pyckaged:main means the main function in __main__.py
        'console_scripts': [
            'pyckaged = pyckaged.pyckaged:main',
        ],
    },
    packages=['pyckaged'],
    readme = 'readme.md',
    install_requires=[
        'requests',
        'colorama',
        'termcolor',
        'pyfiglet'
    ],
    author='LeWolfYT',
    author_email='ciblox3@gmail.com',
    description='A package manager made with python! If you want your package to be added to the repository, please contact me!',
    license='MIT',
    keywords='package manager'
    )