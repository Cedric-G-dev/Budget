__all__ = ("MDDialogRefund",)

import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from kivymd.uix.dialog import MDDialog

from ...widget_functions import number_input_control

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyDialogRefund", "dialog_refund.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#class for refund def
class MDDialogRefund(MDDialog):
    def __init__(self, btn_delete, btn_validate, **kwargs):
        self.type = 'custom'
        self.content_cls = RefundDialog()
        self.buttons = [btn_delete, btn_validate]        
        super().__init__(**kwargs)

  
        self.ids.container.padding = [dp(0),dp(0),dp(10),dp(10)]
        self.ids.spacer_top_box.padding = [dp(10),dp(0),dp(0),dp(0)]      


class RefundDialog(BoxLayout):

    def add_refill(self):
        line = RefillLine()
        line.ids.delete.bind(on_press = self.delete_refill)
        self.ids.stack.add_widget(line)
    
    def delete_refill(self, instance):
        self.ids.stack.remove_widget(instance.parent)


class RefillLine(BoxLayout):
    who_helper_text = 'Qui ?'
    howmany_helper_text = 'Combien ?'

    def check_amount(self, instance):
        number_input_control(instance)

    def check_reason(self, instance):
        if instance.text != '':
            instance.text = instance.text.lower()