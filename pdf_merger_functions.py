"""
functions for pdf_merger gui
oktl 22 May 2023
27 Jul 2023 revised code with Sourcery.
"""
import datetime
import webbrowser
from pathlib import Path

import PySimpleGUI as sg
from pypdf import PdfMerger

# declare some sg aliases
B = sg.Button
T = sg.Text


def check_inputs(values: dict) -> list:
    '''
    Loop through inputs to see if any are empty.
    
    Returns
    -------
    empty_inputs : list
        A list of any inputs that are empty, empty list if none.
    '''
    
    # Get a dictionary of keys and empty values.    
    no_values = {key: value for (key, value) in values.items() if value == ''}
    return [*no_values]


def make_file_list(folder: Path, file_extension: str) -> list:
    """ Get a list of all filenames of type 'extension' in a folder. """
    
    # List comprehension to Glob folder for extension and 
    # cull only the filenames from the globbed list. 
    # Return list of filenames only, no paths.
    return [i.name for i in folder.glob(file_extension)]


def merge_pdfs(pdfs: list[str], output: str) -> None:
    """ Combine any number of pdfs in the list and write to new .pdf file. """

    # Create pdf file merger object.
    merger = PdfMerger()
    # Append pdfs one by one.
    for pdf in pdfs:
        merger.append(pdf)
    # Write combined pdf to output pdf file.
    with open(output, 'wb') as file:
        merger.write(file)
        

def confirm_file_exists(filename:str) -> bool:
    """ Check to see if file exists. """
    
    return Path(filename).exists()


def confirm_file_does_not_exist(filename:str) -> bool:
    """Check to see if file does not exists."""
    return not Path(filename).exists()


def open_file_in_browser(filename: str) -> None:
    """ Open a file in the os default web browser. """
    
    # use with here?
    # file_to_open = str(Path(filename))
    file_to_open = (Path(filename))
    webbrowser.open_new(file_to_open)
    
    
def open_text_file(file_to_open):
    """
    Open a file for reading.

    Parameters
    ----------
    file : text file

    Returns
    -------
    contents : the file, read,  to use
    """

    # Using the 'with' keyword automatically closes file, no need to do it explicitly.
    # 'r' option opens file as read only.
    with open(file_to_open, 'r') as file:
        contents = file.read()
        
    return contents
    
    
def convert_bytes(size: float):
    """ Convert integer of whatever length of bytes
        to string in  KB, MB, GB or TB size.
    """
    
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f'{size: .2f} {x}'
        size /= 1024.0

    return size


def get_file_attributes(filename: Path) -> tuple:
    """ Get some attributes of a file  - for delete popup. """
    
    file_stats = Path(filename).stat()
    file_size = file_stats.st_size
    file_size_str = convert_bytes(file_size)
    file_time = file_stats.st_mtime
    file_time_str = datetime.datetime.fromtimestamp(file_time).strftime('%m/%d/%Y %H:%M')
        
    return file_size_str, file_time_str


def delete_popup(title: str, text:str, filename: Path) -> None:
    """ Custom popup to confirm delete. """
        
    window = sg.Window(
        title,
        [
            [
                sg.Image(get_delete_icon()),
                T('Are you sure you want to delete this file?'),
            ],
            [sg.Image(get_custom_icon()), T(text)],
            [sg.OK(), sg.Cancel()],
        ],
    )
    event, values = window.read()

    if event != 'OK': 
        ...
    else:
        
        filename.unlink()

    window.close()


def delete_file(filename: Path) -> None:
    """ Delete a file with a popup to confirm. """
    
    file_size, file_time = get_file_attributes(filename) 
    
    newline = '\n'
    ask_lines = (f'{newline} {filename} {newline} Size:  {file_size} {newline} Date modified:  {file_time} {newline}')
    
    delete_popup('Delete', ask_lines, filename)


# User defined layout elements
# Shortcut for the information frames.
def information_frame(title: str, key:str) -> sg.Frame:
    """ User defined custom frame element for displaying information. """

    return [sg.Frame(layout=[[sg.Text('', size=(46, 3), justification='c', key=key)]],
                    title=title, title_location=sg.TITLE_LOCATION_TOP,
                    font='Calibri 10', pad=((0, 0), (5, 15)))]


# Shortcut for the button frame.
def action_buttons_frame(title: str) ->sg.Frame:
    """ User defined custom frame element for placing buttons. """

    return [sg.Frame(layout=[
                [sg.Column(layout=[
                    [B('Merge Files', tooltip='Do the magic!', bind_return_key=True ),
                    B('Clear', tooltip=' Clear all data '),
                    B('Open', tooltip=' Open the new file ', disabled=True, key='-OPEN-'),
                    B('Exit',)],
                ], pad=((0, 0), (15, 15)))],],
            title=title, title_location=sg.TITLE_LOCATION_TOP,
            font='Calibri 14', pad=((0, 0), (15, 15)))
            ]


def open_about_window(title: str, text_file) -> sg.Window:
    """ User defined custom window to show a text file.
    Open a new window, show the text file.

    Parameters
    ----------
    title : string
    text : 
    """

    layout = [
        [T(title, font='Calibri 12 bold')],
        [T(text_file, auto_size_text=True, font='Calibri 9'),],
        [B('OK', enable_events=True, bind_return_key=True, focus=True)]]
    window = sg.Window(title, layout, no_titlebar=True, text_justification='c',
                    element_justification='c', finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'OK', ):
            break    
    window.close()


def print_inputs(values: dict) -> None:
    """ Print all values by key. """
#    key_value_dict = {key: value for (key, value) in values.items()}
    key_value_dict = dict(values) 
    keys_and_values = [key_value_dict]

    sg.Print(f'values.items are: {keys_and_values}')     

    
def get_custom_icon() -> bytes:
    """ Return a base 64 representation of an image. """    
    return b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAACxUlEQVR4nO3X7UtTURwH8L2I/odeZrW7xIIMjZaWLxKFYK2JblBvelHQqOiBoQahkVGvtBcRzHuFbLFgsp1rIUQrKxTDUWphVDj24IK6OXonvhD8xt3RbffuBsa4Z5vcA1+2c8497HzufueOmUxGM5q+Dc4q6JKOnfcqFrB24Qg7BHQArH6bw5q7gQ1CF4D0kx0CegFYIaAnQGKA0B0g6YxgApB0RDADSDohmAIkHRDMAZISUZaA/4nJADiNbwBGCRXTjBJyGiVUXNuaJXStFUgmcln4DoRHgI2/il0nlfMzU0D/pdz6vrPK+eR6rjYzAnhOAEt/gNQPYOIF8Gma9r/MAactwA0H7S8uAlNhIJWi/YfddP3dc7Qfj9L1G3E3MgbMvqd91y7gwyQdu3UmB4i8pfMXmwBpCUjE6LUbgFfBEpWQGiBn7AkdG7hSCJAzP0PH5DIrG8D8LH3f46LlII/JfS1A5B0d67JrltDy8FAJAOqEeDqvBZjWAPz6nTm86fGv8B0cReToZcaAWBTwDwDem0D3qdy8FuDzx/USalCUUNrWCF+1HwInZqJGsDsD+VED5LrP3O0k4NqdBaQfBRWb10KUFhCPA+OEvsp9oTf7GE1PLcJXq9y4FqK0gEydL9En0ANPdj7tuQ5f/dg/N5+P0AdQRFbb92LS2onXh3ozeV57X7Fpf81wdk6OYAkdLiuAOolWmwIQru9jcIgNQJXxDWy6GSXk3OKHON5qVwBe1t2pLMBc03kFYGT/YOUAVtr2wV/zuOAXONrSVj6AZccBxFocBZHvvF9j83KGLCFMWDux0NwBgRttz4+XI1amAPUhLTY8JxITyyaYiX1zGyMzgpmsVhyA58gKbya3e4692Ta0RzwucGK0rABe87M6gSMBdXiODApm4vZagjvyrw9UB7YLnGgTONLPc+Rp4VrRk/8BfwH/VulgMBaDXgAAAABJRU5ErkJggg=='


def get_delete_icon() -> bytes:
    """ Return a base 64 representation of an image. """    
    return b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAMAAADXqc3KAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAA4VBMVEX//////v7+/v7+/Pz++/v42trsmZnfVFTWJyfSEhL+/f3me3vUGxvQBwfaPDzhYWHlc3PUHBzldnb42dnvra3XKCjSDQ3ja2v1zc376urSDg7XKSnxtrbrmZnRDAzZODj1y8vSERHtoKDvq6veT0/77e3eTk7wtLTaOTn65+fXKirmenr0yMj88vLxurr87+/319fjamrxubnQBgbleHjmeXn32Njsmpr99vbQBQXleXn99fX1ycn66enld3fhYGDmfHzTEhLkcXHkcnL0x8f65ub77OzZNzf1ysr76enjbGysa4tLAAAAAWJLR0QAiAUdSAAAAAd0SU1FB+cGFBQYHW2cS94AAAE8SURBVCjPdVKJVsIwEJzuprQNttAicohAUe5LubQKVEVF/f8PMsGLpzTv5eVldmd2MxvAADEJM2XZjmNbKVOQBBnY4TDTR66XyWYznusHOUjSsMKP8yeFYokBLhUL5dMKBBEgcVat1XWWVBoS9VrYUCAY59WLJlhIUksKRrMVthUMM9/pqlMxFF8xGN1OzwTQLw9Aw9FY0yXGoyFhUA6AS/9KJU2mM2gpzKcTdS34C1y7RTDdzKNbyUzzaHanAks3BctbQdftT9fMOqzrrDwLdoaxK7qO+ulovesAIrbhZDVBR+7DhzRpP9R+dOBsEgJ2LA5LJRZPbHeR9EAE/y150pbA7P018bmmTWS0w9bLj+38a7tEI9zuDep1+zkoIoFKr/w12rfl+/doDZ2VC3zXizebeO8zwFAaB77PBybvJeRgmYXnAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDIzLTA2LTIwVDIwOjIzOjM0KzAwOjAwVPG1+QAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyMy0wNi0yMFQyMDoyMzozNCswMDowMCWsDUUAAAAASUVORK5CYII='

    