__all__ = ("MessageSnackbar",)

import os
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.snackbar import BaseSnackbar

from design import widgets_path


with open(
    os.path.join(widgets_path, "MySnackbar", "snackbar.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#Class for customized snackbar 
class MessageSnackbar(BaseSnackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = "15sp"
