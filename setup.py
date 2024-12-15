from setuptools import setup, find_packages

setup(
    name="guardrails",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "pyyaml",
        "openai==0.28.1",
        "httpx",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ]
    }
) 