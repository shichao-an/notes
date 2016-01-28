#!/usr/bin/env python

import os
import yaml

NO_INDEX = set(['PL', 'Others', 'Topics', 'Roadmap'])


def load_mkdocs():
    filename = 'mkdocs.yml'
    with open(filename) as f:
        return yaml.load(f.read())


def make_index(docs):
    groups = docs['pages']
    for group in groups:
        topic = group.keys()[0]
        _pages = group[topic]
        if topic not in NO_INDEX and isinstance(_pages, list):
            pages = []
            for _page in _pages:
                page = _page.items()[0]
                if 'index.md' not in page[1]:
                    path = page[1]
                    new_page = (page[0], path.split('/')[1])
                    pages.append(new_page)
            write_index(topic, pages)


def write_index(topic, pages):
    index = os.path.join('docs', topic.lower(), 'index.md')
    title = '### **%s**' % topic
    contents = '\n'.join(map(map_page, pages))
    document = '\n\n'.join([title, contents])
    with open(index, 'w') as f:
        f.write(document)


def map_page(page):
    """
    ('Chapter 1. Title', 'foo/ch1.md') => '[Chapter 1. Title](foo/ch1.md)'
    """
    return '* [%s](%s)' % (page[0], page[1])

docs = load_mkdocs()
make_index(docs)
