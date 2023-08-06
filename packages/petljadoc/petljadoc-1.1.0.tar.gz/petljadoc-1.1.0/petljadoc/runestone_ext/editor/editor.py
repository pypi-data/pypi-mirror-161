__author__ = 'petlja'
import json
import os

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from runestone.common.runestonedirective import add_i18n_js


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('petlja-editor', EditorDirective)

    app.add_stylesheet('editor.css')

    app.add_javascript('editor.js')
    app.add_javascript('jszip.js')
    add_i18n_js(app, {"en","sr-Cyrl","sr","sr-Latn"},"editor-i18n")

    app.add_node(EditorNode, html=(visit_nim_game_node, depart_nim_game_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div id="%(divid)s" class="petlja-editor" data='%(data)s'>
"""

TEMPLATE_END = """
    </div>
"""


class EditorNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(EditorNode, self).__init__()
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


class EditorDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {
        'html': directives.unchanged,
        'js': directives.unchanged,
        'css': directives.unchanged,
    }
    def run(self):
        env = self.state.document.settings.env 
        self.options['divid'] = self.arguments[0]
        contents = "\n".join(self.content).split("~~~")
        #data = {"html":{"name":"main.html", "source":""},"js":{"name":"main.js", "source":""},"css":{"name":"main.css", "source":""}}
        data = {}
        if "html" in self.options:
            fname = self.options['html'].replace('\\', '/')
            source, _ = self.state_machine.get_source_and_line()
            type = "html"
            if not os.path.isabs(fname):
                path = os.path.join(os.path.dirname(source),fname)
            else:
                path = fname
            try:
                with open(path, encoding='utf-8') as f:
                    data[type] = {}
                    data[type]["name"] =  fname.rsplit("/")[-1]
                    data[type]["source"] =  html_escape(f.read())
            except:
                self.error('Source file could not be opened')

            if "css" in self.options:
                fname = self.options['css'].replace('\\', '/')
                source, _ = self.state_machine.get_source_and_line()
                type = "css"
                if not os.path.isabs(fname):
                    path = os.path.join(os.path.dirname(source),fname)
                else:
                    path = fname
                try:
                    with open(path, encoding='utf-8') as f:
                        data[type] = {}
                        data[type]["name"] =  fname.rsplit("/")[-1]
                        data[type]["source"] =  html_escape(f.read())
                except:
                    self.error('Source file could not be opened')
            if "js" in self.options:
                fname = self.options['js'].replace('\\', '/')
                source, _ = self.state_machine.get_source_and_line()
                type = "js"
                if not os.path.isabs(fname):
                    path = os.path.join(os.path.dirname(source),fname)
                else:
                    path = fname
                try:
                    with open(path, encoding='utf-8') as f:
                        data[type] = {}
                        data[type]["name"] =  fname.rsplit("/")[-1]
                        data[type]["source"] =  html_escape(f.read())
                except:
                    self.error('Source file could not be opened')

        else:
            for file in contents:
                file = file.strip('\n')
                if len(file):
                    try:
                        name_type,type,source = parse(file)
                    except:
                        raise Exception("Couldn't parse editor directive. ID:{}".format(self.options['divid']))
                    data[type] = {}
                    data[type]["name"] = name_type
                    data[type]["source"] =  html_escape(source)

        self.options['data'] = json.dumps(data)
        editornode = EditorNode(self.options)
        return [editornode]

html_escape_table = {
    "&": "&amp;",
    '"': "\"",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


def parse(file_content):
    name_type = file_content.split('\n')[0]
    type = name_type.split('.')[1]
    if type not in ["html","css","js"]:
        raise Exception
    source =  "\n".join(file_content.split('\n')[1:])
    return name_type, type, source