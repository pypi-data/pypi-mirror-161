import os


# Pathlike object of current project
PROJECT_PATH = os.getcwd()

# Name of the current project
PROJECT_TITLE = os.path.split(PROJECT_PATH)[1]


# Build Path based on current working directory
def build_path(path: str) -> str:
    """
    Pass any pathlike object and get the absolute path of desired destination.
    The current working directory is used as starting point.\n
    e.g.: build_path('myfolder/mysubfolder/filename.py')
    will return: 'absolute_path/to/my/project_title/myfolder/mysubfolder/filename.py'.
    """
    return os.path.join(PROJECT_PATH, path)


def split_filepath(path: str) -> 'tuple[str, str]':
    """
    Pass a pathlike object or filename to split
    the filename and the file extension.
    Returns a 2-element tuple (docname, docext).
    e.g.: docname, docext = split_filepath('mypath/to/myfile.csv')
    * docname = myfile
    * docext = .csv
    """
    path, docext = os.path.splitext(path)
    _, docname = os.path.split(path)
    return docname, docext
