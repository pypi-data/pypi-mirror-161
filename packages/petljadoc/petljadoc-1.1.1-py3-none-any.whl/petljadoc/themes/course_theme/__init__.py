from os import path


def get_html_theme_path():
    """Return list of HTML theme paths."""
    cur_dir = path.abspath(path.dirname(path.dirname(__file__)))
    return cur_dir


def setup(app):
    app.add_html_theme('petljadoc_course_theme', path.abspath(path.dirname(__file__)))
    app.add_message_catalog('sphinx', path.join(path.abspath(path.dirname(__file__)), 'locale'))
