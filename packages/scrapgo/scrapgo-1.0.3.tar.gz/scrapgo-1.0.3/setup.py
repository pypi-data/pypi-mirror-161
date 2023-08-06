from setuptools import setup, find_packages



setup(
	name='scrapgo',
	version='1.0.3',
	license='MIT',
	description='Convenient crawling framework using as wrapper of reqeusts, requests-cache, beautifulsoup, etc.',
	author = 'HS Moon',
	author_email = 'pbr112@naver.com',
	keywords=['scrapgo', 'crawling', 'scrapping', 'scrap', 'web'],
	url='https://github.com/zwolf21/scrapgo',
	packages=find_packages(exclude=['test', 'test.*']),
	install_requires=[
        'requests', 'requests-cache', 'bs4',
        'requests-file', 'fake-useragent',
        'python-dateutil'
    ],
	classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'Topic :: Communications :: Email',
    ],
	python_requires=">=3.8"
)