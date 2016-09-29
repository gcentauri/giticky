import sh
from pathlib import Path
from itertools import takewhile
import operator
import yaml

        
class Ticket:
    ''' 
    A ticket is a markdown file with a YAML header.  We would like to parse
    this file and gather data like: title, meta, body, tags, mtime, etc etc, 
    '''
    def __init__(self, path):
        self.path = Path(path)
        self.modified = self.path.stat().st_mtime
        self.name = self.path.name

    def meta(self):
        return 
    
        
class Gitick:

    '''
    A Gitick object represents a git repository full of markdown
    files that are Tickets.  
    '''
    
    root = Path # pathlib Path object
    tickets = [] # list of Paths
    users = [] # list of Paths
    
    def __init__(self, path):
        self.root = Path(path).absolute()
        if self.root.exists():
            self.tickets = sorted(self.root.glob('**/*.md'))
        else:
            self.new()
        self._home()
        
    def __len__(self):
        return len(self.tickets)

    def __getitem__(self, position):
        return self.tickets[position]

    def _home(self):
        sh.cd(self.root.as_posix())
    
    def new(self):
        newdirs = [self.root / x for x in ['new',
                                           'new/need-info',
                                           'backlog',
                                           'tested']]
        
        self.root.mkdir()
        for d in newdirs:
            d.mkdir()

        sh.cd(self.root.as_posix())
        sh.echo( '.', _out='.gitick' )
        sh.echo( '..', _out='new/.gitick' )
        sh.echo( '../..', _out='new/need-info/.gitick' )

        sh.git( 'init', '.' )
        sh.git( 'add', '.' )
        sh.git( 'commit', '-m', str("initial commit for " + self.root.name) )

    
    def add_ticket(self, title, priority, tags):
        '''
        title is a string
        priority is an int from 1 to 9
        tags is a list of strings
        '''
        curdir = str(sh.pwd()).rstrip()
        sh.cd(self.root.as_posix())
        ticket_file = ( 'new/' + title.replace(' ','-') + '.md' )
        title = 'title: ' + title
        priority = 'priority: ' + str(priority)
        tags = 'tags: ' + '[' + ', '.join(tags) + ']'
        date = 'date: ' + str(sh.date()).strip()
        reported = 'reported: ' + str(sh.git('config', 'user.name'))
        
        with open( ticket_file, 'w' ) as ticket:

            metaString = '\n'.join([title, priority, tags, date, reported])
            headings = '\n'.join(['## summary', '# LOG'])
            
            ticket.write(metaString)
            ticket.write('\n')
            ticket.write(headings)
            ticket.close()

        self.tickets = sorted(self.tickets + [Path(self.root, ticket_file)])
        sh.cd(curdir)

    def user_create(self, name):
        newdirs = [Path(name)] + [Path(name) / x for x in ['in-progress',
                                                           'need-info',
                                                           'test']]
        for d in newdirs:
            d.mkdir()

        sh.echo( '../..', _out=name + '/in-progress/.gitick' )
        sh.echo( '../..', _out=name + '/need-info/.gitick' )
        sh.echo( '../..', _out=name + '/test/.gitick' )
        
        sh.git('add', '.')
        sh.git('commit', '-m', str("adding user " + name))

        self.users = self.users = [Path(name)]


    # allows tof get in-progress, testing, need-info (must have tix directly
    # under parent tho)
    def get_tickets_from_parent( self, parent ):
        return [t for t in self.tickets if t.parent.name == parent]

    def in_progress( self ):
        return self.get_tickets_from_parent("in-progress")

    def new_tickets( self ):
        return self.get_tickets_from_parent("new")

    
    
##---------------------------------------------------------##
## just for testing ##

PROJ = Gitick('/home/grant/projects/gitick-projects/giticky.gitick')
TOPDIR = [x for x in PROJ.root.iterdir() if x.is_dir() and x.name[0] is not '.']
TIX = PROJ.tickets
NEW = PROJ.new_tickets()
WIP = PROJ.in_progress()


## old gitick functions

# def home(self):
#     with open( '.gitick', 'r' ) as f:
#         l = f.read()
#         f.close()
#     return l.rstrip()
