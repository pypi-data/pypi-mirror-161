__author__ = 'petlja'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('quizq', QuizQDirective)

    app.add_node(QuizQNode, html=(visit_info_note_node, depart_info_note_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div class="quiz-question">
"""

TEMPLATE_END = """
    </div>
"""


class QuizQNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(QuizQNode, self).__init__()
        self.note = content


def visit_info_note_node(self, node):
    node.delimiter = "_start__{}_".format("info")
    self.body.append(node.delimiter)
    res = TEMPLATE_START
    self.body.append(res)


def depart_info_note_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class QuizQDirective(Directive):
    required_arguments = 0
    optional_arguments = 0
    has_content = True

    def run(self):


        env = self.state.document.settings.env

        qnode = QuizQNode(self.options)

        self.state.nested_parse(self.content, self.content_offset, qnode)

        return [qnode]

