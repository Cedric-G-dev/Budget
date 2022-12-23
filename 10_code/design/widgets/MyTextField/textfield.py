__all__ = ("MyTextField",)

import os
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyTextField", "textfield.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class MyTextField(MDTextField):
    pass

