#!/usr/bin/env python
"""
vim: Pure Python Vim clone.
Usage:
    vim [-p] [-o] [-O] [-u <vimrc>] [<location>...]

Options:
    -p           : Open files in tab pages.
    -o           : Split horizontally.
    -O           : Split vertically.
    -u <vimrc> : Use this .vimrc file instead.
"""
from __future__ import unicode_literals
import docopt
import os

from vim.editor import Editor
from vim.rc_file import run_rc_file

__all__ = (
    'run',
)


def run():
    a = docopt.docopt(__doc__)
    locations = a['<location>']
    in_tab_pages = a['-p']
    hsplit = a['-o']
    vsplit = a['-O']
    vimrc = a['-u']

    # Create new editor instance.
    editor = Editor()

    # Apply rc file.
    if vimrc:
        run_rc_file(editor, vimrc)
    else:
        default_vimrc = os.path.expanduser('~/.vimrc')

        if os.path.exists(default_vimrc):
            run_rc_file(editor, default_vimrc)

    # Load files and run.
    editor.load_initial_files(locations, in_tab_pages=in_tab_pages,
                              hsplit=hsplit, vsplit=vsplit)
    editor.run()


if __name__ == '__main__':
    run()
