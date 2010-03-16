from pig.editor.util import create_new_project, open_project
from pug import App

App()
project = create_new_project()
if project:
    open_project( project)