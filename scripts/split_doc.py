import logging
import re
import sys
from pathlib import Path
from dataclass import dataclass

import unicodedata
import re

"""
Spliting SEPARATOR-separated documentation into multiple files into `docs/`, each with filename as `{page_index}.{first_line}.txt`.
"""

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def _find_first_non_empty(lines):
    for line in lines:
        if line.strip() == '':
            continue

        return line

def split_doc(filename):
    SEPARATOR = '==============================================================================\n'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    with open(filename, 'r') as f:
        content = f.read()

        splitted_docs = re.split(SEPARATOR, content)

        if len(splitted_docs) > 0:
            path = Path('docs')
            if not path.exists():
                path.mkdir()

        for idx, doc in enumerate(splitted_docs):
            filename = slugify(_find_first_non_empty(doc.split('\n')))
            filepath = f'docs/{idx}.{filename}.txt'
            #logger.info(f'saving section to {filepath}...')
            print(_find_first_non_empty(doc.split('\n')))
            with open(filepath, 'w+') as doc_file:
                doc_file.write(doc)
    return splitted_docs
        
if __name__ == '__main__':
    filename = sys.argv[1]
    split_doc(filename)
