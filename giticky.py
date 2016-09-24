from flask import Flask, render_template
from flask_flatpages import FlatPages
from collections import defaultdict
from os import walk, listdir
from os.path import isdir, isfile
import re

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = '/home/grant/projects/gitick-projects/giticky.gitick'

IS_MD_FILE = re.compile('\.md$')

app = Flask(__name__)
app.config.from_object(__name__)
TICKETS = FlatPages(app) #this is a flatpages.pages object, a collection of page(s)
TAG_DICT = defaultdict(list)

## tag_list is used in the case that page['tags'] is a string
## it removes excess whitespace and makes the tag lowercase to avoid duplicates
## tag_list: (U str list) -> list

def tag_list(tags):
    if type(tags) is str:
        taglist = tags.split(',')
        return [tag.strip().lower() for tag in taglist]
    elif type(tags) is list:
        return [t.strip().lower() for t in tags]
    else: return []
    
    
TICKET_PATHS = [ticket.path for ticket in TICKETS] #list of strings
TICKET_PATHS.sort()
TOPDIRS = [d for d in listdir(FLATPAGES_ROOT) if d[0] != '.'] 

## lod is a list of directories (strings) tickets is a flatpages.pages object
## returns a dict of directory : list of tickets (tickets are page objects)
def project_index(lod, tickets):
    index_dict = defaultdict(list)
    for d in lod:
        [index_dict[d].append(t) for t in tickets if t.path[:len(d)] == d]
    return index_dict

INDEX_DICT = project_index(TOPDIRS, TICKETS)

## like the above function except just uses paths instead of tickets
## using paths seems to be fine, because in the templates you can use the
## url_for('ticket', path=ticket_path) to generate links to the pages themselves
def project_index_paths(lod, t_paths):
    index_dict = defaultdict(list)
    for d in lod:
        [index_dict[d].append(t) for t in t_paths if t[:len(d)] == d]
    return index_dict

PATH_DICT = project_index_paths(TOPDIRS, TICKET_PATHS)

def fill_tags(ticket):
    for tag in tag_list(ticket['tags']):
        TAG_DICT[tag].append(ticket.path)

def init_dicts():
    for ticket in TICKETS:
        fill_tags(ticket)

        
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
    tags = list(TAG_DICT.keys())
    tags.sort()
    ticket = TICKETS.get_or_404(path)
    ticket_tags = tag_list(ticket['tags'])
    priority = int(ticket['priority'])
    data = {
        'ticket': ticket,
        'ticket_tags' : ticket_tags,
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

# @app.route('/user/<user>/')
# def user(user):
#     paths = USER_DICT[user]
#     paths.sort()
#     assigned = {'user' : user, 'paths' : paths}
#     return render_template('user.html', assigned=assigned)


if __name__ == '__main__':
    init_dicts()
    app.run(port=8000)
    
