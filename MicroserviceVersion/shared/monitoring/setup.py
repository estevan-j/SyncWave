from setuptools import setup, find_packages

setup(
    name="microservice-monitoring",
    version="1.0.0",
    description="Shared monitoring utilities for Flask microservices",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "prometheus-client>=0.17.0",
        "psutil>=5.9.0",  # Para métricas del sistema
    ],
    python_requires=">=3.8",
    author="Bug Hunters",
    author_email="bug.hunters@example.com",
)