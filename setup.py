from setuptools import setup, find_packages

setup(
    name="vault-of-memories",
    version="0.1.0",
    description="Digital vault pre-processor for preserving family memories",
    author="Vault of Memories Project",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        # Standard library only - following Dependency Minimalism principle
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "vault-ingest=cli.ingest_command:main",
        ],
    },
)