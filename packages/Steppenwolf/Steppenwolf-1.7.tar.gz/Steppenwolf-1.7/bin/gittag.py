#!/usr/bin/env python3

import os, re, sys, json, subprocess

result = subprocess.Popen(['git','tag'], stdout=subprocess.PIPE)

class Tags:

	def __init__(self, value=''):
		self.value = value
		self.children = list()

	def bury(self, tag, indent=''):
		parts = tag.split('.')
		value = int(parts[0])
		
		child = None
		for _child in self.children:
			if _child.value == value:
				child = _child
				#print(f'{indent}={child.value}')
				break
		if not child:
			child = Tags(value=value)
			#print(f'{indent}+{child.value}')
			self.children.append(child)

		if len(parts) > 1:
			remainder = '.'.join(parts[1:])
			child.bury(remainder, indent=f'\t{indent}')
		
	def dig(self, prefix=''):
		if len(self.children) == 0:
			print(f'{prefix}{self.value}'.lstrip('.'))
		for child in sorted(self.children, key=lambda x: x.value):
			child.dig(prefix=f'{prefix}{self.value}.')

		
tags = Tags()

for tag in result.stdout.readlines():
	tag = tag.decode('UTF8').rstrip('\n')
	tags.bury(tag)


tags.dig()
