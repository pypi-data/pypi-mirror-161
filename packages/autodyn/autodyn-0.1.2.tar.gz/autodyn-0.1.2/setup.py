from setuptools import setup, find_packages

setup(
    name="autodyn",
    version="0.1.2",
    description="A module for differentiable dynamical systems",
    author="Vineet Tiruvadi",
    author_email="virati@gmail.com",
    package_dir={"": "src"},
    packages=[
        "autodyn",
        "autodyn.core",
        "autodyn.models",
        "autodyn.analysis",
        "autodyn.utils",
        "autodyn.viz",
    ],
    install_requires=["wheel"],  # external packages as dependencies
)
