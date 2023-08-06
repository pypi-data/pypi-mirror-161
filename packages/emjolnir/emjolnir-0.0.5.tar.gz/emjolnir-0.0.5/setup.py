import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="emjolnir", # Replace with your own username
    version="0.0.5",
    author="pyotel",
    author_email="pyotel@gmail.com",
    description="A small example package",
    long_description="long_description",
    long_description_content_type="text/markdown",
    url="https://github.com/pyotel/emjolnir",
    packages=['emjolnir'],
    scripts=['emjolnir/wt_field.dat'],
#    package_data = {'': ['emjolnir/wt_field.dat']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)