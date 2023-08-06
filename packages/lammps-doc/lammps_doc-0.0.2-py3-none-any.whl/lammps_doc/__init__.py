from bs4 import BeautifulSoup
from IPython.display import display, HTML
import os

html_path = os.environ.get('LAMMPS_HTML_PATH')+'/'

def list_matching(command):
    if '_' in command:
        prefix = command.split('_')[0]
        cmds = list_commands(prefix)
    else:
        cmds = list_commands()
    n = int(len(command)*0.8)
    seta = set(command)
    ml = []
    for i in cmds:
        if len(seta & set(i)) >= n:
            ml.append(i)
    return ml

def list_commands(prefix=''):
    import glob
    ll = glob.glob(f'{html_path}{prefix}*.html')
    kk = [i.split('/')[-1][0:-5] for i in ll]
    return kk

def get_soup(command):
    from bs4 import BeautifulSoup
    from IPython.display import display, HTML
    with open(f'{html_path}{command}.html', 'r') as f:
        lines = f.readlines()
        f.close()
    dd = ''
    for i in lines:
        dd += i
    gg = BeautifulSoup(dd, 'html.parser')
    return gg

def get_syntax(command):
    try:
        data = HTML(str(get_soup(command).find_all('section', attrs={'id':'syntax'})[0]))
        display(data)
    except:
        print(f'{command} not found')
        print(f'Maybe one of these \n {list_matching(command)}')

def get_examples(command):
    try:
        data = HTML(str(get_soup(command).find_all('section', attrs={'id':'examples'})[0]))
        display(data)
    except:
        print(f'{command} not found')
        print(f'Maybe one of these \n {list_matching(command)}')

def get_description(command):
    try:
        data = HTML(str(get_soup(command).find_all('section', attrs={'id':'description'})[0]))
        display(data)
    except:
        print(f'{command} not found')
        print(f'Maybe one of these \n {list_matching(command)}')
