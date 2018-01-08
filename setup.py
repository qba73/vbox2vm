from setuptools import setup, find_packages


setup(
    name='ovf',
    version='0.1.0',
    url="https://github.com/qba73/vbox2vm.git",
    packages=find_packages(),
    package_data={
        'ovf': ['templates/*.j2']
    },
    install_requires=[
        'Click',
        'lxml',
        'bs4',
        'jinja2'
    ],
    entry_points='''
        [console_scripts]
        ovf=ovf.ovf:cli
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
