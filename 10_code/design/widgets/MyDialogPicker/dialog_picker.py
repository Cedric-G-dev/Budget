__all__ = ("MDDialogDate","MDDialogDayOfMonth","MDDialogItemConfiration","MDDialogFilter","MDDialogResearch","ListItemResearch")

import os
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ColorProperty, DictProperty
from kivy.metrics import dp

from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.list import OneLineAvatarIconListItem, OneLineListItem
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.color_definitions import colors, palette


import calendar
from dateutil.relativedelta import relativedelta
from datetime import date

from design import widgets_path



with open(
    os.path.join(widgets_path, "MyDialogPicker", "dialog_picker.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#global parameter
Dialog_radius = 20

#class for MMDialogResearch
class ListItemResearch(OneLineListItem):
    #divider = None
    _height = dp(50)
    _txt_top_pad = dp(15)
    _txt_bot_pad = dp(15)

    def update_input(self):
        self.parent.parent.parent.ids.input.text = self.text


class ResearchDialog(BoxLayout):
    user_input = StringProperty()
    search_hint = StringProperty()

    def __init__(self, user_input, search_hint, **kwargs):
        super(ResearchDialog, self).__init__(**kwargs)
        self.user_input = user_input
        self.search_hint = search_hint


class MDDialogResearch(MDDialog):
    def __init__(self, user_input, search_hint, btn_text_cancel, btn_text_ok, **kwargs):
        self.type = 'custom'
        self.content_cls = ResearchDialog(user_input, search_hint)
        self.buttons = [
                MDRaisedButton(
                    text = btn_text_cancel,
                    on_press = self.filter_cancel
                ),
                MDRaisedButton(
                    text = btn_text_ok,
                    on_press = self.filter_ok
                )
            ]
        
        super(MDDialogResearch, self).__init__(**kwargs)
        self.user_input = user_input
        self.ids.container.padding = [dp(25),dp(0),dp(8),dp(0)]

    def filter_ok(self, *args):
        self.user_input = self.content_cls.ids.input.text
        self.content_cls.ids.suggestion_list.clear_widgets()
        self.dismiss()

    def filter_cancel(self, *args):
        self.content_cls.ids.input.text = self.user_input
        self.content_cls.ids.suggestion_list.clear_widgets()
        self.dismiss()


#class for MDDialogFilter
class ListItemFilter(OneLineAvatarIconListItem):
    divider = None
    _height = dp(50)
    _txt_top_pad = dp(15)
    _txt_bot_pad = dp(15)
    _txt_right_pad = dp(0)

    def set_list_switch(self):
        list_member_state = [member_state.ids.check.active for member_state in self.parent.children]

        if False not in list_member_state:
            self.parent.parent.parent.ids.filter_checkbox.active = True
        else:
            self.parent.parent.parent.ids.filter_checkbox.active = False

    def list_click_set_checkbox(self, instance_check):
        instance_check.active = not instance_check.active

    def checkbox_active_set_checkbox(self, instance):
        if instance.parent.parent.parent:
            self.parent.parent.parent.content_dict[self.text] = instance.active
            self.set_list_switch()



class FilterDialog(BoxLayout):
    content_dict = DictProperty()

    def __init__(self, content_dict, filter_name, **kwargs):
        super(FilterDialog, self).__init__(**kwargs)
        self.content_dict = content_dict
        self.ids.filter_name.text = filter_name
        self.ids.filter_checkbox.active = True

        for content_name, content_state in self.content_dict.items():
            list_member = ListItemFilter(text = content_name)
            list_member.ids.check.active = content_state
            self.ids.filter_list.add_widget(list_member)
            if content_state == False:
                self.ids.filter_checkbox.active = False

    def on_content_dict(self, instance, value):
        for list_member in self.ids.filter_list.children:
            list_member.ids.check.active = self.content_dict[list_member.text]


    def filter_checkbox(self):
        checkbox_state = self.ids.filter_checkbox.active
        for list_member in self.ids.filter_list.children:
            list_member.ids.check.active = checkbox_state

#TODO: check_item was deemed useless in HomeScreen, wait and see if it is true for all screen
# before deleting
class MDDialogFilter(MDDialog):
    content_dict = DictProperty()
    external_ok_action = NumericProperty()

    def __init__(self, content_dict, filter_name, btn_text_cancel, btn_text_ok, **kwargs):
        self.type = 'custom'
        self.content_cls = FilterDialog(content_dict, filter_name)
        self.buttons = [
                MDRaisedButton(
                    text = btn_text_cancel,
                    on_press = self.filter_cancel
                ),
                MDRaisedButton(
                    text = btn_text_ok,
                    on_press = self.filter_ok
                )
            ]
        super(MDDialogFilter, self).__init__(**kwargs)
        self.content_dict = content_dict
        self.ids.container.padding = [dp(10),dp(0),dp(8),dp(0)]

    def on_content_dict(self, instance, value):
        self.content_cls.content_dict = self.content_dict

    def filter_ok(self, *args):
        # checked_item = []
        # item_list = self.content_cls.ids.filter_list.children

        # for item in item_list:
        #     self.content_dict[item.text] = item.ids.check.active
            # if item.ids.check.active == True:
            #     checked_item.append(item.text)
        self.content_dict = self.content_cls.content_dict
        self.external_ok_action += 1
        self.dismiss()

    def filter_cancel(self, *args):
        # checked_item = []
        # item_list = self.content_cls.ids.filter_list.children

        # for item in item_list:
        #     item.ids.check.active = self.content_dict[item.text]

        self.content_cls.content_dict = self.content_dict

        self.dismiss()


#class for item selection in list - confirmation MDDialog
#TODO: create confirmation dialog
class ItemConfirmDiag(OneLineAvatarIconListItem):
    divider = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._txt_right_pad = dp(5)

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

        self.update_choice()

    def update_choice(self):
        self.parent.parent.parent.parent.choice = self.text


class MDDialogItemConfiration(MDDialog):
    choice = StringProperty()

    def __init__(self, choice_list, choice,**kwargs):
        #MDDialog variable
        self.choice = choice
        #definition of MDDialog parameter
        self.type = 'confirmation'
        self.items = [
            ItemConfirmDiag(text = item) for item in choice_list
        ]
        super().__init__(**kwargs)

        #initialize if choice != None
        if choice:
            for item in self.items:
                if item.text == self.choice:
                    item.ids.check.active = True
                    break

    def on_choice(self, instance, value):
        self.dismiss()


#Dialog button
class DialogButton(Button, ThemableBehavior):
    text_font_size = 13
    size_ratio = .8
    radius = [5] * 4

    no_bg_color = [1, 1, 1, 0]


#class for MDDialogDate
class DateButton(DialogButton):
    def __init__(self, btn_text, current_month_boolean, input_date_month,
        input_date_year, pick_index,**kwargs):
        super(DialogButton, self).__init__(**kwargs)

        if pick_index == 1:
            self.canvas.children[0].children[0].rgba = self.theme_cls.primary_color
            self.color = self.theme_cls.opposite_text_color        
        if current_month_boolean == 0:
            self.color = self.theme_cls.secondary_text_color

        self.text = btn_text
        self.date_month = input_date_month
        self.date_year = input_date_year


class DateDialog(MDBoxLayout, ThemableBehavior):
    month_page = StringProperty('')

    def __init__(self, input_date, **kwargs):
        super(MDBoxLayout, self).__init__(**kwargs)
        self.grid_date = input_date
        self.displayed_month = input_date

        for i_day in calendar.day_name:
            day_of_the_week = Label(
                text = i_day[:3].upper(),
                font_size = '10dp',
                color =  self.theme_cls.primary_dark,
                size_hint_y = 0.5,
                pos_hint = {'center_x' : 0.5}                
            )
            self.ids.dategrid.add_widget(day_of_the_week)
 
        self.construct_date_grid(self.displayed_month)
  
    def construct_date_grid(self, month_to_display):
        self.month_page = self.displayed_month.strftime('%B - %Y').capitalize()

        previous_month = month_to_display - relativedelta(months = 1)
        next_month = month_to_display + relativedelta(months = 1)
        
        month_info = calendar.monthrange(
            month_to_display.year,
            month_to_display.month)

        previous_month_info = calendar.monthrange(
            previous_month.year,
            previous_month.month)

        if len(self.ids.dategrid.children) > 7 :
            for i in range(1, 43):
                self.ids.dategrid.remove_widget(self.ids['day_' + str(i)])

        index_calendar = 0
        for i in range(month_info[0]):
            index = month_info[0] - 1 - i
            day_number = previous_month_info[1] - index
            if date(previous_month.year, previous_month.month, day_number) == self.grid_date :
                text_color = 1
                pick_index = 1
            else :
                text_color = 0
                pick_index = 0

            previous_month_day = DateButton(
                str(day_number),
                text_color,
                previous_month.month,
                previous_month.year,
                pick_index,
                on_press = self.pick_date
            )
            self.ids.dategrid.add_widget(previous_month_day)            
            self.ids['day_' + str(index_calendar + 1)] = previous_month_day
            index_calendar += 1

        for i in range(1, month_info[1]+1):
            if date(month_to_display.year, month_to_display.month, i) == self.grid_date :
                pick_index = 1
            else:
                pick_index = 0              

            current_month_day = DateButton(
                str(i),
                1,
                month_to_display.month,
                month_to_display.year,
                pick_index,
                on_press = self.pick_date
            )

            self.ids.dategrid.add_widget(current_month_day)
            self.ids['day_' + str(index_calendar + 1)] = current_month_day
            index_calendar += 1         
        
        for i in range(1,42 - index_calendar + 1):
            if date(next_month.year, next_month.month, i) == self.grid_date :
                text_color = 1
                pick_index = 1
            else :
                text_color = 0
                pick_index = 0

            next_month_day = DateButton(
                str(i),
                text_color,
                next_month.month,
                next_month.year,
                pick_index,
                on_press = self.pick_date
            )
            self.ids.dategrid.add_widget(next_month_day)
            self.ids['day_' + str(index_calendar + i)] = next_month_day        

    def go_to_previous_month(self):
        self.displayed_month = self.displayed_month - relativedelta(months = 1)
        self.construct_date_grid(self.displayed_month)

    def go_to_next_month(self):
        self.displayed_month = self.displayed_month + relativedelta(months = 1)
        self.construct_date_grid(self.displayed_month)

    def pick_yesterday(self):
        picked_date = date.today() - relativedelta(days = 1)
        self.parent.parent.parent.dialog_date = picked_date
        self.grid_date = picked_date
        self.displayed_month = picked_date
        self.construct_date_grid(self.displayed_month)        
        self.parent.parent.parent.dismiss()

    def pick_before_yesterday(self):
        picked_date = date.today() - relativedelta(days = 2)
        self.grid_date = picked_date
        self.displayed_month = picked_date
        self.construct_date_grid(self.displayed_month)
        self.parent.parent.parent.dialog_date = picked_date
        self.parent.parent.parent.dismiss()

    def pick_date(self, instance):
        picked_date = date(instance.date_year, instance.date_month, int(instance.text))
        self.grid_date = picked_date
        self.displayed_month = picked_date
        self.construct_date_grid(self.displayed_month)
        self.parent.parent.parent.dialog_date = picked_date
        self.parent.parent.parent.dismiss()


class MDDialogDate(MDDialog):
    def __init__(self, input_date, **kwargs):
        #MDDialog variable
        self.dialog_date = input_date        
        #definition of MDDialog parameter
        self.type = 'custom'
        self.content_cls = DateDialog(self.dialog_date)
        super(MDDialogDate, self).__init__(**kwargs)
        #update MDialog graphic parameter
        self.ids.container.padding = [dp(16),dp(0),dp(0),dp(10)]
        self.radius = [Dialog_radius] * 4

#class for MDDialogDayOfMonth
#TO USE : bind function on dismiss for dialog_day variable
class DayButton(DialogButton):
    pick_state = BooleanProperty(False)

    def __init__(self, btn_text, pick_index,**kwargs):
        super(DialogButton, self).__init__(**kwargs)
        self.pick_state = pick_index
        self.text = btn_text
    
    def on_pick_state(self, instance, value):
        if self.pick_state:
            self.canvas.children[0].children[0].rgba = self.theme_cls.primary_color
            self.color = self.theme_cls.opposite_text_color
        else:
            self.canvas.children[0].children[0].rgba = DialogButton.no_bg_color
            self.color = self.theme_cls.text_color


class DayOfMonthDialog(GridLayout):
    chosen_day = NumericProperty()

    def __init__(self, chosen_day, **kwargs):
        super().__init__(**kwargs)
        self.chosen_day = chosen_day
        self.previous_chosen_day = chosen_day
        
        for day_number in range(1, 31):
            day = DayButton(
                str(day_number),
                True if day_number == self.chosen_day else False,
                on_press = self.pick_day)

            self.add_widget(day)

    def pick_day(self, instance):
        self.previous_chosen_day = self.chosen_day
        self.chosen_day = int(instance.text)

    #function for after initialization
    def on_chosen_day(self, instance, value):
        if self.parent:
            self.parent.parent.parent.dialog_day = self.chosen_day
            self.update_grid()

    def update_grid(self):
        if self.previous_chosen_day != 0:
            self.children[30 - self.previous_chosen_day].pick_state = False
        if self.chosen_day != 0:
            self.children[30 - self.chosen_day].pick_state = True


class MDDialogDayOfMonth(MDDialog):
    dialog_day = NumericProperty()

    def __init__(self, title, input_day, **kwargs):
        #MDDialog variable
        self.title = title
        self.dialog_day = input_day
        #definition of MDDialog parameter
        self.type = 'custom'
        self.content_cls = DayOfMonthDialog(self.dialog_day)
        super(MDDialogDayOfMonth, self).__init__(**kwargs)
        #update MDialog graphic parameter
        self.ids.container.padding = [dp(16),dp(24),dp(0),dp(10)]
        self.radius = [Dialog_radius] * 4

    #function close dialog and/or to update dialog from the outside
    def on_dialog_day(self, instance, value):
        if self.dialog_day != self.content_cls.chosen_day:
            self.content_cls.previous_chosen_day = self.content_cls.chosen_day
            self.content_cls.chosen_day = self.dialog_day
        
        self.dismiss()

#class for MDDialogColorPicker
#HOW TO USE:
#input/output: color [x, y ,z]

class ColorPickerDialog(GridLayout):
    basic_hue = '500'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for palette_color in palette:
            widget = MDIconButton(
                    icon =  'checkbox-blank',
                    theme_text_color ='Custom',
                    text_color = colors[palette_color][self.basic_hue]
                )
            widget.bind(on_release = self.select_color)
            self.add_widget(widget)

    def select_color(self, instance):
        self.parent.parent.parent.color_pick = instance.text_color
        self.parent.parent.parent.dismiss()


class MDDialogColorPicker(MDDialog):
    color_pick = ColorProperty()

    def __init__(self, input_color, **kwargs):
        self.type = 'custom'
        self.content_cls = ColorPickerDialog()
        super(MDDialogColorPicker, self).__init__(**kwargs)
        self.color_pick = input_color
        self.ids.container.padding = [dp(25),dp(0),dp(8),dp(0)]