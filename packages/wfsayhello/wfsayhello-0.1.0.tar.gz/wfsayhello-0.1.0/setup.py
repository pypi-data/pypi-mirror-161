from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='wfsayhello',
    version='0.1.0',    
    description='Webforce say hello package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Webforce',
    author_email='ehoy@webforcehq.com',
    packages=['wfsayhello'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)