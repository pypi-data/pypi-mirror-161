import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="limeutils", # Replace with your own username
    version="0.2.11",
    author="dropickdev",
    author_email="enchance@gmail.com",
    description="Utility functions for python. Functions were made and tested in FastAPI but are "
                "suitable for any python project.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dropkickdev/limeutils.git",
    packages=setuptools.find_packages(),
    install_requires=['redis', 'pydantic'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)