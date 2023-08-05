import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding='utf8') as fh:
    requires = fh.read().replace('==', '>=')

setuptools.setup(
    name="auth-util",
    version="0.0.9",
    author="Steven Wang",
    author_email="brightstar8284@icloud.com",
    description="Password and jwt manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StevenLianaL/auth-util",
    packages=setuptools.find_packages(exclude=["tests*"]),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
