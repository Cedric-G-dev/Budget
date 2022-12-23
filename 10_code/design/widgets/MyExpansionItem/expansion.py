__all__ = ("ExpansionScrollItem",)

import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, DictProperty, NumericProperty, BooleanProperty, ListProperty

from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import OneLineAvatarIconListItem, ILeftBodyTouch

from decimal import Decimal as D

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyExpansionItem", "expansion.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#TODO: Recreate so that there is no creation/deletion of widget upon selection -> use scrolling
#       -> take inspiration from AccountAbstract
#TODO: selection list is working, except that scrolling over it can trigger
#       list item function -> disable or change function call
#class for Recursion Selection

class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    pass


class ListItemWithCheckboxDisplay(OneLineAvatarIconListItem):
    icon = StringProperty()
    item_state = BooleanProperty(False)


class ExpansionScrollItem(BoxLayout):
    text = StringProperty()
    item_icon = StringProperty()
    data_recursion = DictProperty()
    icon_recursion = ListProperty()

    indicator_update = NumericProperty(0)

    expansion_icon = StringProperty('chevron-right')
    expansion_state = BooleanProperty(False)
    scroll_height = NumericProperty(0)

    _margin = '25dp'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._set_expansion_size)
        Clock.schedule_once(self._set_expansion)

    def _set_expansion_size(self, event):
        self.children_height = self.ids.item.height * len(self.data_recursion)

    def _set_expansion(self, event):
        for key, value in self.data_recursion.items():
            if type(value) is dict:
                temp_widget = ExpansionScrollItem(
                    data_recursion = value,
                    icon_recursion = self.icon_recursion[1:],
                    text = key,
                    item_icon = self.icon_recursion[1]
                )
            else:
                temp_widget = ListItemWithCheckboxDisplay(
                    text = key,
                    icon = self.icon_recursion[-1],
                    on_release = self.update_list_dict,
                    item_state = True if value else False)

            self.ids.value_item_box.add_widget(temp_widget)

    def control_expansion(self):
        self.expansion_state = not self.expansion_state
        #THINK ABOUT: is there a need for two paremeters, expanstion_state and scroll_height??
        # if self.scroll_height != 0:
        #     self.scroll_height = 0
        #     self.expansion_icon = 'chevron-right'
        #     self.item_icon = self.item_icon.replace('-outline','')
        #     #close all children expansion
        #     if isinstance(self.ids.value_item_box.children[0], ExpansionScrollItem):
        #         for children in self.ids.value_item_box.children:
        #             children._close_expansion()

        # elif self.scroll_height == 0:
        #     self._open_expansion()
        #     self.expansion_icon = 'chevron-down'
        #     self.item_icon += '-outline'

    def on_expansion_state(self, instance, value):
        if value:
            self.scroll_height = self.children_height
            self.expansion_icon = 'chevron-down'
            self.item_icon += '-outline'
        else:
            self.scroll_height = 0
            self.expansion_icon = 'chevron-right'
            self.item_icon = self.item_icon.replace('-outline','')
            if isinstance(self.ids.value_item_box.children[0], ExpansionScrollItem):
                for children in self.ids.value_item_box.children:
                    children.expansion_state = not children.expansion_state

    def on_scroll_height(self, instance, value):
        if isinstance(self.parent.parent, ExpansionScrollItem):
            if self.scroll_height == 0:
                self.parent.parent.scroll_height -= self.children_height
            else:
                self.parent.parent.scroll_height += self.children_height
        elif isinstance(self.parent.parent, ScrollView):
            if self.scroll_height == 0:
                self.parent.parent.height -= self.children_height
            else:
                self.parent.parent.height += self.children_height                

    def update_list_dict(self, instance):
        instance.item_state = not instance.item_state
        if instance.item_state:
            self.data_recursion[instance.text] = D('0.00')
        else:
            self.data_recursion[instance.text] = False
        self.indicator_update += 1

    def on_data_recursion(self, instance, value):
        #prevent trigger at initialization
        if self.parent is not None:
            if isinstance(self.parent.parent, ExpansionScrollItem):
                self.parent.parent.data_recursion[self.text] = self.data_recursion
                self.parent.parent.indicator_update += 1

