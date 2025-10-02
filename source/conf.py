# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Student SOC Documentation'
copyright = '2025, Cal Poly Pomona - Student-led Security Operations Center'
author = 'Collaborators @ Student SOC'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
release = '1.0.0'

extensions = ['myst_parser']

templates_path = ['_templates']
exclude_patterns = []

master_doc='index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# lets not cache, especially since im doing lots of css now
html_use_smartypants = False
html_add_permalinks = None

html_context = {
    'meta_tags': '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" /><meta http-equiv="Pragma" content="no-cache" /><meta http-equiv="Expires" content="0" />'
}

html_file_suffix = '.html'
html_copy_source = False
html_show_sourcelink = False
