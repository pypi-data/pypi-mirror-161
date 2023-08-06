from setuptools import setup

with open("requirements.txt") as installation_requirements_file:
    requirements = installation_requirements_file.read().splitlines()

with open("requirements-dev.txt") as test_requirements_file:
    test_requirements = test_requirements_file.read().splitlines()

with open("README.md") as readme_file:
    readme = readme_file.read()

project_urls = {
    "Home": "https://github.com/matpompili/easypubsub",
    "Documentation": "https://easypubsub.readthedocs.io/",
    "Changelog": "https://github.com/matpompili/easypubsub/blob/main/CHANGELOG.md",
}

setup(
    name="easypubsub",
    version="0.3.1",
    packages=["easypubsub"],
    author="Matteo Pompili",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="A simple wrapper around PyZMQ that provides an easy interface to Publish Subscribe.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    test_suite="tests",
    tests_require=test_requirements,
    package_data={
        "": ["LICENSE"],
        "easypubsub": ["py.typed"],
    },
    project_urls=project_urls,
)
