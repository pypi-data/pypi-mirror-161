from setuptools import setup, find_packages

setup(
    # name of package
    name='datadb',

    version='0.0.6',
    description='tool to assess data',



    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows"
    ],

    install_requires=[
        "pandas",
        "bokeh",
        "notebook",
        "scikit-learn"
    ],

    packages = find_packages(),

    license='MIT',

    author='Rens Jochemsen',
    author_email='rensjochemsen@gmail.com'
)
