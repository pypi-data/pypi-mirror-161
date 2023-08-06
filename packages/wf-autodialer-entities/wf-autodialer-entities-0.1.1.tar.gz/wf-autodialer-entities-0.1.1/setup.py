from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='wf-autodialer-entities',
    version='0.1.1',    
    description='Webforce autodialer entities',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Webforce',
    author_email='master@webforcehq.com',
    packages=['wf_autodialer_entities'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)