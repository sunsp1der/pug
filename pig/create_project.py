from pig.editor.util import create_new_project, open_project
from pug import App


def create_project():
    App()
    project = create_new_project()
    if project:
        open_project( project)
        
if __name__ == "__main__":
    create_project()