from setuptools import setup
import os

def package_files(directory):
	paths = []
	for path, directories, file_names in os.walk(directory):
		for filename in file_names:
			paths.append(os.path.join('..', path, filename))
	return paths

extra_files = package_files('throneloon')

setup(
	name = 'throneloon',
	version = '1.0',
	packages = ['throneloon'],
	package_data = {'': extra_files},
	dependency_links = [
		'https://github.com/guldfisk/eventdispatch/tarball/master#egg=eventdispatch-1.0',
		'https://github.com/guldfisk/eventtree/tarball/master#egg=eventtree-1.0',
		'https://github.com/guldfisk/ring/tarball/master#egg=ring-1.0',
	],
	install_requires = [
		'frozendict',
		'weakreflist',
		'ordered_set',
		'eventdispatch',
		'eventtree',
		'ring',
	]
)