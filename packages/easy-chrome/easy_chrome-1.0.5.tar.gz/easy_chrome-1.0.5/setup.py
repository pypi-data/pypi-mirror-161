import setuptools

setuptools.setup(
    name="easy_chrome",
    version="1.0.5",
    author="VanCuong",
    author_email="vuvancuong94@gmail.com",
    description="Easy selenium chrome for window",
    long_description="Easy selenium chrome for windows",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
       'selenium',
       'requests'
    ],
    python_requires=">=3.7",
)
