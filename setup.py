from setuptools import setup, find_packages

setup(
    name="bumpers",
    version="0.1.4",
    description="Safety/alignment guardrails for AI agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Omar Abul-Hassan",
    author_email="omarah@stanford.edu",
    url="https://github.com/pythonomar22/bumpers",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pyyaml",
        "httpx",
        "langchain",
        "sentence-transformers",
        "cerebras-cloud-sdk",
        "torch",
        "openai>=1.0.0",
        "google-generativeai",
        "Pillow"
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 