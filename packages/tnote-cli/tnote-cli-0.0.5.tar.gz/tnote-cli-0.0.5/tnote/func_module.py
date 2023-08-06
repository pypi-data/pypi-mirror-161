import os
import json


DATAPATH = os.path.expanduser('~/.tnote/')
NOTESPATH = os.path.join(DATAPATH, "notes")
CONFIGPATH = os.path.expanduser('~/.tnoterc')
INDEXPATH = os.path.join(DATAPATH, "index.json")
EDITOR = os.getenv("$EDITOR")
RECENT = '.recent'


def print_index():
    intialize_files()
    index_dict = get_index()
    print("\
|-------------------------INDEX-------------------------|\n\
\n")
    if RECENT in index_dict.keys():
        print("\
|-------------------------RECENT------------------------|\n\
 Note ID: {}\n\
 Name: {}\n\
 Path: {}\n\
|-------------------------------------------------------|\n\
    \n\
            _________________________________\n\
            \n".format(index_dict[RECENT]['id'], index_dict[RECENT]['name'], index_dict[RECENT]['path']))
    keys = index_dict.keys()
    for key in keys:
        if key == RECENT:
            continue
        print("\
|-------------------------------------------------------|\n\
 Note ID: {}\n\
 Name: {}\n\
 Path: {}\n\
|-------------------------------------------------------|\n".format(key, index_dict[key]['name'], index_dict[key]['path']))


def intialize_files():
    if not os.path.exists(CONFIGPATH):
        open(CONFIGPATH, "x")
    if not os.path.exists(DATAPATH):
        os.mkdir(DATAPATH)
    if not os.path.exists(NOTESPATH):
        os.mkdir(NOTESPATH)
    if not os.path.exists(INDEXPATH):
        index = open(INDEXPATH, 'w')
        index.write('{\n\n}')
        index.close()


def get_index(name=None):
    intialize_files()
    index_dict = {}
    with open(INDEXPATH, 'r') as index_file:
        index_dict = json.load(index_file)
        try:
            return index_dict[name]
        except KeyError:
            return dict(index_dict)


def write_index(dict: dict):
    with open(INDEXPATH, 'w') as index:
        json.dump(dict, index)


def recent_check(index):
    try:
        note_id = index[RECENT]['id']
        return note_id
    except KeyError:
        print("Error: Cannot find recent note you are looking for")
        quit()


def index_check(index, note_id, action):
    try:
        return index[note_id]['path']
    except KeyError:
        if action == 'move':
            print("Error: Cannot move a note that doesn't exist")
            quit()
        return
