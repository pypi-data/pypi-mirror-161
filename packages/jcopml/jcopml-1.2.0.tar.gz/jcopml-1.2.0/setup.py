from setuptools import setup, find_packages
import jcopml

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="jcopml",
    version=jcopml.__version__,
    author="Wira Dharma Kencana Putra",
    author_email="wiradharma_kencanaputra@yahoo.com",
    description="J.COp ML is a machine Learning package to complement scikit-learn workflow",
    long_description=description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6.6",
    install_requires=['numpy', 'scipy', 'pandas', 'scikit-learn', 'matplotlib',
                      'seaborn', 'scikit-optimize', 'ipywidgets', 'statsmodels'],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Natural Language :: Indonesian",
        "Natural Language :: English"
    ],
    keywords="machine learning ml jcop indonesia",
    url="https://github.com/WiraDKP/jcopml"
)
