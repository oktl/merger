"""
created by oktl 20 May 2023
gui for helping merge several .pdfs into one

27 Jul 2023 revised code with Sourcery.

VERSION: 1.00

"""

from os import chdir
from pathlib import Path

import PySimpleGUI as sg

import pdf_merger_functions as mf

# These lines are needed for the Help and About files,
# to change to the path with the Resources folder they are in.
# Change this path_to_app before doing auto-py-to-exe.
# path_to_app = Path('c:/Users/Tim/Documents/output/pdf_merger')
# path_to_app = Path('A:\working_apps\pdf_merger')
# path_to_app = Path('A:\working_apps\pdf_merger')
# chdir(path_to_app)

information_frame = mf.information_frame
keys_to_clear = ['-FOLDER-', '-INFO-', '-PDF_LIST-', '-RESULT-'] #'-FILENAME-', 
pdf_icon = mf.get_custom_icon()
    
    
def show_message(key: str, message: str, color: str="#e9e8e4") -> None:
    """Update PySimplGUI element to show a message."""
    window[key].update(message, text_color=color)

# declare some sg aliases
B = sg.Button
Frame = sg.Frame
In = sg.Input
T = sg.Text

# Make it whatever you want.
sg.theme('DarkTeal6')
sg.set_options(tooltip_font='Calibri 12')

menu_layout = [
    ['&File', ['&Properties', 'E&xit']],
    ['&Actions', ['&Merge', '&Clear', '&Open', '&Delete']],
    ['&Help', ['&Help', '&About...']]
    ]

# For showing the files that are going to be merged.
multiline_frame = [Frame(layout=
    [
        [sg.Multiline(default_text='', 
                    size=(44, 3),
                    write_only=True,
                    background_color='#204969',
                    justification='c',
                    focus=False,
                    disabled=True,
                    key='-PDF_LIST-')
        ]
    ],
    title='Files to Merge',
    title_location=sg.TITLE_LOCATION_TOP,
    font='Calibri 10',
    pad=((0, 0), (5, 15))
    )
]

# Full layout
layout = [
    [sg.Menu(menu_layout)],
    [T('Merge PDFs')],    
    [sg.HorizontalSeparator(color='dark grey', pad=((0, 0), (5, 15)))],
    [T('Get Info', font=('Calibri', 14, 'bold'))],
    # [T('Filename to save:'), In(size=20, key='-FILENAME-')],
    # [T('Folder to save to:'), In('Folder?', size=20, disabled=True, use_readonly_for_disable=False,                                 
    #     key='-FOLDER-'), sg.FolderBrowse(enable_events=True,)], # Use to pick directory of .pdfs (chdir_booklet).
    [T('Filename to save:  '),
        In(size=20,
        disabled=True,
        use_readonly_for_disable=False,                                 
        key='-FOLDER-'),
        sg.SaveAs(enable_events=True,)], # Use to pick directory of .pdfs (chdir_booklet).
    [sg.HorizontalSeparator(color='dark grey', pad=((0, 0), (20, 15)))],
    information_frame('Information', '-INFO-'),
    multiline_frame,
    information_frame('Result', '-RESULT-'),
    [sg.HorizontalSeparator(color='dark grey', pad=((0, 0), (5, 5)))],
    mf.action_buttons_frame('Actions'),
]

window = sg.Window('PDF merger', layout, icon=pdf_icon, auto_size_buttons=False,
                    default_button_element_size=(10, 1), font='Calibri 14',
                    return_keyboard_events=True, finalize=True)

# key bindings
window.bind("<Alt_L><m>", "Alt-m")
window.bind("<Alt_R><m>", "Alt-m")
MERGE = window['Merge Files']
MERGE.Widget.configure(underline=0)

window.bind("<Alt_L><c>", "Alt-c")
window.bind("<Alt_R><c>", "Alt-c")
CLEAR = window['Clear']
CLEAR.Widget.configure(underline=0)

window.bind('<Alt_L><o>', 'Alt-o')
window.bind('<Alt_R><o>', 'Alt-o')
OPEN = window['-OPEN-']
OPEN.Widget.configure(underline=0)

window.bind("<Alt_L><x>", "Alt-x")
window.bind("<Alt_R><x>", "Alt-x")
EXIT = window['Exit']
EXIT.Widget.configure(underline=1)

while True:  # event Loop
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit', 'Alt-x', 'End:35'):
        break

    if event in ['Merge Files', 'Merge', 'Alt-m']:
        # Catch blank inputs, uses named expression (walrus) assignment.
        merge_path = values['-FOLDER-']
        if not merge_path:
            show_message('-INFO-', 'No folder chosen?', 'yellow')
            
            
            # window['-INFO-'].update(f'Empty input: {empty_input}', text_color='yellow')
        else:
            # Get values from inputs.
            merge_path = Path(merge_path)
            merge_folder = merge_path.parent
            merge_filename = f'{merge_path.name}.pdf'

            chdir(merge_folder)  # Set the working folder to the one with the files to merge.
            window['-INFO-'].update(f'Folder to merge files from and save   {merge_filename}   to is: {merge_folder}', text_color='white')  

            pdf_list = mf.make_file_list(merge_folder, '*.pdf')

            # Catch empty folder (no files with the extension you're looking for)
            if not pdf_list:
                window['-PDF_LIST-'].update(
                    'There are no files in that folder', text_color='yellow1'
                )
            else:
                window['-PDF_LIST-'].update(pdf_list, text_color='white')

            # This lets you see the folder and the files that will be merged.
            confirm_merge = sg.popup_ok_cancel('   Confirm Merge', font=('Calibri', 14), text_color='yellow',
                        no_titlebar=True, grab_anywhere=True, keep_on_top=True, relative_location=(10, 208))
            if confirm_merge == 'Cancel':
                ...
            else:                 
                # Do the magic.
                merged_pdf = mf.merge_pdfs(pdfs=pdf_list, output=merge_filename)

            if success := mf.confirm_file_exists(merge_filename):
                window['-RESULT-'].update(f'Nice! the file - {merge_filename} - was created', text_color='white')              

            else:
                window['-RESULT-'].update('Bummer')
            window['-OPEN-'].update(disabled=False)

    # Click the Clear button to clear inputs.
    if event in ('Clear', 'Alt-c',):
        values.clear()
        for key in keys_to_clear:
            window[key].update('')
        window['-OPEN-'].update(disabled=True)

    # Click the Open button, use the file menu item -Alt, F, O-,
    # or press Alt-O to open file in os default webbrowser.    
    if event in ['-OPEN-', 'Open', 'Alt-o']:
        chdir(merge_folder)
        print(f'Open folder is: {merge_folder}')
        file_to_open = Path(merge_filename).absolute()
        mf.open_file_in_browser(merge_filename)

    # Use the Delete menu item -Alt, A, D-, or press Delete to delete the file.
    if event in ('Delete', 'Delete:46'):
        chdir(merge_folder)
        file_to_delete = Path(merge_filename)
        if Path(file_to_delete).exists():
            mf.delete_file(file_to_delete)
        else:
            sg.Popup(
                'Nothing to delete',
                text_color='yellow',
                font=('Calibri', 14),
                no_titlebar=True,
                keep_on_top=True,
                relative_location=(0, 200),
            )

        if deleted := mf.confirm_file_does_not_exist(file_to_delete):
            window['-RESULT-'].update(f'"{merge_filename}"  deleted', text_color='dark orange')
            window['-INFO-'].update('')
        else: 
            window['-RESULT-'].update(f'{merge_filename} not deleted')                

    # # Use the About menu item -Alt, H, A- or press F2.
    # # Show the about file in new window.
    # if event in ('About...', 'F2:113'):
    #     window.disappear()
    #     chdir(path_to_app)
    #     about_file = Path('Resources\\about.txt')
    #     about = mf.open_text_file(about_file)
    #     mf.open_about_window('About', about)
    #     window.reappear()

    # # Use the Help menu item -Alt, H, H- or press F1.
    # if event in ('Help', 'F1:112'):
    #     chdir(path_to_app)
    #     print(f'Help folder is: {path_to_app}')
    #     help_file = Path('Resources\\help.html')
    #     help = mf.open_file_in_browser(help_file)

window.close()
