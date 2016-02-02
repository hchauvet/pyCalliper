from distutils.core import setup
#from setuptools import setup #too create .egg

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["icons/*"]

setup(name = "pyCalliper",
    version = "0.1.1",
    description = "Image processing for grain size image",
    author = "CHAUVET Hugo",
    author_email = "chauvet@ipgp.fr",
    url = "https://morpho.ipgp.fr/OSS",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages = ['LibPyCalliper'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'LibPyCalliper' : files },
    #'runner' is in the root.
    scripts = ["pyCalliper"],
    #long_description = """Really long text here."""
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []
    license='GPL',
    install_requires=[
        'setuptools',
        'matplotlib',
        'numpy',
        'scipy',
        'scikits-image',
    ],
)

