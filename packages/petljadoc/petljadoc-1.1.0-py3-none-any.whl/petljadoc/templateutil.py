import os
import re
import shutil
import datetime
import jinja2

_template_pattern = re.compile(r"^.*(\.t)\.[^\.]+$")

def default_template_arguments():
    return {"now":datetime.datetime.now()}

def apply_template_dir(src_dir, dest_dir, template_params, filter_name=None):
    # print(f"D {src_dir} -> {dest_dir}")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for item in os.listdir(src_dir):
        if filter_name and not filter_name(src_dir, item):
            continue
        s = os.path.join(src_dir, item)     
        if os.path.isdir(s):
            d = os.path.join(dest_dir, item)
            apply_template_dir(s, d, template_params, filter_name)
        else:
            match = _template_pattern.match(item)
            if match:
                i,j = match.span(1)
                d = os.path.join(dest_dir, item[:i] + item[j:])
                with open(s, "r", encoding='utf8') as sf:
                    t = jinja2.Template(sf.read())
                dtext = t.render(template_params)
                with open(d, "w", encoding='utf8') as df:
                    df.write(dtext)
                #print(f"T {s} -> {d}")
            else:
                d = os.path.join(dest_dir, item)
                shutil.copyfile(s,d)
                #print(f"C {s} -> {d}")
