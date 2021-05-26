from setuptools import setup

requires = [
    "pulp",
    "black",
]


setup(
    name="sudoku-solver",
    version="0.0.0",
    description="Sudoku Solver",
    author="LRossdeutscher",
    author_email="lucas.rossdeutscher@gmail.com",
    url="",
    packages="sudoku_solver",
    include_package_data=True,
    install_requires=requires,
)
