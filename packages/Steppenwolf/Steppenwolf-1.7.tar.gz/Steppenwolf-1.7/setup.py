#!/usr/bin/env python3

import os, codecs
from os import path
from setuptools import setup

pwd = path.abspath(path.dirname(__file__))
with codecs.open(path.join(pwd, 'README.md'), 'r', encoding='utf8') as input:
	long_description = input.read()

name='Steppenwolf'
user='eddo888'
version='1.7'

setup(
	name=name,
	version=version,
	license='MIT',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://github.com/%s/%s'%(user,name),
	download_url='https://github.com/%s/%s/archive/%s.tar.gz'%(user, name, version),
	author='David Edson',
	author_email='eddo888@tpg.com.au',
	packages=[name],
	install_requires=[
		'twine',
		'PyGithub',
		'Baubles',
		'Perdy',
		'Argumental',
		'Spanners',
	],
	scripts=[
		"bin/githubapi.py",
		"bin/pypi.sh",
		"bin/gitrevert.sh",
		"bin/gitadd.sh",
		"bin/gitpush.sh",
		"bin/gitinit.sh",
		"bin/gitmove.sh",
		"bin/gitdiff.sh",
		"bin/gitorigin.sh",
		"bin/gitkey.sh",
		"bin/githubinit.sh",
		"bin/gitstatus.sh",
		"bin/gitmerge.sh",
		"bin/githubget.sh",
		"bin/gitupload.sh",
		"bin/gitpull.sh",
		"bin/gitget.sh",
		"bin/gitlist.sh",
		"bin/gitremove.sh",
		"bin/githubflow.sh",
		"bin/gitbranch.sh",
		"bin/gitcommit.sh",
		"bin/gittag.py",
		"bin/gittime.sh",
		"bin/gittree.sh",
	], 
)

