__all__ = ("AffectationDialog",)

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.lang import Builder

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyDialogAffectation", "dialog_affectation.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


class AffectationItem(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    data_id = NumericProperty()
    data_designation = StringProperty()
    data_amount = NumericProperty()
    data_budget = StringProperty()

    font_style = StringProperty('Subtitle2')
    _horizontal_padding = NumericProperty('10dp')
    _vertical_padding = NumericProperty('0dp')
    _spacing = NumericProperty('2dp')
    _roundness = NumericProperty('10dp')

    def update_state(self):
        self.ids.check.active = not self.ids.check.active

#HOW TO USE:
#1- input: 
#   data :  dictionnary with keys 'id', 'designation', 'amount'
#   budget : str with the working budget

class AffectationDialog(BoxLayout):
    budget = StringProperty()
    data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._set_expense_list)

    def _set_expense_list(self, event):
        for item in self.data:
            temp_widget = AffectationItem(
                data_id = item['id'],
                data_designation = item['designation'],
                data_amount = item['amount'],
                data_budget = item['budget']
            )

            if item['budget'] == self.budget:
                temp_widget.ids.check.active = True

            self.ids.list.add_widget(temp_widget)

