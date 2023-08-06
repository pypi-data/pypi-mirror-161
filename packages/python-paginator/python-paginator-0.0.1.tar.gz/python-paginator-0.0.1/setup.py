from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Python object paginator'
LONG_DESCRIPTION = 'Python object paginator which split list of objects into pages.'

# Setting up
setup(
    name="python-paginator",
    version=VERSION,
    author="Patryk Dąbrowski",
    author_email="tibiasportex@gmail.com",
    license_files=('LICENSE.txt',),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['setuptools_git >= 0.3'],
    install_requires=['pydantic'],
    exclude_package_data={'': ['.gitignore', 'requirements.txt']},

    keywords=['python', 'paginator'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
