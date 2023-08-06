# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
from importlib import import_module
from tempfile import NamedTemporaryFile
from docutils import nodes
from docutils.frontend import OptionParser
from docutils.parsers.rst import Directive, Parser
from docutils.utils import new_document
from sphinx.errors import ExtensionError

# -- Project information -----------------------------------------------------

project = "omni"
copyright = "2021, David Montez, Andrew Van"  # pylint: disable=redefined-builtin
author = "David Montez, Andrew Van"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.viewcode", "myst_parser", "numpydoc"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# autodoc/autosummary settings
autoclass_content = "class"
autodoc_default_options = {"members": True}
autosummary_generate = True

# myst parser settings
myst_enable_extensions = ["amsmath", "dollarmath"]
myst_heading_anchors = 6

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"
html_context = {"default_mode": "dark"}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
html_logo = "_static/logo.png"


def skip_member(app, what, name, obj, skip, opts):
    if "CustomTextHelpFormatter" in name:  # skip CustomTextHelpFormatter
        return True
    return None


class AddArgumentDirective(Directive):
    required_arguments = 2

    def run(self):
        # try to import the script selected
        try:
            selected_script = import_module(self.arguments[0])
        except ModuleNotFoundError as module_exception:
            # throw error if invalid
            raise ExtensionError(
                "Could not find module: %s, line number: %s" % (self.arguments[0], self.lineno),
                module_exception,
                self.name,
            ) from module_exception

        # generate the parser from the selected script
        parser = selected_script.generate_parser()

        # fix the prog name of the parser
        parser.prog = "omni_" + selected_script.__name__.split("omni.scripts.")[1]

        # try to find the selected argument from the script,
        selected_argument = None
        for action in parser._actions:  # pylint: disable=protected-access
            # look at destination name
            if self.arguments[1] == action.dest:
                selected_argument = action
                break
        # raise error if not found
        if not selected_argument:
            raise ExtensionError(
                "Could not find argument: %s, line number: %s" % (self.arguments[1], self.lineno), modname=self.name
            )

        # check number of args
        if selected_argument.nargs in ("+", "*"):
            nargs = "\u221e"
        else:
            nargs = selected_argument.nargs

        # get option strings or destination name if a positional argument
        if selected_argument.option_strings:
            if nargs != 0 and selected_argument.default != "==SUPPRESS==":
                arg_name = " " + selected_argument.dest.upper()
            else:
                arg_name = ""
            if nargs:  # add ellipsis when multiple args
                arg_name += " ..."
            option_string = ("%s, " % arg_name).join(selected_argument.option_strings)
            option_string += " " + arg_name
        else:  # this is a positional argument
            option_string = selected_argument.dest

        # add indicator multiple arguments if set
        if selected_argument.nargs:
            option_string += " (Number of Arguments: {0})".format(nargs)

        # if a default exists add it to option_string
        if selected_argument.default and selected_argument.default != "==SUPPRESS==":
            option_string += " (default: {0})".format(selected_argument.default)

        # parse paragraphs from help text
        paragraphs = self.parse_paragraphs(selected_argument.help)

        # in the help text, replace the [sphinx-build] text with the program name
        # since the parser mistakenly uses sphinx as the program name
        # on ReadTheDocs this is replaced with __main__.py
        paragraphs = [paragraph.replace("[sphinx-build]", f"[{parser.prog}]") for paragraph in paragraphs]
        paragraphs = [paragraph.replace("[__main__.py]", f"[{parser.prog}]") for paragraph in paragraphs]

        # create list of paragraph nodes
        paragraph_nodes = [self.parse_rst(p) for p in paragraphs]

        # create option help text
        option_item = nodes.option_list_item(
            "",
            nodes.option_group("", nodes.option("", nodes.option_string(text=option_string))),
            nodes.description("", *paragraph_nodes),
        )

        # create options list
        # ideally this should group more than one option
        # but to make this directive flexible we just try to wrap each
        # individual argument in it's own options list
        option_list = nodes.option_list("", option_item)
        return [option_list]

    def parse_paragraphs(self, text):
        # split text on "\n"
        split_text = text.split("\n")

        # join lines that are part of the same paragraph
        paragraphs = list()
        for line in split_text:
            if line == "":
                paragraphs.append("")
            else:
                try:
                    if paragraphs[-1] != "":
                        paragraphs[-1] += " "
                    paragraphs[-1] += line
                except IndexError:  # on an IndexError just append
                    paragraphs.append(line)

        # drop any empty paragraphs
        paragraphs = [p for p in paragraphs if p != ""]

        # return paragraphs
        return paragraphs

    def parse_rst(self, text):
        parser = Parser()
        with NamedTemporaryFile() as f:
            document = new_document(f.name, settings=OptionParser(components=(Parser,)).get_default_values())
        parser.parse(text, document)
        # return unwrapped from document
        return document.children[0]


def setup(app):
    app.connect("autodoc-skip-member", skip_member)
    app.add_directive("add_argument", AddArgumentDirective)
