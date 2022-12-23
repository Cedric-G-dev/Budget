__all__ = ("CancelOkButtons","RefillButton")

import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyButton", "button.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#Class for customized snackbar 
class CancelOkButtons(BoxLayout):
    validate = StringProperty()
    cancel = StringProperty()
    validation = ObjectProperty()
    cancellation = ObjectProperty()

    def __init__(self, **kwargs):
        super(BoxLayout, self).__init__(**kwargs)
        
class RefillButton(BoxLayout):
    button_state = BooleanProperty(False)

    def trigger(self):
        self.button_state = not self.button_state
