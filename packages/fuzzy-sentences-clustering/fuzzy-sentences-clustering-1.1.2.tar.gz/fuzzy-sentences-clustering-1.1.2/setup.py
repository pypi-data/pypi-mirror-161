# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fuzzy_sentences_clustering']

package_data = \
{'': ['*']}

install_requires = \
['fuzzywuzzy==0.18.0', 'nltk==3.7', 'python-Levenshtein-wheels==0.13.2']

setup_kwargs = {
    'name': 'fuzzy-sentences-clustering',
    'version': '1.1.2',
    'description': 'Clustering similar sentences based on their fuzzy similarity.',
    'long_description': 'fuzzy-sentences-clustering\n==========================\n\nClustering similar sentences based on their fuzzy similarity.\n\nFor the word stem extractor I am using `Snowball\nstemmers <https://www.nltk.org/api/nltk.stem.snowball.html#:~:text=The%20following%20languages%20are%20supported,%2C%20Russian%2C%20Spanish%20and%20Swedish.>`__\nfrom NLTK library. So the following languages are supported:\n\n-  Arabic\n-  Danish\n-  Dutch\n-  English\n-  Finnish\n-  French\n-  German\n-  Hungarian\n-  Italian\n-  Norwegian\n-  Portuguese\n-  Romanian\n-  Russian\n-  Spanish\n-  Swedish\n\nPurpose of the Package\n----------------------\n\nThere are some popular algorithms on the market for mining topics in a\ntextual set, such as\n`LDA <https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation>`__, but\nthey don’t work very well for a small set of data, let’s say a thousand\nsentences for example.\n\nThis package tries to solve this for a small dataset by making the\nfollowing naive assumption:\n\n   *If I remove all the stopwords, get the stems from words and after\n   that these sentences become similar, they are probably talking about\n   the same, or similar, subject.*\n\nThe goal here is to form clusters/groups with at least two similar\nsentences, isolated sentences (sentences that don’t look like any other\nin the total set) will not generate a cluster just for them. For these\ncases, the sentence will receive the *-1* tag.\n\nUsage\n-----\n\nYou can choose more than one method to compare the similarity between\nsentences:\n\n-  ratio\n-  partial_ratio\n-  token_sort_ratio (the default one)\n-  token_set_ratio\n\nTo know more about these methods click\n`here <https://pypi.org/project/fuzzywuzzy/>`__.\n\n.. code:: python\n\n   >>> from fuzzy_sentences_clustering import look_for_clusters\n   >>> eng_sentences = [\n           "I live in New York",\n           "I want to buy a car",\n           "a car I would like to buy",\n           "Ohh New York, I lived there in 2005",\n           "I have a dog",\n       ]\n   >>> ger_sentences = [\n           "ich lebe in New York",\n           "Ich möchte ein Auto kaufen",\n           "ein Auto, das ich kaufen möchte",\n           "Oh New York, Ich habe dort 2005 gelebt",\n           "Ich habe einen Hund",\n       ]\n   >>> look_for_clusters(eng_sentences, similarity_threshold=60)\n   output: [1, 2, 2, 1, -1]\n   >>> look_for_clusters(ger_sentences, language="german", method="token_set_ratio", similarity_threshold=80)\n   output: [1, 2, 2, 1, -1]\n\nContribution\n------------\n\nContributions are welcome.\n\nIf you find a bug, please let me know.\n\nAuthor\n------\n\n`Cloves Paiva <https://www.linkedin.com/in/cloves-paiva-02b449124/>`__.\n',
    'author': 'Cloves Paiva',
    'author_email': 'clovesgtx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SClovesgtx/fuzzy-sentences-clustering',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
