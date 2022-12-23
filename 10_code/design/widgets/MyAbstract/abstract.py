
__all__ = ("BudgetAbstract","AccountAbstract","BudgetExpensesExpansion")

import os
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, NumericProperty, ColorProperty, BooleanProperty, DictProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior

from ..MyListItem import LabelAmountListItem
from ..MyGraph import ConsumptionGraphButton
from design import widgets_path

from kivy.factory import Factory
register = Factory.register
register("ConsumptionGraphButton", module="design.widgets.MyGraph")


with open(
    os.path.join(widgets_path, "MyAbstract", "abstract.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#TODO: revision of line indicating status of budget (lower part), make it start further,
#       at the end of the budget label 
#TODO: create parent class for budget/account present class
#account_status refers to account_consumption ratio in regard to criteria
#Class for budget home
class BudgetAbstract(BoxLayout):
    id = NumericProperty()
    name = StringProperty()
    budget_amount = NumericProperty()
    month_expenditure = NumericProperty()
    month_prevision = NumericProperty()
    budget_cap = NumericProperty()
    end_of_last_month_budget_amount = NumericProperty()

    id_account = NumericProperty()
    account_name = StringProperty()
    account_status = NumericProperty()

    danger_criteria =  NumericProperty(0.7)
    danger_color = get_color_from_hex('#E65100')
    critical_criteria =  NumericProperty(0.9)
    critical_color = get_color_from_hex('#B71C1C')
    safe_color = get_color_from_hex('#1B5E20')

    graph_button = NumericProperty()
    list_button_1 = NumericProperty()
    list_button_2 = NumericProperty()    

    expansion = BooleanProperty(False)
    _expansion_state = BooleanProperty(False)

    _roundness = NumericProperty('10dp')
    _thickness = NumericProperty('2dp')
    _border_color = get_color_from_hex('#8defb4')#'#009074')
    _state_indicator_line_thickness = NumericProperty('1.5dp')

    _scroll_padding = NumericProperty('10dp')
    _scroll_spacing = NumericProperty('10dp')

    opening_time = 1
    budget_consumption_ratio = 0

    def __init__(self, budget_id, budget_designation, budget_amount, budget_month_expenditure,
        budget_month_prevision, budget_cap, bugdet_last_month,
        account_id, account_name, account_status, **kwargs):
        super().__init__(**kwargs)
        self.id = budget_id
        self.name = budget_designation
        self.budget_amount = float(budget_amount)
        self.month_expenditure = float(budget_month_expenditure)
        self.month_prevision = float(budget_month_prevision)
        self.budget_cap = float(budget_cap)
        self.end_of_last_month_budget_amount = float(bugdet_last_month)  
        self.id_account = account_id
        self.account_name = account_name
        self.account_status = account_status

        if self.month_prevision != 0:
            self.budget_consumption_ratio = self.month_expenditure / self.month_prevision
            
        self._set_budget_state()
        self._set_consumption_graph()
        self._set_expansion_open()

    def _set_budget_state(self):
        if self.budget_consumption_ratio > self.critical_criteria:
            self.ids.indication.budget_state_indicator = 2
            self.budget_status_color = self.critical_color
        elif self.budget_consumption_ratio > self.danger_criteria:
            self.ids.indication.budget_state_indicator = 1
            self.budget_status_color = self.danger_color
        else:
            self.ids.indication.budget_state_indicator = 0
            self.budget_status_color = self.safe_color
        
        self.set_budget_status_color(self.budget_status_color)

    def _set_consumption_graph(self):
        self.graph = ConsumptionGraphButton(
            month_expenditure = self.month_expenditure,
            month_prevision = self.month_prevision,
            danger_limit = self.danger_criteria,
            critical_limit = self.critical_criteria
        )
        self.graph.bind(on_release = self.graph_buton_action)    
        self.ids.box.add_widget(self.graph, index = 1)

    def on_expansion(self, instance, bool):
        self.ids.indication.abstract_state = not self.ids.indication.abstract_state
        self.graph.display = not self.graph.display

    def animation_pending(self, animation, instance):
        self._expansion_state = not self._expansion_state

    def _set_expansion_open(self):
        self.anim_expansion = Animation(
            height = 2 * self._scroll_padding + self.graph._graph_size,
            duration = self.opening_time,
            t = 'out_circ'
        )
        self.anim_expansion.bind(on_start = self.animation_pending)
        self.anim_expansion.bind(on_complete = self.animation_pending)

    def set_budget_status_color(self, status_color):
        self.canvas.children[6].rgba = status_color

    def expand(self):
        if self.expansion :
            if self._expansion_state:
                self.anim_expansion.stop(self.ids.scroll)
            self.ids.scroll.height = 0
            self.set_budget_status_color(self.budget_status_color)
        else:
            self.anim_expansion.start(self.ids.scroll)
            self.set_budget_status_color([0, 0, 0, 0])

        self.expansion = not self.expansion

    def graph_buton_action(self, event):
        self.graph_button += 1

    def list_buton_action_1(self):
       self.list_button_1 += 1

    def list_buton_action_2(self):
        self.list_button_2 += 1


class BudgetIndication(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    name = StringProperty()
    budget_amount = NumericProperty()
    budget_cap_state = BooleanProperty(False)
    
    budget_state_indicator = NumericProperty()
    abstract_state = BooleanProperty(False)

    _left_padding = NumericProperty('10dp')
    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)


class ListBudgetReviewItem(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    icon = StringProperty()
    icon_color = ColorProperty()
    item_list_text = StringProperty()
    
    _horizontal_padding = NumericProperty('5dp')
    _vertical_padding = NumericProperty('0dp')
    _spacing = NumericProperty('5dp')

    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)


#Class for account home 
#TODO: check spacing between bank amount and 1st icon
#TODO: check when expanding, black circle
#TODO: transform graph into button to go to linked budget (sorted budget page)

class AccountAbstract(BoxLayout):
    id = NumericProperty()
    name = StringProperty()
    bank_amount = NumericProperty()
    real_amount = NumericProperty()
    month_expenditure = NumericProperty()
    month_prevision = NumericProperty()

    danger_criteria =  NumericProperty(0.7)
    critical_criteria =  NumericProperty(0.9)

    graph_button = NumericProperty()
    list_button_1 = NumericProperty()
    list_button_2 = NumericProperty()

    expansion = BooleanProperty(False)
    _expansion_state = BooleanProperty(False)

    _roundness = NumericProperty('10dp')
    _thickness = NumericProperty('2dp')

    _scroll_padding = NumericProperty('10dp')
    _scroll_spacing = NumericProperty('10dp')

    opening_time = 1
    account_consumption_ratio = 0

    def __init__(self, account_id, account_designation, account_bank_amount, account_real_amount,
        account_month_expenditure, account_month_prevision, **kwargs):
        super().__init__(**kwargs)
        self.id = account_id
        self.name = account_designation
        self.bank_amount = float(account_bank_amount)
        self.real_amount = float(account_real_amount)
        self.month_expenditure = float(account_month_expenditure)
        self.month_prevision = float(account_month_prevision)

        if self.month_prevision != 0:
            self.account_consumption_ratio = self.month_expenditure / self.month_prevision

        self._set_up_to_date_indication()
        self._set_state_indication()
        self._set_consumption_graph()
        self._set_expansion_open()

    def _set_up_to_date_indication(self):
        if self.real_amount != self.bank_amount:
            self.ids.indication.pending_ticket_state = False
        else:
            self.ids.indication.pending_ticket_state = True

    def _set_state_indication(self):
        if self.account_consumption_ratio > self.critical_criteria:
            self.ids.indication.account_state_indicator = 2
        elif self.account_consumption_ratio > self.danger_criteria:
            self.ids.indication.account_state_indicator = 1
        else:
            self.ids.indication.account_state_indicator = 0

    def _set_consumption_graph(self):
        self.graph = ConsumptionGraphButton(
            month_expenditure = self.month_expenditure,
            month_prevision = self.month_prevision,
            danger_limit = self.danger_criteria,
            critical_limit = self.critical_criteria
        )
        self.graph.bind(on_release = self.graph_buton_action)    
        self.ids.box.add_widget(self.graph, index = 1)

    def on_expansion(self, instance, bool):
        self.ids.indication.abstract_state = not self.ids.indication.abstract_state
        self.graph.display = not self.graph.display

    def animation_pending(self, animation, instance):
        self._expansion_state = not self._expansion_state

    def _set_expansion_open(self):
        self.anim_expansion = Animation(
            height = 2 * self._scroll_padding + self.graph._graph_size,
            duration = self.opening_time,
            t = 'out_circ'
        )
        self.anim_expansion.bind(on_start = self.animation_pending)
        self.anim_expansion.bind(on_complete = self.animation_pending)

    def expand(self):
        if self.expansion :
            if self._expansion_state:
                self.anim_expansion.stop(self.ids.scroll)
            self.ids.scroll.height = 0
        else:
            self.anim_expansion.start(self.ids.scroll)

        self.expansion = not self.expansion 

    def graph_buton_action(self, instance):
        self.graph_button += 1

    def list_buton_action_1(self):
        self.list_button_1 += 1

    def list_buton_action_2(self):
        self.list_button_2 += 1


class AccountIndication(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    name = StringProperty()
    bank_amount = NumericProperty()

    pending_ticket = StringProperty('progress-clock')
    pending_ticket_state = BooleanProperty(False)

    account_state = StringProperty('alert-outline')
    account_state_indicator = NumericProperty()

    abstract_state = BooleanProperty(False)

    _left_padding = NumericProperty('10dp')

    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)    


class ListAccoutReviewItem(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    status_icon = StringProperty()
    amount_text = StringProperty()
    
    _horizontal_padding = NumericProperty('10dp')
    _vertical_padding = NumericProperty('0dp')
    _spacing = NumericProperty('5dp')

    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)

#class for budgetline
class BudgetItem(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior, MDFloatLayout):
    color = ColorProperty()
    designation = StringProperty()
    amount = NumericProperty()
    
    font_style = StringProperty('Subtitle2')
    _horizontal_padding = NumericProperty('10dp')
    _vertical_padding = NumericProperty('0dp')
    _spacing = NumericProperty('2dp')
    _roundness = NumericProperty('10dp')

    _ripple_alpha = NumericProperty(0.2)
    _ripple_duration_in_fast = NumericProperty(0.2)


class BudgetExpensesExpansion(BoxLayout):
    budget_designation = StringProperty()
    budget_dict = DictProperty()

    expansion_state = BooleanProperty(False)
    scroll_height = NumericProperty(0)

    _list_left_padding = NumericProperty('25dp')
    _list_right_padding = NumericProperty('10dp')
    _list_vertical_padding = NumericProperty('10dp')

    _list_spacing = NumericProperty('5dp')

    _color_margin = NumericProperty('10dp')
    _color_thickness = NumericProperty('3dp')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._set_expense_item)

    def _set_expense_item(self, event):
        for expense, value in self.budget_dict['expense'].items():
            expense_item = LabelAmountListItem(
                designation = expense,
                amount = value
            )
            expense_item.bind(on_release = self.go_to_expense)
            self.ids.list_box.add_widget(expense_item)

    def go_to_expense(self, instance):
        print('go to clicked expense')

    def on_expansion_state(self, instance, value):
        if value:
            self.scroll_height = self.ids.box.height
        else:
            self.scroll_height = 0

