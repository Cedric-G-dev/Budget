__all__ = ("NavDrawer",)

import os
from kivy.lang import Builder

from kivymd.uix.navigationdrawer import MDNavigationDrawerMenu

from design import widgets_path

with open(
    os.path.join(widgets_path, "drawer", "drawer.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

class NavDrawer(MDNavigationDrawerMenu):
    pass