from flask import Flask, render_template
from flask_flatpages import FlatPages
from collections import defaultdict
from os import walk, listdir
from os.path import isdir, isfile
import re



DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = '/home/grant/programming/gitick-projects'
TAG_DICT = defaultdict(list)
USER_DICT = defaultdict(list)

IS_MD_FILE = re.compile('\.md$')

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)

def fill_tags(fname):
    path_name = fname.replace(FLATPAGES_ROOT,'/')[1:-3]     # used for the url
    for l in open(fname,'r'):
        if 'tags:' == l[:5]:
            if len(l) > 5:
                for t in l[5:].strip().replace('[','').replace(']','').split(','):
                    if t != '':
                        TAG_DICT[t.strip().lower()].append(path_name)
                        
def tagList(tags):
    if type(tags) is str:
        return tags.split(',')
    else: return tags            

def collect_user( userdirs, fname):
    for user in userdirs:
        if fname.find(user + '/') > -1:
            USER_DICT[user].append(fname.replace(FLATPAGES_ROOT,'/')[1:-3])
        
def init_dicts():
    touched = {}
    userdirs = [x for x in listdir(FLATPAGES_ROOT)
                if isdir(FLATPAGES_ROOT + x) and isfile( FLATPAGES_ROOT + x + '/.gitick')]

    for (dn,_,fl) in walk(FLATPAGES_ROOT):
        for f in fl:
            fname = dn + '/' + f
            if ((not touched.get(fname) and IS_MD_FILE.search(fname))):
                touched[fname] = True
                fill_tags( fname )
                collect_user( userdirs, fname )

@app.route('/')
def index():
    tags = list(TAG_DICT.keys())
    tags.sort()
    users = list(USER_DICT.keys())
    users.sort()
    data = {
        'pages':pages,
        'tags': tags,
        'users' : users
    }
    return render_template('index.html', data=data)  

@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    tags = tagList(page['tags'])
    priority = int(page['priority'])
    return render_template('ticket.html', page=page, tags=tags, priority=priority)

## tags is either a list of tags or a string of comma separated tags

@app.route('/tagged/<tag>/')
def tagged(tag):
    paths = TAG_DICT[tag]
    paths.sort()
    tagged = {'tag' : tag, 'paths' :paths}
    
    return render_template('tagged.html', tagged=tagged)

@app.route('/user/<user>/')
def user(user):
    paths = USER_DICT[user]
    paths.sort()
    assigned = {'user' : user, 'paths' : paths}
    return render_template('user.html', assigned=assigned)


if __name__ == '__main__':
    init_dicts()
    app.run(port=8000)
    
