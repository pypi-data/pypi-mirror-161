from setuptools import setup

setup(
    name='aioheroku3',
    version='2.0',
    packages=['aioheroku3', 'aioheroku3.errors', 'aioheroku3.methods', 'aioheroku3.methods.accounts'],
    url='https://github.com/DoellBarr/aioheroku3',
    license='MIT',
    author='ShohihAbdul',
    author_email='shohih242@gmail.com',
    description='Asynchronous Heroku wrapper library.',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ]
)
