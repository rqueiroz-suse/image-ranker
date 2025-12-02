import FreeSimpleGUI as sg

def layout_screen1():
    return [[sg.Text("This is Screen 1")],
            [sg.Button("Go to Screen 2", key="-GOTO2-")]]

def layout_screen2():
    return [[sg.Text("This is Screen 2")],
            [sg.Button("Go to Screen 1", key="-GOTO1-")]]

# Define the full layout with columns for each screen
# Columns are placed in a Frame or directly in the window, initially only one visible
layout = [
    [sg.Column(layout_screen1(), key='-COL1-', visible=True)],
    [sg.Column(layout_screen2(), key='-COL2-', visible=False)]
]

window = sg.Window("Single Window App", layout, finalize=True)

current_layout = '-COL1-'

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == '-GOTO2-':
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)
        current_layout = '-COL2-'
        # You might need to add a window.refresh() here for some configurations/frameworks

    if event == '-GOTO1-':
        window['-COL2-'].update(visible=False)
        window['-COL1-'].update(visible=True)
        current_layout = '-COL1-'
        # You might need to add a window.refresh() here for some configurations/frameworks

window.close()