import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

    setuptools.setup(
        name='fiser_tools',
        version='0.33',
        author="fiser",
        author_email="sergi.garcia.munoz@gmail.com",
        description="Personal DS tools",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/f1se4/fiser_tools",
        packages=['fiser_tools'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        license='MIT',
        install_requires=['pandas', 'matplotlib','seaborn'],
    )
