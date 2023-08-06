from setuptools import setup, find_packages

setup(
    install_requires=[
            'orjson',
        ],
    name='py-fastapi-logging',
    version='0.1.10a2',
    packages=find_packages(exclude=['tests']),
    url='',
    license='',
    author='Dmitry Akhnazarov',
    author_email='wikedwolf@ya.ru',
    description='FastAPI logging requests'
)
