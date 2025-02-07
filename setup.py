from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name='gambax',
    version='0.1.0',
    author='Luis Denninger',
    author_email='l_denninger@uni-bonn.de',
    description='Gambax is a development tool for distributed AI systems.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/LDenninger/Gambax',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'gambax=gambax.interfaces.cli.main:main',
            'gambax-server=gambax.core.server:launch_server',
            'gambax-config=gambax.config.cli:main',
        ],
    },
    package_data={
        "gambax": ["gambax/config/*.json"]
    }

)
