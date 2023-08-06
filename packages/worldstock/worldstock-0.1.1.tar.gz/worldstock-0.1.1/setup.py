## setup.py
import io
from setuptools import find_packages, setup

setup(
    name="worldstock",
    version="0.1.1",
    url = "http://github.com/2ky1234",
    license="MIT",
    author = "LEE GUNYOUNG",
    author_email= "2ky1234@khu.ac.kr",
    description = 'Download world stock list and Make short company name using full name',
    keywords = ['stock', 'data-analysis', 'company-info'],
    packages=find_packages(),
    include_package_data=True,
    python_requires = '>=3.9',
    classifiers=[
            "Programming Language :: Python :: 3",
        ],
    install_requires=["bs4","yfinance"],
)