from pig.editor.util import create_demo_project, open_project
from pug import App

App()
project = create_demo_project()
if project:
    open_project( project)