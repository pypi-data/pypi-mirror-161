from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="PubMedSucker",
    description="Pull all articles from PubMed and insert them into a Neo4j Graph Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.connect.dzd-ev.de/dzdtools/pubmedsucker",
    author="TB",
    author_email="tim.bleimehl@helmholtz-muenchen.de",
    license="MIT",
    packages=["pms"],
    install_requires=[
        "py2neo",
        "lxml",
        "xmltodict",
        "memoization",
        "graphio",
        "neobulkmp",
        "getversion",
        "dict2graph",
        "DZDConfigs",
        "FTPDownloader",
        "DZDutils",
        "requests",
        "py_expression_eval"
    ],
    python_requires=">=3.9",
    zip_safe=False,
    include_package_data=True,
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        # "local_scheme": "node-and-timestamp"
        "local_scheme": "no-local-version",
        "write_to": "version.py",
    },
    setup_requires=["setuptools_scm"],
)
