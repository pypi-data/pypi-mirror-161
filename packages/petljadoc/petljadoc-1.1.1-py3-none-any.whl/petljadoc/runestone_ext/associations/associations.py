__author__ = 'petlja'

import os
import shutil
import json
from tokenize import group

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from runestone.common.runestonedirective import add_i18n_js


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('associations', AssociationsDirective)

    app.add_stylesheet('associations.css')

    app.add_javascript('associations.js')
    add_i18n_js(app, {"en","sr-Cyrl","sr","sr-Latn"},"associations-i18n")

    app.add_node(AssociationsQNode, html=(visit_associations_note_node, depart_associations_note_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div id="%(divid)s" class="asc" data-game='%(data)s'>
"""

TEMPLATE_END = """
    </div>
"""


class AssociationsQNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(AssociationsQNode, self).__init__()
        self.components = content


def visit_associations_note_node(self, node):
    node.delimiter = "_start__{}_".format(node.components['divid'])
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.components
    self.body.append(res)


def depart_associations_note_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class AssociationsDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {}
    option_spec.update({
        'final_answer': directives.unchanged,
        'answer_a': directives.unchanged,
        'group_a': directives.unchanged,
        'answer_b': directives.unchanged,
        'group_b': directives.unchanged,
        'answer_c': directives.unchanged,
        'group_c': directives.unchanged,
        'answer_d': directives.unchanged,
        'group_d': directives.unchanged,
    })
    def run(self):
        env = self.state.document.settings.env 
        self.options['divid'] = self.arguments[0]
        if 'final_answer' not in self.options:
            raise self.error('Missing final_anser')

        group_dict_a = {"group":"A"}
        group_dict_b = {"group":"B"}
        group_dict_c = {"group":"C"}
        group_dict_d = {"group":"D"}

        if 'answer_a' in self.options: 
            group_dict_a["group-answ"] = self.options['answer_a']
        else:
            group_dict_a["group-answ"] = ""
        if 'answer_b' in self.options: 
            group_dict_b["group-answ"] = self.options['answer_b']
        else:
            group_dict_b["group-answ"] = ""
        if 'answer_c' in self.options: 
            group_dict_c["group-answ"] = self.options['answer_c']
        else:
            group_dict_c["group-answ"] = ""
        if 'answer_d' in self.options: 
            group_dict_d["group-answ"] = self.options['answer_d']
        else:
            group_dict_d["group-answ"] = ""

        if 'group_a' in self.options: 
            group_dict_a["clues"] = self.options['group_a'].split(',')
        else:
            group_dict_a["clues"] = []
        if 'group_b' in self.options: 
            group_dict_b["clues"] = self.options['group_b'].split(',')
        else:
            group_dict_b["clues"] = []
        if 'group_c' in self.options: 
            group_dict_c["clues"] = self.options['group_c'].split(',')
        else:
            group_dict_c["clues"] = []
        if 'group_d' in self.options: 
            group_dict_d["clues"] = self.options['group_d'].split(',')
        else:
            group_dict_d["clues"] = []

        self.options['data'] = json.dumps({"clues" : [group_dict_a,group_dict_b,group_dict_c,group_dict_d],"answer": self.options["final_answer"]})

        #self.options['data'] = '{"clues":[{"group":"A", "clues" : ["test","test2","test","test2"], "group-answ" : "Odgovor"},{"group":"B", "clues" : ["test3","test4","test","test2"],"group-answ" : "(O|o)dgovor"},{"group":"A", "clues" : ["test","test2"], "group-answ" : "Odgovor"},{"group":"B", "clues" : ["test3","test4"],"group-answ" : "(O|o)dgovor"}], "answer":42}'
        ascnode = AssociationsQNode(self.options)
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
