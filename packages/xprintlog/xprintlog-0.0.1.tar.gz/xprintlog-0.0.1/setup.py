from setuptools import setup
from setuptools import find_packages

__version__ = '0.0.1'
__author__ = 'dwpeng'
__email__ = '1732889554@qq.com'


with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name='xprintlog',
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__author__,
    maintainer_email=__email__,
    description='Patch your print function.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/dwpeng/xprint',
    keywords=['print', 'logging', 'log'],
    packages=find_packages('src'),
    package_dir={"": "src"},
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
