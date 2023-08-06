import os
import sys
import paver
from paver.easy import options, Bunch
import paver.setuputils

#pylint: disable=unused-import
from runestone import build  # build is called implicitly by the paver driver.

paver.setuputils.install_distutils_tasks()

sys.path.append(os.getcwd())

home_dir = os.getcwd()
master_url = '{{master_url}}'
master_app = '{{master_app}}'
serving_dir = "{{build_dir}}"
dest = "{{dest}}"

options(
    sphinx = Bunch(docroot=".",),

    build = Bunch(
        builddir="{{build_dir}}",
        sourcedir="_intermediate",
        outdir="{{build_dir}}",
        confdir=".",
        project_name = "{{project_name}}",

        # leave template_args empty, use html_context from conf.py
        template_args= {}
    )
)
