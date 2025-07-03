from setuptools import setup, find_packages

with open("requirements.in") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="operato_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=install_requires,
) 