__author__ = 'petlja'

import os
import shutil

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


def setup(app):
    app.connect('html-page-context', html_page_context_handler)
    app.add_directive('gallery', GalleryDirective)

    app.add_stylesheet('gallery.css')

    app.add_javascript('gallery.js')
 

    app.add_node(GalleryNode, html=(visit_info_note_node, depart_info_note_node))


def html_page_context_handler(app, pagename, templatename, context, doctree):
    app.builder.env.h_ctx = context

TEMPLATE_START = """
    <div class="gallery" id="%(divid)s">
        <div>
            <div style="width: %(width)s;height:%(height)s">
            %(imgnodes)s

"""

TEMPLATE_END = """
            </div>
        </div>
    </div>
    <div class="nav-gallery row" id="%(divid)s-nav">
        <div class="prev-img">
        &#10094;
        </div>
        <div class="next-img">
        <span class="float-right">&#10095;</span>
        </div>
    </div>
"""


class GalleryNode(nodes.General, nodes.Element):
    def __init__(self, content):
        super(GalleryNode, self).__init__()
        self.components = content


def visit_info_note_node(self, node):
    node.delimiter = "_start__{}_".format(node.components['divid'])
    self.body.append(node.delimiter)
    res = TEMPLATE_START % node.components
    self.body.append(res)


def depart_info_note_node(self, node):
    res = TEMPLATE_END  % node.components
    self.body.append(res)
    self.body.remove(node.delimiter)


class GalleryDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {}
    option_spec.update({
        'folder': directives.unchanged,
        'images': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged
    })
    def run(self):

        env = self.state.document.settings.env
 
        if 'width' not in self.options:
            self.options['width'] = '780px'          
        if 'height' not in self.options:
            self.options['height'] = '780px'   

        self.options['imgnodes'] = '' 

        if 'folder' not in self.options:   
            self.options['folder'] = '../../_images'

        if 'images' in self.options:
            self.options['images'] = [image.strip() for image in self.options['images'].split(',')]
        else:
            self.options['images'] = []

        fname = self.options['folder'].replace('\\', '/')
        source, _ = self.state_machine.get_source_and_line()
        if not os.path.isabs(fname):
            fname = os.path.join(os.path.dirname(source),fname)
            
        first = True
        for image in self.options['images']:
            path = os.path.dirname(os.path.join(fname, image))
            img = os.path.basename(image)
            cwd = os.path.abspath(os.getcwd())
            try:
                src_file_path = os.path.join(path,img)
                build_file_path = os.path.join(cwd,os.path.dirname(os.path.join('_build/_images/',image)))
                build_file_path_img = os.path.join(cwd, os.path.join(os.path.dirname(os.path.join('_build/_images/',image)),img))
                if not os.path.exists(build_file_path):
                    os.makedirs(build_file_path)
                shutil.copyfile(src_file_path, build_file_path_img)
            except:
                self.error('Images could not be copied')
            self.options['imgnodes'] = self.options['imgnodes']  + ('<img src="../_images/{}" width="100%" height="100%">\n'.format(image) if first else '<img src="../_images/{}" width="100%" height="100%" style="display: none;">\n'.format(image))
            first = False
           
        self.options['divid'] = self.arguments[0]

        gallery = GalleryNode(self.options)

        return [gallery]
