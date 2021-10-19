
# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'pythium'
copyright = '2021, UoM,ATLAS'
author = 'Mohamed Aly'

release = '0.1'
version = '0.1.0'
import os,sys
sys.path.insert(0, os.path.abspath('../../scripts/'))
# -- General configuration

extensions = [
            'sphinx.ext.duration',
                'sphinx.ext.doctest',
                    'sphinx.ext.autodoc',
                        'sphinx.ext.autosummary',
                            'sphinx.ext.intersphinx',
                            'sphinx.ext.napoleon'
                            ]

intersphinx_mapping = {
            'python': ('https://docs.python.org/3/', None),
                'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
                }
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_logo = '../../misc/pythium_logo.png'
# -- Options for EPUB output
epub_show_urls = 'footnote'
