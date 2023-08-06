__author__ = 'petlja'

import os
import shutil

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('pycode', PyCodeDirective)

    app.add_stylesheet('pycode.css')

    app.add_javascript('pycode.js')
 

    app.add_node(PyCodeNode, html=(visit_info_note_node, depart_info_note_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div id="%(divid)s" class="pycode" data-code="%(code)s" %(imgpath)s %(scale)s>
"""

TEMPLATE_END = """
    </div>
"""


class PyCodeNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(PyCodeNode, self).__init__()
        self.components = content


def visit_info_note_node(self, node):
    node.delimiter = "_start__{}_".format(node.components['divid'])
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.components
    self.body.append(res)


def depart_info_note_node(self, node):
    res = TEMPLATE_END
    self.body.append(res)
    self.body.remove(node.delimiter)


class PyCodeDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {}
    option_spec.update({
        'folder': directives.unchanged,
        'script': directives.unchanged,
        'images': directives.unchanged,
        'scale': directives.unchanged,
    })
    def run(self):


        env = self.state.document.settings.env

        if 'script' not in self.options:
            self.error('No script path specified')

        if 'folder' not in self.options:
            self.error('No folder path specified')      

        if 'images' in self.options:
            self.options['images'] = [image.strip() for image in self.options['images'].split(',')]
        else:
            self.options['images'] = []

        if 'scale' in self.options:
            self.options['scale'] = 'data-scale = "{}"'.format( self.options['scale'])
        else:
            self.options['scale'] = 'data-scale = "1"'

        fname = self.options['folder'].replace('\\', '/')
        source, _ = self.state_machine.get_source_and_line()
        if not os.path.isabs(fname):
            fname = os.path.join(os.path.dirname(source),fname)
        path = os.path.join(fname, self.options['script'])

        self.options['code'] = ""
        try:
            with open(path, encoding='utf-8') as f:
                self.options['code'] = html_escape(f.read())
        except:
            self.error('Source file could not be opened')


        for image in self.options['images']:
            path = os.path.dirname(os.path.join(fname, image))
            img = os.path.basename(image)
            cwd = os.path.abspath(os.getcwd())
            try:
                build_file_path = os.path.join(cwd,os.path.dirname(os.path.join('_build/_images/',image)))
                src_file_path = os.path.join(path,img)
                build_file_path_img = os.path.join(cwd, os.path.join(os.path.dirname(os.path.join('_build/_images/',image)),img))
                if not os.path.exists(build_file_path):
                    os.makedirs(build_file_path)
                shutil.copyfile(src_file_path, build_file_path_img)
            except:
                self.error('Images could not be copied')

        self.options['divid'] = self.arguments[0]

        self.options['imgpath'] = 'data-img-path= "../../_images/"'

        pycode = PyCodeNode(self.options)

        return [pycode]

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
