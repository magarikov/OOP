
from curses_adapter import CursesAdapter
from model import TextModel
from view import TextView
from controller import Controller
import sys


if __name__ == "__main__":

    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    ui = CursesAdapter()
try:
    ui.init()
    model = TextModel(filename)
    model.load_file(filename)

    view = TextView(ui)

    ctrl = Controller(model, view, ui)
    ctrl.run()
finally:
    ui.shutdown()
