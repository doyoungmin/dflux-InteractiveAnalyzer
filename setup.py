"""
dflux_InteractiveAnalyzer - 설치 스크립트
"""

from setuptools import setup, find_packages
from pathlib import Path

# README 읽기
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# 요구사항 읽기
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding='utf-8').strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="dflux-interactive-analyzer",
    version="2.0.0",
    author="Touch Data Analyzer Team",
    author_email="",
    description="dflux_InteractiveAnalyzer - 데이터 시각화 및 분석 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "monitoring": [
            "psutil>=5.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "dflux-analyzer=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "touch_analyzer": [
            "config/*.py",
            "docs/*.md",
        ],
    },
    zip_safe=False,
)
