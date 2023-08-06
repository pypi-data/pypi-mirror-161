__author__ = 'petlja'

import os
import shutil
import json

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from runestone.common.runestonedirective import add_i18n_js


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('regex-check', RegexCheckDirective)

    app.add_stylesheet('regex-check.css')

    app.add_javascript('regex-check.js')
    add_i18n_js(app, {"en","sr-Cyrl","sr","sr-Latn"},"regex-check-i18n")

    app.add_node(RegexCheckQNode, html=(visit_regex_check_note_node, depart_regex_check_note_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div id="%(divid)s" class="regex-check" data-regex='%(data)s''>
        <div>
            <p class="title"></p>
            <textarea type="text" spellcheck="false"  class="regex-input"></textarea>
        </div>
        <div>
            <p class="title flags"><span class="flag-markers"></span></p>
        </div>
        <div class="editor-wrapper">
            <p class="title"></p>
            <div class="test-text">
                <div class="regex-text front"></div>
                <textarea spellcheck="false" autocomplete="false"  class="hidden-ta text-input"></textarea>
            </div>
            %(getsol)s
"""

TEMPLATE_END = """
        </div>
    </div>
"""


class RegexCheckQNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(RegexCheckQNode, self).__init__()
        self.components = content


def visit_regex_check_note_node(self, node):
    node.delimiter = "_start__{}_".format(node.components['divid'])
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.components
    self.body.append(res)


def depart_regex_check_note_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class RegexCheckDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {}
    option_spec.update({
        'solution': directives.unchanged,
        'editable': directives.unchanged,
        'flags': directives.unchanged,
        'initregex': directives.unchanged,
    })
    def run(self):
        env = self.state.document.settings.env 
        self.options['divid'] = self.arguments[0]
        data = {}
        if 'solution' not in self.options: 
            data['solution']  = ""
            self.options['getsol'] = ""
        else:
            data['solution'] = self.options['solution']
            self.options['getsol'] = '<div class="test-button"></div><div class="sol-button"></div>'

        if 'editable' in self.options: 
            data['editable'] = True
        else:
            data['editable'] = False

        if 'flags' not in self.options: 
            data['flags']= ""
        else:
            data['flags'] = self.options['flags']
            
        if 'initregex' not in self.options: 
            data['initregex']= ""
        else:
            data['initregex'] = self.options['initregex']

        data['text'] = '\n'.join(self.content)

        self.options['data'] = json.dumps(data)
        ascnode = RegexCheckQNode(self.options)
        return [ascnode]

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)
