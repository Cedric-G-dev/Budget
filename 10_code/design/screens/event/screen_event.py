__all__ = ("EventScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, DictProperty

from kivymd.uix.dialog import MDDialog

from design.widgets.MyDialogPicker import MDDialogDayOfMonth
from design.widgets.MyDialogNote import MDDialogNote

from functools import partial
from decimal import Decimal as D

from design.widget_functions import number_input_control

from design import screens_path
import design.config as conf


with open(
    os.path.join(screens_path, "event", "screen_event.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#TODO: amount integer, think with D('XX.YY') definition
#TODO stay with architecture Label/screen variable/object variable
#       create function to update both when no ditinction between vairbale needed
#       e.g. amount
#TODO: create automatic ticket if date defined on the date
#TODO: HOT, create event type, input ,ouput or intern
#TODO: HOT, when intern type, defined the input/output budgets
class EventScreen(Screen):
    expense_label = StringProperty()
    budget_label = StringProperty()
    amount_label = StringProperty()
    payment_day_label = StringProperty()
    date_selector = BooleanProperty(False)

    designation_label_empty = ''
    budget_label_empty = ''
    payment_day_label_empty = 'Le __ du mois'

    expense_designation = StringProperty()
    expense_budget = StringProperty()
    expense_string_amount = StringProperty()
    expense_note = StringProperty()
    expense_payment_day = NumericProperty()

    # initialize id = 0 for new ticket
    input_expense = DictProperty({
        'id': 1,
        'designation': 'Course',
        'budget': 'Charges',
        'amount': D('250.00'),
        'note': 'test note',
        'payment_day': 10
    })

    introduction_separator = 'Dépense mensuelle :'
    date_separator = 'Définir une date de prélèvement'
    date_separator_color = 't'
    expense_name_hint = 'Dépense :'
    expense_label_lenght_limit = 21
    expense_monthly_amount_hint = 'Coût mesuel :'

    note_dialog = None
    expense_day_picker = None
    note_dialog_title = 'Note :'

    error_name_already_exist = 'le nom de la dépense existe déjà !'
    expense_designation_too_long = 'le nom de la dépense est trop long ({}/21) !'
    error_amount = 'coût nul ou négatif !'

    ok_button = 'OK'
    cancel_button = 'Annuler'


    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self._set_screen_variable()
        Clock.schedule_once(self._self_date_selector)

    def _set_screen_variable(self):
        #set expense screen variable
        self.expense_designation = self.input_expense['designation']
        self.expense_budget = self.input_expense['budget']
        self.expense_string_amount = str(self.input_expense['amount'])
        self.expense_note = self.input_expense['note']
        self.expense_payment_day = self.input_expense['payment_day']

        #set label
        if self.input_expense['id']:
            self.expense_label = self.expense_designation
            self.budget_label = self.expense_budget
            self.amount_label = self.expense_string_amount
            self.payment_day_label = self.payment_day_label_empty.replace('__', str(self.expense_payment_day))
        else:
            self.expense_label = self.designation_label_empty
            self.budget_label = self.budget_label_empty
            self.amount_label = ''
            self.payment_day_label = self.payment_day_label_empty

    def _self_date_selector(self, interval):
        self.date_selector = True if self.expense_payment_day > 0 else False

    def on_date_selector(self, instance, value):
        if self.date_selector:
            self.ids.date_selection_switch.active = True
            self.ids.date_scroll.height = self.ids.abstract.height
        else:
            self.ids.date_selection_switch.active = False
            self.ids.date_scroll.height = 0
            self.expense_payment_day = 0

    #TODO: when value inserted at the end of the string, no change of text ...
    def return_designation(self, instance):
        if instance.focus is False:
            if len(instance.text) > self.expense_label_lenght_limit:
                self.show_alert(self.expense_designation_too_long.format(len(instance.text)))
                self.expense_label = instance.text[0:self.expense_label_lenght_limit]
                Clock.schedule_once(partial(self.truncate_designation, instance))
            else:
                self.expense_label = instance.text
                self.expense_designation = instance.text

    def truncate_designation(self, instance, interval):
        instance.cursor = (0, 0)

    def show_note_dialog(self):
        if not self.note_dialog:
            self.note_dialog = MDDialogNote(self.expense_note)
            self.note_dialog.bind(on_dismiss = self.get_note)
        self.note_dialog.open()

    def get_note(self, instance):
        self.expense_note = self.note_dialog.note

    def return_amount(self, instance):
        self.expense_string_amount = str(number_input_control(instance))

    def date_definition(self, instance):
        self.date_selector = instance.active

    def show_expense_day_picker(self):
        if not self.expense_day_picker:
            self.expense_day_picker = MDDialogDayOfMonth(self.expense_payment_day)
            self.expense_day_picker.bind(on_dismiss = self.get_day)

        self.expense_day_picker.open()
    
    def get_day(self, event):
        self.expense_payment_day = self.expense_day_picker.dialog_day

    def on_expense_payment_day(self, instance, value):
        if value > 0:
            self.payment_day_label = self.payment_day_label_empty.replace('__', str(value))
        else:
            self.payment_day_label = self.payment_day_label_empty
            if self.expense_day_picker:
                self.expense_day_picker.dialog_day = 0

    def show_alert(self, information):
        alert_account_dialog = MDDialog(
            title = conf.alert_dialog_title,
            text = information
        )
        alert_account_dialog.open()

    def open_deletion_dialog(self):
        print('window for deletion')

    def ok_expense(self):
        pass

    def cancel_expense(self):
        pass

