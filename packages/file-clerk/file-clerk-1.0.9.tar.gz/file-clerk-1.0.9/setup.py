# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['file_clerk']

package_data = \
{'': ['*']}

install_requires = \
['autodoc>=0.5.0,<0.6.0',
 'autoflake8>=0.3.2,<0.4.0',
 'black>=22.6.0,<23.0.0',
 'bs4>=0.0.1,<0.0.2',
 'isort>=5.10.1,<6.0.0',
 'mkdocs-awesome-pages-plugin>=2.7.0,<3.0.0',
 'mkdocs-enumerate-headings-plugin>=0.5.0,<0.6.0',
 'mkdocs-git-authors-plugin>=0.6.4,<0.7.0',
 'mkdocs-git-revision-date-localized-plugin>=1.1.0,<2.0.0',
 'mkdocs-img2fig-plugin>=0.9.3,<0.10.0',
 'mkdocs-material>=8.3.9,<9.0.0',
 'mkdocs-minify-plugin>=0.5.0,<0.6.0',
 'mkdocs-print-site-plugin>=2.3.4,<3.0.0',
 'mkdocs-table-reader-plugin>=1.1.0,<2.0.0',
 'mkdocs>=1.3.1,<2.0.0',
 'mkdocstrings-python>=0.7.1,<0.8.0',
 'mkdocstrings>=0.19.0,<0.20.0',
 'mkgendocs>=0.9.1,<0.10.0',
 'mknotebooks>=0.7.1,<0.8.0',
 'nltk>=3.7,<4.0',
 'pip-licenses>=3.5.4,<4.0.0',
 'pre-commit>=2.20.0,<3.0.0',
 'pyrsistent>=0.18.1,<0.19.0',
 'tqdm>=4.64.0,<5.0.0']

extras_require = \
{'docs': ['Sphinx==4.2.0',
          'sphinx-rtd-theme==1.0.0',
          'sphinxcontrib-napoleon==0.7']}

setup_kwargs = {
    'name': 'file-clerk',
    'version': '1.0.9',
    'description': 'A collection of functions for dealing with files and file content.',
    'long_description': 'file-clerk\n==========\n\nA collection of functions for dealing with files and file content.\n\nThis was a library I created for previous projects that deal with files\nand file paths in order to get code from files, lists of files in\nproject folders, file extensions, and allows us to capture just files\nof a particular type. I also developed my projects on Windows OS, so\nthese functions were designed to work with the file paths on Windows,\nMac, and Linux (Windows is the one with backslashes - wacky, I know.).\n\nTypical usage example:\n----------------------\n\n:code:`extension = get_file_type("path/to/file.js")`\n\n:code:`code_string = file_to_string("path/to/file.html")`\n\n:code:`project_path = "path/to/project"`\n:code:`all_project_files = get_all_project_files(project_path)`\n:code:`just_css_files = get_all_files_of_type(project_path, "css")`\n',
    'author': 'hundredvisionsguy',
    'author_email': 'cwinikka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/HundredVisionsGuy/file-clerk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
