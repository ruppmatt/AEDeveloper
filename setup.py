from setuptools import setup

setup(
    name='AEDeveloper',
    packages=['AEDeveloper'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Pygments',
        'mysql-connector',
    ],
)
