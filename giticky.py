from flask import Flask, render_template
from flask_flatpages import FlatPages
from collections import defaultdict
from os import walk, listdir
from os.path import isdir, isfile
import re

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG

app = Flask(__name__)

IS_MD_FILE = re.compile('\.md$')

PROJECTS = ['wwb', 'giticky']

TAG_DICT = defaultdict(list)

def init_tickets_for(proj):
    config = proj + '.cfg'
    app.config.from_pyfile(config)
    return FlatPages(app, name=proj)

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
    
def get_ticket_paths(tickets):
    ticket_paths = [ticket.path for ticket in tickets] #list of strings
    ticket_paths.sort()
    return ticket_paths

def get_subdirs(proj):
    return [d for d in listdir(proj) if d[0] != '.'] 

## lod is a list of directories (strings) tickets is a flatpages.pages object
## returns a dict of directory : list of tickets (tickets are page objects)
def project_index(lod, tickets):
    index_dict = defaultdict(list)
    for d in lod:
        [index_dict[d].append(t) for t in tickets if t.path[:len(d)] == d]
    return index_dict


# def fill_tags(ticket):
#     for tag in tag_list(ticket['tags']):
#         TAG_DICT[tag].append(ticket.path)

# def init_dicts():
#     for ticket in TICKETS:
#         fill_tags(ticket)

@app.route('/')
def top():
    projects = PROJECTS
    return render_template('top.html', projects=projects)

@app.route('/<project>')
def index(project):
    tickets = init_tickets_for(project)
    subdirs = get_subdirs(tickets.root)
    ticket_index = project_index(subdirs, tickets)
    return render_template('index.html', ticket_index=ticket_index, project=project, subdirs=subdirs)  

@app.route('/<project>/<path:path>/')
def ticket(path, project):
    tickets = init_tickets_for(project)
    ticket = tickets.get_or_404(path)
    priority = int(ticket['priority'])
    ticket_tags = tag_list(ticket['tags'])
    data = {
        'ticket': ticket,
        'ticket_tags': ticket_tags,
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


# @GITICKY.route('/user/<user>/')
# def user(user):
#     paths = USER_DICT[user]
#     paths.sort()
#     assigned = {'user' : user, 'paths' : paths}
#     return render_template('user.html', assigned=assigned)


if __name__ == '__main__':
    app.run(port=8000)
    
