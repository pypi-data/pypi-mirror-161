import setuptools

setuptools.setup(
    name='anews',
    version='1.30',
    author="Thanh Hoa",
    author_email="getmoneykhmt3@gmail.com",
    description="A Des of anews",
    long_description="anews",
    long_description_content_type="text/markdown",
    url="https://github.com/vtandroid/anews",
    packages=setuptools.find_packages(),
    py_modules=['anews'],
    install_requires=[
        'pillow','requests','gbak','w3lib','python-slugify'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )