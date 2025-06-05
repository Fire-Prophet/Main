from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fire-map-visualizer",
    version="1.0.0",
    author="Fire Simulation Team",
    author_email="developer@example.com",
    description="화재 시뮬레이션 결과를 지도 위에 시각화하는 Python 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/fire-map-visualizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
        ],
        "enhanced": [
            "contextily>=1.2.0",
            "rasterio>=1.2.0",
            "xarray>=0.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fire-visualizer=visualize.fire_map_visualizer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "visualize": ["*.json", "*.yaml", "*.yml"],
    },
    keywords="fire simulation visualization gis mapping folium streamlit",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/fire-map-visualizer/issues",
        "Source": "https://github.com/your-repo/fire-map-visualizer",
        "Documentation": "https://fire-map-visualizer.readthedocs.io/",
    },
)
