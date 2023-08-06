from setuptools import setup

with open("requirements.txt") as f:
    requires_list = [x.strip() for x in f.readlines()]

setup(
    name="fedai",
    version="0.2.6",
    description="Xeniro Federated Learning Tools",
    install_requires=requires_list,
    packages=["fedai", "fedai.utils"]
)
