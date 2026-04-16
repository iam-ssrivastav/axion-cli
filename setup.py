"""Setup file for backward compatibility with older pip versions."""
from setuptools import setup, find_packages

setup(
    name="axion-cli",
    version="0.1.0",
    description="Free, open-source AI coding assistant for your terminal",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.30.0",
        "google-generativeai>=0.7.0",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.43",
        "click>=8.1.7",
        "pyyaml>=6.0.1",
        "httpx>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "axion=axion.__main__:main",
        ],
    },
)
