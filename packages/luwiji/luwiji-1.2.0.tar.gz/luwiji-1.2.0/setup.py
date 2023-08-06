from setuptools import setup, find_packages
import luwiji

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="luwiji",
    version=luwiji.__version__,
    author="Wira Dharma Kencana Putra",
    author_email="wiradharma_kencanaputra@yahoo.com",
    description="LuWiji is a package full of machine learning illustrations and widgets",
    long_description=description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6.7",
    install_requires=['numpy', 'scipy', 'pandas', 'scikit-learn', 'matplotlib', 'ipywidgets', 'jcopml', 'pillow', 'networkx'],
    include_package_data=True,
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
    license='BSD',
    keywords="machine learning ml widget luwiji indonesia",
    url="https://github.com/WiraDKP/luwiji"
)