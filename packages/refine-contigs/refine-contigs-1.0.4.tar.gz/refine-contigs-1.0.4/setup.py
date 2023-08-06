from setuptools import setup
import versioneer

requirements = [
    "pandas<=1.2.0",
    "scipy>=1.5.2",
    "networkx>=2.5",
    "tqdm==4.50.0",
    "PyYAML>=5.4",
    "biopython>=1.77",
    "pyfaidx>=0.5.9",
    "pyranges==0.0.110",
    "ncls==0.0.62",
    "datatable>=1.0.0",
]

setup(
    setup_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        "setuptools>=18.0",
        "Cython>=0.29.21",
    ],
    scripts=["scripts/minimus2_mod"],
    name="refine-contigs",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A simple tool to identify and clean misassemblies for ancient metagenomics",
    license="GNUv3",
    author="Antonio Fernandez-Guerra",
    author_email="antonio@metagenomics.eu",
    url="https://github.com/genomewalker/refine-contigs",
    packages=["refine_contigs"],
    entry_points={"console_scripts": ["refineC=refine_contigs.__main__:main"]},
    install_requires=requirements,
    keywords="refine-contigs",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
