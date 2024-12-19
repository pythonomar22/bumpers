from setuptools import setup, find_packages

setup(
    name="bumpers",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "pyyaml",
        "httpx",
        "sentence-transformers",
        "cerebras-cloud-sdk",
        "torch",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ]
    }
) 