
import os
import click
from tnote.note_module import Note
from tnote.func_module import NOTESPATH, RECENT, index_check, print_index, get_index, recent_check


@click.command()
@click.argument("note_id", required=False)
@click.option('--recent', '-r', is_flag=True, show_default=True, default=False, help='Opens most recent note')
@click.option("--edit", "-e", 'action', flag_value='edit', show_default=True, default='edit')
@click.option("--view", "-v", 'action', flag_value='view', show_default=True, default='edit')
@click.option("--delete", "-d", 'action', flag_value='del', show_default=True, default='edit')
@click.option('--rename', '-rn', 'rename')
@click.option("--move", "-m", 'move', type=click.Path(readable=True, writable=True, dir_okay=False), help='allows you to move a note to the specified path')
@click.option('--execute', '-x', count=True)
@click.option('--path', '-p', 'to_path', type=click.Path(readable=True, writable=True, dir_okay=False), help='Specify the path to the note if not specified will go in the default notes folder')
def cli(**k):
    index = get_index()
    if k['recent']:
        k['note_id'] = recent_check(index)
    if k['note_id'] == None:
        print_index()
        return
    path = index_check(index, k['note_id'], k['action']) or k['to_path']
    path = path or os.path.join(NOTESPATH, k['note_id']+'.md')
    note = Note(id=k['note_id'], path=path)
    if k['move'] is not None:
        note.move_note(k['move'])
        return
    if k['rename'] is not None:
        note.rename_note(k['rename'])
        return
    if k['execute'] >= 1:
        note.exe(False)
        if k['execute'] >= 2:
            note.exe(True)
            return
        return

    match k['action']:
        case 'edit':
            note.edit_note()
        case 'del':
            note.delete_note()
        case 'view':
            note.view_note()


if __name__ == '__main__':
    cli()
