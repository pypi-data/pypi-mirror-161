from setuptools import setup, find_namespace_packages
from optimeed import VERSION
with open("README.md", "r") as fh:
    long_description = fh.read()

extras = {
    'with_matplotlib': ['matplotlib'],  # Hold CTRL to select multiple points on graphs
    'with_pandas': ['pandas'],  # Export XLS the collection
    'with_plotly': ['plotly']  # 3D plots
}

setup(
    name="optimeed",
    version="{}".format(VERSION),
    author="Christophe De Greef",
    author_email="christophe.degreef@uclouvain.be",
    description="Powerful optimization and vizualisation tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.immc.ucl.ac.be/chdegreef/optimeed",
    packages=find_namespace_packages(include=['optimeed.*']),
    include_package_data=True,
    install_requires=['numpy', 'PyOpenGL', 'PyQt5', 'pytypes', 'SALib'],
    extras_require=extras,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering"
    ],
    python_requires='>=3.6',
)
