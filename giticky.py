from flask import Flask, render_template
from flask_flatpages import FlatPages
from collections import defaultdict
from os import walk, listdir
from os.path import isdir, isfile
import re



DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = '/home/grant/programming/gitick-projects/wwb.gitick'
TAG_DICT = defaultdict(list)
USER_DICT = defaultdict(list)

IS_MD_FILE = re.compile('\.md$')

app = Flask(__name__)
app.config.from_object(__name__)
tickets = FlatPages(app) #this is a flatpages.pages object, a collection of page(s)

def fill_tags(fname):
    path_name = fname.replace(FLATPAGES_ROOT,'/')[1:-3]     # used for the url
    for l in open(fname,'r'):
        if 'tags:' == l[:5]:
            if len(l) > 5:
                for t in l[5:].strip().replace('[','').replace(']','').split(','):
                    if t != '':
                        TAG_DICT[t.strip().lower()].append(path_name)

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

## tagList is used in the case that page['tags'] is a string
## it removes excess whitespace and makes the tag lowercase to avoid duplicates
## tagList: (U str list) -> list
def tagList(tags):
    if type(tags) is str:
        taglist = tags.split(',')
        return [tag.strip().lower() for tag in taglist]
    else: return [t.strip().lower() for t in tags]
    
ticket_paths = [ticket.path for ticket in tickets] #list of strings
ticket_paths.sort()
topdirs = [d for d in listdir(FLATPAGES_ROOT) if d[0] != '.'] 

## lod is a list of directories (strings) tickets is a flatpages.pages object
## returns a dict of directory : list of tickets (tickets are page objects)
def project_index(lod, tickets):
    index_dict = defaultdict(list)
    for d in lod:
        [index_dict[d].append(t) for t in tickets if t.path[:len(d)] == d]
    return index_dict

## like the above function except just uses paths instead of tickets
## using paths seems to be fine, because in the templates you can use the
## url_for('ticket', path=ticket_path) to generate links to the pages themselves
def project_index_paths(lod, t_paths):
    index_dict = defaultdict(list)
    for d in lod:
        [index_dict[d].append(t) for t in t_paths if t[:len(d)] == d]
    return index_dict

INDEX_DICT = project_index_paths(topdirs, ticket_paths)

@app.route('/')
def index():
    tags = list(TAG_DICT.keys())
    tags.sort()
    subdirs = list(INDEX_DICT.keys())    
    data = {
        'tickets': INDEX_DICT,
        'tags': tags,
        'subdirs' : subdirs,
    }
    return render_template('index.html', data=data)  

@app.route('/<path:path>/')
def ticket(path):
    ticket = tickets.get_or_404(path)
    tags = tagList(ticket['tags'])
    priority = int(ticket['priority'])
    data = {
        'ticket': ticket,
        'tags': tags,
        'priority': priority
    }
    return render_template('ticket.html', data=data)

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
    app.run(host='192.168.2.6', port=8000)
    
