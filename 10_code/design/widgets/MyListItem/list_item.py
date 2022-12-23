__all__ = ("LabelAmountListItem, BillLine, ListInOutItem")

import os
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ColorProperty
from kivy.animation import Animation

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior

from decimal import Decimal as D

from design import widgets_path


with open(
    os.path.join(widgets_path, "MyListItem", "list_item.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

class LabelAmountListItem(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    designation = StringProperty()
    amount = NumericProperty()
    
    font_style = StringProperty('Subtitle2')
    _horizontal_padding = NumericProperty('10dp')
    _vertical_padding = NumericProperty('0dp')
    _spacing = NumericProperty('2dp')
    _roundness = NumericProperty('10dp')

    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)


class BillLine(BoxLayout):
    budget = StringProperty()
    str_amount = StringProperty()
    state = BooleanProperty(True)

    def __init__(self, account, budget, amount, state, **kwargs):
        super(BoxLayout, self).__init__(**kwargs)
        self.budget = budget
        self.account = account
        self.amount = amount
        self.state = state
        if amount == D('0'):
            self.str_amount = ''
        else:
            self.str_amount = str(self.amount)

#Class for in-out line
#TODO blurry text for scrolling label
#TODO connect to other screen when released
#TODO think about transaction type to give information about intern ticket 
#       -> In/Out = +/-, but intern...what to do?
class ListInOutItem(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    ticket_id = NumericProperty()
    date_text = StringProperty()
    recipient_text = StringProperty()
    reason_text = StringProperty()
    ticket_state = NumericProperty()
    amount = NumericProperty()
    intern = BooleanProperty()

    main_budget = StringProperty()
    budget_color = ColorProperty()#StringProperty('blue')
    
    font_style = StringProperty('Subtitle2')
    _horizontal_padding = NumericProperty('10dp')
    _vertical_padding = NumericProperty('0dp')
    _spacing = NumericProperty('2dp')
    _roundness = NumericProperty('10dp')

    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)

    scroll_position = NumericProperty()

    def on_scroll_position(self, instance, scroll_x_value):
        if self.ids:          
            anim = Animation(
                scroll_x = scroll_x_value,
                duration = 1,
                t = 'linear'
            )
            anim.start(self.ids.scroll)
