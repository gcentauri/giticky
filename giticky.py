from flask import Flask, render_template
from flask_flatpages import FlatPages
from collections import defaultdict
from os import walk
import re



DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'tickets'
TAG_DICT = defaultdict(list)

IS_MD_FILE = re.compile('\.md$')

def init_tag_dict():
    touched = {}

    for (dn,_,fl) in walk(FLATPAGES_ROOT):
        for f in fl:
            fname = dn + '/' + f
            if ((not touched.get(fname) and IS_MD_FILE.search(fname))):
                touched[fname] = True
                path_name = fname[1:-3]
                for l in open(fname,'r'):
                    if 'tags:' == l[:5]:
                        if len(l) > 5:
                            for t in l[5:].split(','):
                                TAG_DICT[t.strip().lower()].append(path_name)


app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)

@app.route('/')
def index():
    data = {'pages':pages, 'tags': list(TAG_DICT.keys())}
    return render_template('index.html', data=data)  

@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    tags = tagList(page['tags'])
    priority = int(page['priority'])
    return render_template('ticket.html', page=page, tags=tags, priority=priority)

## tags is either a list of tags or a string of comma separated tags
def tagList(tags):
    if type(tags) is str:
        return tags.split(',')
    else: return tags            

@app.route('/tagged/<tag>/')
def tagged(tag):
    print("got tag: " + tag)
    tagged = {'tag' : tag, 'paths' : TAG_DICT[tag]}
    
    return render_template('tagged.html', tagged=tagged)

if __name__ == '__main__':
    init_tag_dict()
    print(TAG_DICT)
    app.run(port=8000)
    
