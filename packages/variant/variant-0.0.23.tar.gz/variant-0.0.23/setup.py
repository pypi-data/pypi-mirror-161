# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['variant']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'pyensembl>=2.0.0,<3.0.0', 'varcode']

entry_points = \
{'console_scripts': ['variant-effect = variant.effect:run']}

setup_kwargs = {
    'name': 'variant',
    'version': '0.0.23',
    'description': '',
    'long_description': '# Python pakcage for genomic variant analysis\n\n[![Pypi Releases](https://img.shields.io/pypi/v/variant.svg)](https://pypi.python.org/pypi/variant)\n[![Downloads](https://pepy.tech/badge/variant)](https://pepy.tech/project/variant)\n\n## `variant-effect` command can infer the effect of a mutation\n\n- `-i/--input` to sepecify the input file. The input file has 5 columns: `chromosome`, `position`, `strand`, `reference allele`, `alternative allele`.\n\n  - No header is required.\n  - The 3rd column (strand) is not used by default, just for compatibility with RNA mode.\n  - By default, the base of reference and alternative allele are based on DNA information\n  - For RNA mode (through `--rna` argument), the base of reference and alternative allele is reverse complement if the strand is negative(-).\n\n- `-o/--output` to specify the output file, leave empty for stdout.\n- `-r/--reference` to specify reference name, can be human / mouse / dog / cat / chicken ...\n- `-t/--type [DNA|RNA]` to run in DNA or RNA mode. If RNA is specified, the ref base will be complemented.\n- `--all-effects` output all effects of the variant.\n\n> demo:\n\nStore the following table in sites.tsv.\n\n```\nchr3    10301112        -       G       T\nchr7    94669540        +       G       N\nchr2    215361150       -       A       T\nchr15   72199549        -       G       T\nchr17   81843580        -       C       T\nchr2    84906537        +       C       T\nchr14   23645352        +       G       T\nchr20   37241351        +       G       T\nchrX    153651037       +       G       T\nchr17   81844010        -       A       T\n```\n\nRun command `variant-effect -i sites.tsv -r human -t RNA` to get the following output.\n\n```\n#chrom  pos     strand  ref     alt     mut_type        gene_name       transcript_id   transcript_pos  transcript_motif        coding_pos      codon_ref       aa_pos  aa_ref\nchr3    10301112        -       C       A       Silent  SEC13   ENST00000397117 1441    TTGATCATCTGCCTTAACGTG   849     CTG     284     L\nchr7    94669540        +       G       N       ThreePrimeUTR   PEG10   ENST00000612941 6240    TTTTACCCCTGTCAGTAGCCC   None    None    None    None\nchr2    215361150       -       T       A       ThreePrimeUTR   FN1     ENST00000323926 8012    GGCCCGCAATACTGTAGGAAC   None    None    None    None\nchr15   72199549        -       C       A       ThreePrimeUTR   PKM     ENST00000319622 2197    GCTGTAACGTGGCACTGGTAG   None    None    None    None\nchr17   81843580        -       G       A       ThreePrimeUTR   P4HB    ENST00000681020 3061    AGAAGCTTGTCCCCCGTGTGG   None    None    None    None\nchr2    84906537        +       C       T       ThreePrimeUTR   TMSB10  ENST00000233143 327     CCTGGGCACTCCGCGCCGATG   None    None    None    None\nchr14   23645352        +       G       T       ThreePrimeUTR   DHRS2   ENST00000344777 1391    CTGCCATTCTGCCAGACTAGC   None    None    None    None\nchr20   37241351        +       G       T       ThreePrimeUTR   RPN2    ENST00000237530 1959    AAAACTGAATGTCAAGAAAAG   None    None    None    None\nchrX    153651037       +       G       T       ThreePrimeUTR   DUSP9   ENST00000342782 2145    CTGCTACTTTGGGGGGTGGGG   None    None    None    None\nchr17   81844010        -       T       A       ThreePrimeUTR   P4HB    ENST00000681020 2631    GAACTGTAATACGCAAAGCCA   None    None    None    None\n```\n\nTODO:\n\n- support GRCh37\n',
    'author': 'Chang Ye',
    'author_email': 'yech1990@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yech1990/variant',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
