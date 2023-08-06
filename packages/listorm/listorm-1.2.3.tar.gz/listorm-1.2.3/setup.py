from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
	name='listorm',
	version='1.2.3',
	license='MIT',
	description='list orm methods and shortcuts for table type of dict-list',
	long_description=long_description,
	long_description_content_type="text/markdown",
	author = 'HS Moon',
	author_email = 'pbr112@naver.com',
	py_modules = ['listorm'],
	keywords=['listorm', 'list of dict', 'dict list', 'records', 'sql', 'orm'],
	url='https://github.com/zwolf21/listorm',
	packages=find_packages(exclude=['docs', 'test', 'test.*']),
	install_requires=['openpyxl'],
	classifiers=[
		'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
	python_requires=">=3.8"
)
