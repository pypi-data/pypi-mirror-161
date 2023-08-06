import setuptools
with open(r'README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='small_timer',
	version='1.0.9',
	author='Dolenko10.0Artem10.0',
	author_email='artemdolenko.ua@gmail.com',
	description='A miniature timer that does the same thing as a regular timer',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['small_timer'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)
