import codecs
import os

from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def long_description():
    return f'''{read('docs/user-guide.md')}

# Release Notes

{read('docs/release-notes.md')}
'''


setup(
    name='routeviews',
    version='0.1.2',
    description='CLI tools that support RouteViews.',
    long_description_content_type='text/markdown',
    long_description=long_description(),
    author='University of Oregon',
    author_email='rleonar7@uoregon.edu',
    license='MIT',
    url='https://github.com/routeviews/routeviews-cli',
    keywords=['RouteViews', 'CLI', 'peeringdb', 'API', 'Integration'], 
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'routeviews-template=routeviews.scripts.template:run_main',
            'routeviews-email-peers=routeviews.scripts.rv_get_peers_email:main',
            'routeviews-lint=routeviews.scripts.format_ansible_inventory:run_main',
            'routeviews-build-peer=routeviews.scripts.ansible_peering_request:run_main',
        ]
    },
    install_requires=[
        'ConfigArgParse>=1',
        'netmiko>=3',
        'pathvalidate>=2',
        'PyYAML>=6',
        'rdap>=1',
        'requests>=2',
        'ruamel.yaml>=0.17',
        'tabulate>=0.8',
        'uologging>=0.7.3',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Networking :: Monitoring',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.8',
    ]
)
