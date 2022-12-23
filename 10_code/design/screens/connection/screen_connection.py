__all__ = ("ConnectionScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from design import screens_path

with open(
    os.path.join(screens_path, "connection", "screen_connection.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#TODO: rework color, forme radius
class ConnectionScreen(Screen):
    pass