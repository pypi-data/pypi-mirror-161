from pyfiglet import Figlet


def figletise(projectname):
    figlet = Figlet(font='slant')
    return f'\n{figlet.renderText(projectname)}'
