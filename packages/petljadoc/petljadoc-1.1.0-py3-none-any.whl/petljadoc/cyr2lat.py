import os
import re
import shutil
import datetime
import jinja2
import sys
import cyrtranslit

extensionList = ['md', 'rst', 'ipynb', 'txt', 'html', 'js', 'css'] 


def title_fix(srt_content):
    new_content_rows = srt_content.split('\n')
    top_title = re.search(r"^([=|\~]|\-|\'|\:)\1*$",new_content_rows[0])    
    if(top_title is not None and ((new_content_rows[0])!= len(new_content_rows[1]))):
        new_content_rows[0] = new_content_rows[0][0]*len(new_content_rows[1]) 
    for i in range (1,len(new_content_rows)):
        title = re.search(r"^([=|\~]|\-|\'|\:)\1*$",new_content_rows[i-1])
        underline = re.search(r"^([=|\~]|\-|\'|\:)\1*$",new_content_rows[i])
        if((underline is not None) and (new_content_rows[i-1])!= len(new_content_rows[i]) and (title is None)):
            new_content_rows[i]=new_content_rows[i][0]*len(new_content_rows[i-1])
    srt_content=""
    for row in new_content_rows:
        srt_content+= row+"\n"
    return srt_content.rstrip()+"\n"

def cyr2latTranslate(src_dir, dest_dir):
    # print(f"D {src_dir} -> {dest_dir}")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for item in os.listdir(src_dir):
        extension = os.path.splitext(item)[1][1:]
        s = os.path.join(src_dir, item) 
        if os.path.isdir(s):
            d = os.path.join(dest_dir, item)
            cyr2latTranslate(s, d)
        else:
            d = os.path.join(dest_dir, item)
            shutil.copyfile(s,d)
            f = open(s, encoding="utf8")
            content = f.read()
            newF = open(d, "w", encoding="utf8")
            newF.truncate(0)
            
            if extension in extensionList:
                new_content = cyrtranslit.to_latin(content, 'sr')
                if(extension == "rst"):
                    new_content = title_fix(new_content)
                newF.write(new_content)
            else:
                newF.write(content)
            newF.close()
            #print(f"C {s} -> {d}")
