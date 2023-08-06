
import os
import stat
import click
import pathlib

from rich.console import Console
from rich.markdown import Markdown

from tnote.func_module import EDITOR, RECENT, get_index, write_index, intialize_files


class Note:

    def __init__(self, **k: str):
        # ensuring valid id must be done before a note is created
        intialize_files()
        self.id = k['id']
        self.path = pathlib.Path(k['path'])
        self.name = self.path.name
        self.path = self.path.resolve()
        self.create_file()

    def note_exists(self):
        return self.path.exists() and self.path.is_file()

    def create_parent(self, path):
        parent_dir = path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)

    def create_file(self):
        if self.note_exists():
            if not self.note_in_index():
                # allow for the addition of notes created outside tnote
                self.add_to_index()
            else:
                return
        else:
            self.create_parent(self.path)
            self.path.touch()
            self.add_to_index()
            self.update_recent()

    def note_in_index(self):
        index = get_index()
        return self.id in index.keys()

    def delete_from_index(self):
        index = get_index()
        index.pop(self.id)
        write_index(index)

    def add_to_index(self):
        index = get_index()
        path = self.path.__str__()
        index[self.id] = {'name': self.name, 'path': self.path.__str__()}
        write_index(index)

    def rename_note(self, new_name: str):
        if '.' not in new_name:
            new_name += '.md'
        new_path = self.path.parent.joinpath(new_name)
        self.move_note(new_path)

    def move_note(self, new_path: str):
        npath = pathlib.Path(new_path)
        if npath.exists():
            print("This path already exists")
        else:
            self.create_parent(npath)
            self.path.rename(new_path)
            self.path = npath
            self.name = npath.name
            self.add_to_index()
            self.update_recent()

    def change_id(self, new_id):
        self.delete_from_index()
        self.id = new_id
        self.create_file()

    def delete_note(self):
        self.path.unlink()
        self.delete_from_index()
        self.update_recent()

    def view_note(self):
        os.system('clear -x')
        console = Console()
        with open(self.path, 'r+') as note:
            console.print(Markdown(note.read()))
        self.update_recent()

    def edit_note(self):
        click.edit(editor=EDITOR, filename=self.path)
        self.update_recent()

    def update_recent(self):
        index = get_index()
        if self.path.exists():
            path = str(self.path)
            index[RECENT] = {'id': self.id, 'name': self.name, 'path': path}
        elif RECENT in index.keys():
            index.pop(RECENT)
        write_index(index)

    def exe(self, chmod=False):
        if chmod:
            self.path.chmod(stat.S_IEXEC)
        os.system(self.path)
