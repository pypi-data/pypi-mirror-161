#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'petlja'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
import json
import os
from runestone.common.runestonedirective import add_i18n_js, add_codemirror_css_and_js, add_skulpt_js

def setup(app):
    app.add_directive('blockly-karel', BlocklyKarelDirective)

    app.add_javascript('acorn_interpreter.js')
    app.add_javascript('blockly_compressed.js')
    app.add_javascript('msg/sr.js')
    app.add_javascript('blocks_compressed.js')
    app.add_javascript('javascript_compressed.js.')
    app.add_javascript('karelBlockly.js')
    app.add_javascript('karelBlocks.js')

    app.add_stylesheet('karelBlockly.css')

    app.add_node(BlocklyKarelNode, html=(visit_karel_node, depart_karel_node))

    app.connect('doctree-resolved', process_karel_nodes)
    app.connect('env-purge-doc', purge_karel_nodes)


TEMPLATE_START = """
<div>
<div id="blocklyKarelDiv" style="height: 500px;width: 780px;margin-top: 20px;" data-categories='%(data_categories)s' ></div>
<div data-childcomponent="%(divid)s" class="karel_section course-box course-box-problem">
    <div class="course-content">
"""

TEMPLATE_END = """
    <div data-component="blocklyKarel" id="%(divid)s" class="karel_section">
        <div class="karel_actions col-md-12 mb-2"><button class="btn btn-success run-button">Покрени програм</button>
        <button class="btn btn-default reset-button">Врати на почетак</button>
        %(export_button)s
        </div>
        <div style="overflow: hidden;" class="karel_actions col-md-12" >
            <section class="col-md-12">
                <article>
                    <textarea class="configArea" style="display:none"><!--x %(initialcode)s x--></textarea>
                </article>
            </section>
            <section class="col-md-12">
                <article>
                    <canvas class="world" style="border-style: solid; border-width: 2px; border-color: inherit; background: white;" width="300" height="300">
                        <p>Please try loading this page in HTML5 enabled web browsers. All the latest versions of famous browsers such as Internet explorer, Chrome, Firefox, Opera support HTML5.</p>
                    </canvas>
                </article>
            </section>
        </div>
    </div>
</div></div>
</div>

"""

class BlocklyKarelNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(BlocklyKarelNode, self).__init__()
        self.karel_components = content


def visit_karel_node(self, node):
    node.delimiter = "_start__{}_".format(node.karel_components['divid'])

    self.body.append(node.delimiter)

    res = TEMPLATE_START % node.karel_components
    self.body.append(res)


def depart_karel_node(self, node):
    res = TEMPLATE_END % node.karel_components
    self.body.append(res)
    self.body.remove(node.delimiter)

def process_karel_nodes(app, env, docname):
    pass


def purge_karel_nodes(app, env, docname):
    pass


class BlocklyKarelDirective(Directive):
    """
.. karel::
    :blockly: -- use blocky
    """
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {
        'blockly': directives.flag,
        'categories' : directives.unchanged,
        'exportmode' : directives.flag,
    }
    def run(self):
        """
        generate html to include Karel box.
        :param self:
        :return:
        """

        env = self.state.document.settings.env
        categories = ["KarelCommands","KarelBrain","Values", "Branching", "KarelBranching", "Loops", "KarelLoops", "Logic", "KarelSays", "Arithmetic"]
        self.options['name'] = self.arguments[0].strip()
        self.options['divid'] = self.arguments[0]

        if not self.options['divid']:
            raise Exception("No divid")


        explain_text = None
        if self.content:
            if '~~~~' in self.content:
                idx = self.content.index('~~~~')
                explain_text = self.content[:idx]
                self.content = self.content[idx+1:]
            source = "\n".join(self.content)
        else:
            source = '\n'

        if 'categories' in self.options:
            author_categories = [categoty.strip() for categoty in self.options['categories'].split(',') if categoty.strip() in categories]
            self.options['data_categories'] = json.dumps(author_categories)
        else:
            self.options['data_categories'] = json.dumps(categories)
        if 'exportmode' in self.options:
            self.options['export_button'] = '<button class="btn btn-default export-button">Сачувај стање</button>'
        else:
            self.options['export_button'] = ''

        self.options['initialcode'] = source.replace("<", "&lt;")
        str = source.replace("\n", "*nline*")
        str0 = str.replace("\"", "*doubleq*")
        str1 = str0.replace("(", "*open*")
        str2 = str1.replace(")", "*close*")
        str3 = str2.replace("'", "*singleq*")
        self.options['argu'] = str3

        knode = BlocklyKarelNode(self.options)
        self.add_name(knode)    # make this divid available as a target for :ref:

        return [knode]

