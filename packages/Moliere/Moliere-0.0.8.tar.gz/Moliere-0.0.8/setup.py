import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    author="Peter Menshih",
    author_email="p.menshih@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    description="Psycopg wrapper",
    install_requires=[
        'psycopg2-binary',
        'python-dotenv'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="Moliere",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    url="https://gitlab.com/pmenshih/moliere",
    version="0.0.8",
)