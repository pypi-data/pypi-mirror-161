# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uniprotparser']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'uniprotparser',
    'version': '1.0.5',
    'description': 'Getting Uniprot Data from Uniprot Accession ID through Uniprot REST API',
    'long_description': 'UniProt Database Web Parser Project\n--\n\nTLDR: This parser can be used to parse UniProt accession id and obtain related data from the UniProt web database.\n\nWith version 1.0.5, support for asyncio through `aiohttp` has been added to `betaparser`. Usage can be seen as follow\n\n```python\nfrom uniprotparser.betaparser import UniprotParser\nfrom io import StringIO\nimport asyncio\nimport pandas as pd\n\nasync def main():\n    example_acc_list = ["Q99490", "Q8NEJ0", "Q13322", "P05019", "P35568", "Q15323"]\n    parser = UniprotParser()\n    df = []\n    #Yield result for 500 accession ids at a time\n    async for r in parser.parse_async(ids=example_acc_list):\n        df.append(pd.read_csv(StringIO(r), sep="\\t"))\n    \n    #Check if there were more than one result and consolidate them into one dataframe\n    if len(df) > 0:\n        df = pd.concat(df, ignore_index=True)\n    else:\n        df = df[0]\n\nasyncio.run(main())\n```\n\nWith version 1.0.2, support for the new UniProt REST API have been added under `betaparser` module of the package.\n\nIn order to utilize this new module, you can follow the example bellow\n\n```python\nfrom uniprotparser.betaparser import UniprotParser\nfrom io import StringIO\n\nimport pandas as pd\nexample_acc_list = ["Q99490", "Q8NEJ0", "Q13322", "P05019", "P35568", "Q15323"]\nparser = UniprotParser()\ndf = []\n#Yield result for 500 accession ids at a time\nfor r in parser.parse(ids=example_acc_list):\n    df.append(pd.read_csv(StringIO(r), sep="\\t"))\n\n#Check if there were more than one result and consolidate them into one dataframe\nif len(df) > 0:\n    df = pd.concat(df, ignore_index=True)\nelse:\n    df = df[0]\n\n\n```\n\n---\nTo parse UniProt accession with legacy API\n\n```python\nfrom uniprotparser.parser import UniprotSequence\n\nprotein_id = "seq|P06493|swiss"\n\nacc_id = UniprotSequence(protein_id, parse_acc=True)\n\n#Access ACCID\nacc_id.accession\n\n#Access isoform id\nacc_id.isoform\n```\n\nTo get additional data from UniProt online database\n\n```python\nfrom uniprotparser.parser import UniprotParser\nfrom io import StringIO\n#Install pandas first to handle tabulated data\nimport pandas as pd\n\nprotein_accession = "P06493"\n\nparser = UniprotParser([protein_accession])\n\n#To get tabulated data\nresult = []\nfor i in parser.parse("tab"):\n    tab_data = pd.read_csv(i, sep="\\t")\n    last_column_name = tab_data.columns[-1]\n    tab_data.rename(columns={last_column_name: "query"}, inplace=True)\n    result.append(tab_data)\nfin = pd.concat(result, ignore_index=True)\n\n#To get fasta sequence\nwith open("fasta_output.fasta", "wt") as fasta_output:\n    for i in parser.parse():\n        fasta_output.write(i)\n```\n\n',
    'author': 'Toan K. Phung',
    'author_email': 'toan.phungkhoiquoctoan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/noatgnu/UniprotWebParser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
