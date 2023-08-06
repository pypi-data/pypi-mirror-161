from setuptools import setup, find_packages

# uses a markdown file README, if you don't have that then 
# delete the .md or something.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gravbody",
    version="0.1.0",
    author="Uzair Nawaz",
    author_email="uzairn@icloud.com",
    description="A gravitational n-body simulation package with features such as a barnes-hut tree, visualization tools, and CLI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/uzairn/nbody",
    #project_urls={
    #    "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    #},

    # license description and other stuff. 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],

    # required packages. I wouldn't list packages that come default to 
    # python standard library such as argparse. If they are managed via
    # pip then list them
    install_requires=[
        'numpy',
        'matplotlib'
    ],

    # command line hook setup also the way it is working 
    # here is the sourcefile "mainfile" (yours is currently main.py)
    # has a method named main(). It may work that you can just
    # delete the ":main" portion and your code runs smoothly. If not then
    # you will have to put your mainfile (excluding imports) inside of a main method 
    # -- you could then further modularize the creation of the argparser to a submethod
    # which may be nice. It might be necessary to add an if __name__ == "__main__" to the
    # bottom of the file as well -- I have never tested a different approach
    entry_points={
        'console_scripts': [
            'gravbody = gravbody.main:main'
        ]
    },

    packages=find_packages(),

    # this line may be useless if you don't have
    # package data inside src/nbody 
    # maybe documentation should go in there idk? It will only affect 
    # people who install your package via pip and not from source and 
    # don't reference the publically available source code which is linked above
    include_package_data = True,

    # may not be true for you but can't hurt
    python_requires=">=3.6",
)
