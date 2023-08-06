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
    app.add_directive('nimgame', NimGameDirective)

    app.add_stylesheet('nimgame.css')

    app.add_javascript('nimgame.js')
    add_i18n_js(app, {"en","sr-Cyrl","sr","sr-Latn"},"nimgame-i18n")

    app.add_node(NimGamesNode, html=(visit_nim_game_node, depart_nim_game_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div id="%(divid)s" class="nim-game" data-nimgame='%(data)s'>
        <div class="switch-wrapp">
        <label class="switch">
            <input type="checkbox" checked>
            <span class="slider round"></span>
        </label>
        <p data-game-mode></p>
        </div>
        <div class="canvas-wrapper">
        <canvas>

        </canvas>
        </div>
        <div class="canvas-control">          
            <div class="game-input">
                <div class="player-one row">
                <input data-input-id="player-1">
                <button class="btn btn-success" data-id="player-1">
                </button>
                </div>
                <div class="player-two row">
                    <input data-input-id="player-2">
                    <button class="btn btn-success" data-id="player-2">
                    </button>
                </div>
            </div>
            <button class="btn btn-danger res-btn" data-restart></button>
            <div class="msg-banner">        
            </div>
"""

TEMPLATE_END = """
        </div>
    </div>
"""


class NimGamesNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(NimGamesNode, self).__init__()
        self.components = content


def visit_nim_game_node(self, node):
    node.delimiter = "_start__{}_".format(node.components['divid'])
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.components
    self.body.append(res)


def depart_nim_game_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class NimGameDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {}
    option_spec.update({
        'takeaway': directives.unchanged,
        'count': directives.unchanged,
    })
    def run(self):
        env = self.state.document.settings.env 
        self.options['divid'] = self.arguments[0]
        data = {}
        if 'takeaway' not in self.options: 
            data['takeaway']  = 2
        else:
            data['takeaway'] = int(self.options['takeaway'])
        if 'count' not in self.options: 
            data['count'] = 15
        else:
            data['count'] = int(self.options['count']) 

        self.options['data'] = json.dumps(data)
        nimgamenode = NimGamesNode(self.options)
        return [nimgamenode]

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
