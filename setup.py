from setuptools import setup

setup(
    name='AEDeveloper',
    version='0.0.1',
    description='AvidaED Developer Web Utilities',
    author='Matthew Rupp',
    author_email='ruppmatt@gmail.com',
    packages=['AEDeveloper'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Pygments',
        'mysql-connector',
        'flask-security',
        'flask-cors',
        'colorama',
        'bcrypt'
    ],
)
