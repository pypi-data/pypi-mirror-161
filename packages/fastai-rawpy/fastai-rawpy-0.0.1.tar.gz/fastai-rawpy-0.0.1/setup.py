from setuptools import setup

setup(
    name='fastai-rawpy', # this is the name people would look up to find this package
    version='0.0.1',
    description='Connecting fastai with RawPy',
    py_modules=['fastairawpy'], # This should match the name of the module.py file
    install_requires=["fastai","rawpy"],
    #extras_require={"dev":"pytest>=3.7"},
    url="https://github.com/lejrn/Fastai-RawPy",
    author="Tal Leron",
    author_mail="lrn.tl.dv@gmail.com",
    package_dir={'':'src'}
)