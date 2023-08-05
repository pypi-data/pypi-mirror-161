import setuptools
with open(r'README.md', 'r', encoding='utf-8') as f:
	long_description = f.read()

setuptools.setup(
	name='easy_stopwatch',
	version='1.0.2',
	author='Dolenko10.0Artem10.0',
	author_email='artemdolenko.ua@gmail.com',
	description='The easy stopwatch that is the best',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['easy_stopwatch'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)
