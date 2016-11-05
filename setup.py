#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

import io
import re
import sys

from os.path import join, dirname

from setuptools import setup, find_packages


ROOT = dirname(__file__)

RE_REQUIREMENT = re.compile(r'^\s*-r\s*(?P<filename>.*)$')

RE_MD_CODE_BLOCK = re.compile(r'```(?P<language>[\w+]+)?\n(?P<lines>.*?)```', re.S)
RE_SELF_LINK = re.compile(r'\[([^[\]]*?)\]\[\]')
RE_LINK_TO_URL = re.compile(r'\[(?P<text>.*?)\]\((?P<url>.*?)\)')
RE_LINK_TO_REF = re.compile(r'\[(?P<text>.*?)\]\[(?P<ref>.*?)\]')
RE_LINK_REF = re.compile(r'^\[(?P<key>[^!].*?)\]:\s*(?P<url>.*?)$', re.M)
RE_BADGE = re.compile(r'^\[\!\[(?P<text>.*?)\]\[(?P<badge>.*?)\]\]\[(?P<target>.*?)\]$', re.M)
RE_TITLE = re.compile(r'^(?P<level>#+)\s*(?P<title>.*)$', re.M)
RE_IMAGE = re.compile(r'\!\[(?P<text>.*?)\]\((?P<url>.*?)\)')
RE_CODE = re.compile(r'``([^<>]*?)``')

GITHUB_REPOSITORY = 'https://github.com/apihackers/wagtail-sendinblue'

BADGES_TO_KEEP = ['gitter-badge']

RST_TITLE_LEVELS = ['=', '-', '*']

RST_BADGE = '''\
.. image:: {badge}
    :target: {target}
    :alt: {text}
'''

def md2pypi(filename):
    '''
    Load .md (markdown) file and sanitize it for PyPI.
    Remove unsupported github tags:
     - code-block directive
     - travis ci build badges
    '''
    content = io.open(filename).read()

    for match in RE_MD_CODE_BLOCK.finditer(content):
        rst_block = '\n'.join(
            ['.. code-block:: {language}'.format(**match.groupdict()), ''] +
            ['    {0}'.format(l) for l in match.group('lines').split('\n')] +
            ['']
        )
        content = content.replace(match.group(0), rst_block)

    refs = dict(RE_LINK_REF.findall(content))
    content = RE_LINK_REF.sub('.. _\g<key>: \g<url>', content)
    content = RE_SELF_LINK.sub('`\g<1>`_', content)
    content = RE_LINK_TO_URL.sub('`\g<text> <\g<url>>`_', content)

    for match in RE_BADGE.finditer(content):
        if match.group('badge') not in BADGES_TO_KEEP:
            content = content.replace(match.group(0), '')
        else:
            params = match.groupdict()
            params['badge'] = refs[match.group('badge')]
            params['target'] = refs[match.group('target')]
            content = content.replace(match.group(0),
                                      RST_BADGE.format(**params))

    for match in RE_IMAGE.finditer(content):
        url = match.group('url')
        if not url.startswith('http'):
            url = '/'.join((GITHUB_REPOSITORY, 'raw/master', url))

        rst_block = '\n'.join([
            '.. image:: {0}'.format(url),
            '  :alt: {0}'.format(match.group('text'))
        ])
        content = content.replace(match.group(0), rst_block)

    # Must occur after badges
    for match in RE_LINK_TO_REF.finditer(content):
        content = content.replace(match.group(0), '`{text} <{url}>`_'.format(
            text=match.group('text'),
            url=refs[match.group('ref')]
        ))

    for match in RE_TITLE.finditer(content):
        underchar = RST_TITLE_LEVELS[len(match.group('level'))]
        title = match.group('title')
        underline = underchar * len(title)

        full_title = '\n'.join((title, underline))
        content = content.replace(match.group(0), full_title)

    content = RE_CODE.sub('``\g<1>``', content)

    return content


long_description = '\n'.join((
    md2pypi('README.md'),
    # md2pypi('CHANGELOG.md'),
    ''
))


exec(compile(open('sendinblue/__about__.py').read(), 'sendinblue/__about__.py', 'exec'))


setup(
    name='wagtail-sendinblue',
    version=__version__,
    description=__description__,
    long_description=long_description,
    url='https://github.com/apihackers/wagtail-sendinblue',
    author='API Hackers',
    author_email='wagtail-sendinblue@apihackers.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests'],
    tests_require=[],
    extras_require={
        'test': [],
        'doc': [],
        # 'dev': pip('develop'),
    },
    license='MIT',
    zip_safe=False,
    keywords='wagtail sendinblue',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)
