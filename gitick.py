import sh

def new():
    gitick_project = 'gitick.' + input( 'project name: ' )
    sh.mkdir( gitick_project )
    sh.cd( gitick_project )
    sh.echo( '.', _out='.gitick' )
    sh.mkdir( 'new' )
    sh.echo( '..', _out='new/.gitick' )
    sh.mkdir( 'new/need-info' )
    sh.echo( '../..', _out='new/need-info/.gitick' )
    sh.git( 'init', '.' )
    sh.git( 'add', '.' )
    sh.git( 'commit', '-m', str("initial commit for " + gitick_project) )

def home():
    with open( '.gitick', 'r' ) as f:
        l = f.read()
        f.close()
        return l.rstrip()
        
def add():
    curdir = str(sh.pwd()).rstrip()
    sh.cd( home() )
    title = input( 'New ticket name: ' )
    ticket_file = ( 'new/' + title.replace(' ','-') + '.md' )
    priority = str( 'priority: ' + input('Priority: ') )
    tags = str('tags: ' + input('Tags (separate by commas): '))
    
    ## please show me a better way to do this, i'm just doing a dumb
    ## translation of the sh script
    
    with open( ticket_file, 'w' ) as ticket:
        ticket.write(priority + '\n')
        ticket.write(tags + '\n')
        ticket.write('date: ' + str(sh.date()))
        ticket.write('reported: ' + str(sh.git('config', 'user.name')))
        ticket.write('\n')
        ticket.write(str('# ' + title))
        ticket.write('\n')
        ticket.write(str('# LOG'))
        ticket.close()

    sh.cd(curdir)
        
def user():
    curdir = str(sh.pwd()).rstrip()
    sh.cd( home() )

    name = input( 'New user name: ' )
    sh.mkdir( name )
    sh.cd(name)
    sh.mkdir('in-progress', 'need-info', 'test')
    sh.echo( '../..', _out='in-progress/.gitick' )
    sh.echo( '../..', _out='need-info/.gitick' )
    sh.echo( '../..', _out='test/.gitick' )

    sh.git('add', '.')
    sh.git('commit', '-m', str("adding user " + name))

    sh.cd(curdir)
    
    
