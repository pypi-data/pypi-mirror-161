def get_versions():
    return versions[0]["number"]


versions = [
    {
        "number": "0.0.8",
        "features": [
            "1. Add ftp function",
            "2. Simplifies the process of loading gff into sqlite",
        ],
    },
    {
        "number": "0.0.7",
        "features": [
            "1. Separate SeqParser from ToolBiox",
        ],
    },
    {
        "number": "0.0.6",
        "features": [
            "1. bug fixed",
        ],
    },
    {
        "number": "0.0.5",
        "features": [
            "1. bug fixed",
        ],
    },
    {
        "number": "0.0.4",
        "features": [
            "1. Separate TaxonTools from ToolBiox",
            "2. Add some package in setup.py",
        ],
    },
    {
        "number": "0.0.3",
        "features": [
            "1. Organized all import code",
            "2. Add function for get common tree by 1kp",
        ],
    },
    {
        "number": "0.0.2.1",
        "features": [
            "1. Get rid of the dependency on scikit-bio",
            "2. Reformat TaxonTools.py",
        ],
    },
    {
        "number": "0.0.2",
        "features": [
            "1. Get rid of the dependency on scikit-bio",
        ],
    },
    {
        "number": "0.0.1",
        "features": [
            "1. Separate the tools, libraries and api parts from the original Genome_work_tools and become ToolBiox",
        ],
    },
]