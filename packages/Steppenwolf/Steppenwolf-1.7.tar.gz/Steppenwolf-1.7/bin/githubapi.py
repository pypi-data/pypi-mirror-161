#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys

from github import Github

from Argumental.Argue import Argue
from Spanners.Squirrel import Squirrel

args=Argue()
squirrel=Squirrel()

@args.command(single=True)
class GitHubAPI(object):

	@args.property(default='github.com')
	def hostname(self): return

	@args.property(default='pypi')
	def tokename(self): return

	def __init__(self):
		token=squirrel.get('%s:%s'%(self.hostname, self.tokename))
		self.github = Github(token)

		
	@args.operation
	def list(self):
		for repo in self.github.get_user().get_repos():  
			print(repo.full_name)

			
	@args.operation
	@args.parameter(name='new_tag', short='t', help='tag label')
	@args.parameter(name='repo_name', short='r', help='select repository')
	@args.parameter(name='tag_message', short='m', help='tag message')
	def release(self, new_tag=None, repo_name=None, tag_message=None):
		if not new_tag:
			pattern = re.compile('^version\s*=\s*[\'\"]([0-9\.]*)[\'\"].*$')
			with open('setup.py') as input:
				for line in input.readlines():
					match = pattern.match(line)
					if match:
						new_tag = match.group(1)
						break
		print('requested tag = %s'%new_tag)

		repo_name = repo_name or os.path.basename(os.getcwd())
		print('requested repo = %s'%repo_name)
		
		repo = self.github.get_user().get_repo(repo_name)
		print('repository found = %s'%repo.name)

		found = None
		for tag in repo.get_tags():
			if tag.name == new_tag:
				found = tag
				break

		if found:
			tag = found
			print('existing tag = %s'%tag.name)
			sha = tag.commit.sha
		else:
			head = repo.get_commits()[0]
			print('using commit sha = %s'%head.sha)
			  
			tag = repo.create_git_tag(new_tag, tag_message or new_tag, head.sha, 'commit')
			print('created tag = %s'%tag.tag)
			sha = tag.sha
                        
			ref = repo.create_git_ref('refs/tags/%s'%tag.tag, tag.sha)

		release = repo.create_git_release(new_tag, new_tag, tag_message or new_tag,)
		print('release created = %s'%release.title)


if __name__ == '__main__': args.execute()



	
