
# Configuration file for the Sphinx documentation builder.
import os,sys
sys.path.insert(0, os.path.abspath('../../src/'))
# -- Project information

project = 'pythium'
copyright = '2021, UoM,ATLAS'
author = 'Mohamed Aly'

import pythium
release = '0.1'
version = pythium.__version__

# -- General configuration

extensions = [
            'sphinx.ext.duration',
            'sphinx.ext.doctest',
            'sphinx.ext.autodoc',
            'sphinx.ext.autosummary',
            'sphinx.ext.intersphinx',
            'sphinx.ext.napoleon',
            'sphinx.ext.todo',
            'sphinx_autodoc_typehints'
            ]

intersphinx_mapping = {
            'python': ('https://docs.python.org/3/', None),
            'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
                }
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_logo = '../../misc/Pythium.png'
# -- Options for EPUB output
epub_show_urls = 'footnote'
