"""
setup file for python package
"""
import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="sourav_easyocr",
    version="0.3.4",
    author="Crossml",
    author_email="sourav@crossml.com",
    packages=setuptools.find_packages(),
    description="Input Adaptor to verify file extension",
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords=['Input-adaptor', 'Adaptor', 'DataAdaptor'],
    python_requires='>=3',
    install_requires=['easyocr', 'pdf2image','opencv-python==4.5.5.64']
)

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
