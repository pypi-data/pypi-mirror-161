from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'Symetry is web development which providing full stack development feature out of the box.'

setup(
    name='symetry',
    version='1.0.0',
    author='Ashish Sahu',
    author_email='spiraldeveloper@gmail.com',
    url='https://github.com/stacknix/symetry',
    description='Symetry is web development framework.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'symetry = symetry.cli:cli'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='python package symetry',
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False
)
