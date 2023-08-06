from setuptools import setup

with open("requirements.txt") as installation_requirements_file:
    requirements = installation_requirements_file.read().splitlines()

setup(
    name="easypubsub",
    version="0.1.0",
    packages=["easypubsub"],
    url="https://github.com/matpompili/easypubsub",
    author="Matteo Pompili",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="TODO",
    install_requires=requirements,
    test_suite="tests",
    package_data={"": ["LICENSE"]},
)
