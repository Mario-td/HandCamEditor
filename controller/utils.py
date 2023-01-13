"""Utils module"""


# pylint: disable=W0640
def connect_button_to_slot(button, func, *args):
    """Connects buttons to slot functions"""
    if args:
        for arg in args:
            button.clicked.connect(lambda: func(arg))
        return
    button.clicked.connect(lambda: func())
