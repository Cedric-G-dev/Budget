__all__ = ("MDDialogNote",)

import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.metrics import dp

from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyDialogNote", "dialog_note.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class MDDialogNote(MDDialog):
    def __init__(self, title, note, btn_text_cancel, btn_text_ok, **kwargs):
        self.title = title
        self.type = 'custom'
        self.note = note
        self.content_cls = NoteDialog(note)
        self.buttons = [
            MDRaisedButton(
                text = btn_text_cancel,
                on_press = self.cancel_note
            ),
            MDRaisedButton(
                text = btn_text_ok,
                on_press = self.ok_note
            )
        ]        
        super().__init__(**kwargs)

        self.ids.container.padding = [dp(20),dp(24),dp(8),dp(0)]

    def cancel_note(self, event):
        self.content_cls.ids.note.text = self.note
        self.dismiss()

    def ok_note(self, event):
        self.note = self.content_cls.user_input
        self.dismiss()

    def on_dismiss(self):
        self.content_cls.ids.note.text = self.note

#class for MDDialog custom - note
class NoteDialog(BoxLayout):
    user_input = StringProperty()

    def __init__(self, input_note, **kwargs):
        super().__init__(**kwargs)
        self.user_input = input_note
    
    def update_input(self, instance):
        self.user_input = instance.text