__all__ = ("BudgetConfigurationScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ListProperty, DictProperty, ColorProperty

from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog

from design.widgets.MyDialogPicker import MDDialogItemConfiration, MDDialogColorPicker
from design.widgets.MyDialogAffectation import AffectationDialog
from design.widgets.MyDialogNote import MDDialogNote
from design.widgets.MyListItem import LabelAmountListItem

from design import screens_path


with open(
    os.path.join(screens_path, "budget_configuration", "screen_budget_configuration.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#TODO: think about the possibility to go expense creation page from expense list dialog?
class BudgetConfigurationScreen(Screen):
    #idea: when creating new budget, this dict is initialized with defined
    #set of values:
        #     budget = DictProperty({
        #     'id': None,
        #     'designation': '',
        #     'color': [1, 1, 1],
        #     'account': '',
        #     'cap': '',
        #     'note': '',
        #     'expense': []
        # })

    input_budget = DictProperty({
        'id': 1,
        'designation': 'budget1',
        'color': [1, 0, 0],
        'account': 'compte1',
        'cap': 1000,
        'note': 'test bugdet screen',
        'expense': [
            {'id': 1, 'designation': 'dépense 1', 'amount': 100, 'budget': 'budget1'},
            {'id': 2, 'designation': 'dépense 2', 'amount': 20, 'budget': 'budget1'}
        ]
    })

    expense_data = [
        {'id': 1, 'designation': 'dépense 1', 'amount': 100, 'budget': 'budget1'},
        {'id': 2, 'designation': 'dépense 2', 'amount': 20, 'budget': 'budget1'},
        {'id': 3, 'designation': 'dépense 3', 'amount': 300, 'budget': 'budget2'},
        {'id': 4, 'designation': 'dépense 4', 'amount': 400, 'budget': 'budget3'},
        {'id': 1, 'designation': 'dépense 5', 'amount': 100, 'budget': 'budget1'},
        {'id': 2, 'designation': 'dépense 6', 'amount': 20, 'budget': 'budget1'},
        {'id': 3, 'designation': 'dépense 7', 'amount': 300, 'budget': 'budget2'},
        {'id': 1, 'designation': 'dépense 8', 'amount': 100, 'budget': 'budget1'},
        {'id': 2, 'designation': 'dépense 9', 'amount': 20, 'budget': 'budget1'},
        {'id': 3, 'designation': 'dépense 10', 'amount': 300, 'budget': 'budget2'}
    ]

    account_list = ['compte1','compte2','compte3', 'compte4']

    #Screen variable
    budget_designation = StringProperty()
    budget_amount = NumericProperty()
    budget_color = ColorProperty()
    budget_account = StringProperty()
    budget_cap = NumericProperty()
    budget_note = StringProperty()
    budget_expense = ListProperty()

    #initialize dialog
    account_dialog = None
    color_dialog = None
    expense_dialog = None
    note_dialog = None

    #label
    expense_separator = StringProperty('Dépenses :')
    budget_hint = StringProperty('Budget')
    cap_hint = StringProperty('Plafond')
    expense_dialog_title = 'Liste des dépenses :'
    note_dialog_title = 'Note :'
    ok_button = 'OK'
    cancel_button = 'Annuler'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_screen_variable()
        self.compute_budget_amount()
        Clock.schedule_once(self.set_expense_list)

    def _set_screen_variable(self):
        self.budget_designation = self.input_budget['designation']
        self.budget_color = self.input_budget['color']
        self.budget_account = self.input_budget['account']
        self.budget_cap = self.input_budget['cap']
        self.budget_note = self.input_budget['note']
        self.budget_expense = self.input_budget['expense']

    def compute_budget_amount(self):
        self.budget_amount= sum([expense['amount'] for expense in self.budget_expense])

    def set_expense_list(self, interval):
        self.ids.expense_list.clear_widgets()

        for expense in self.budget_expense:
            list_item = LabelAmountListItem(
                designation = expense['designation'],
                amount = expense['amount']
            )
            list_item.bind(on_release = self.go_to_expense)
            self.ids.expense_list.add_widget(list_item)

    def ok_budget_update_or_creation(self):
        if self.input_budget['id'] == None:
            print('Call fuction to create budget in DB')
            print('Call function to create expense historic in DB')
        else:
            print('if modification in budget table, update line')
            print('if modification in expense historic table, update line')

    def cancel_budget_action(self):
        #reset all modification
        #exit screen, go back to precedent screen
        pass

    def return_designation(self, instance):
        self.budget_designation = instance.text

    def return_cap(self, instance):
        self.budget_cap = int(instance.text)

    def go_to_expense(self, event):
        print('Go to expense page')

    def show_account_list(self):
        if not self.account_dialog:
            self.account_dialog = MDDialogItemConfiration(self.account_list, self.budget_account)
            self.account_dialog.bind(on_dismiss = self.get_account)
        self.account_dialog.open()

    def get_account(self, event):
        for item in self.account_dialog.items:
            if item.state == 'down' or  item.ids.check.active == True:
                self.budget_account = item.text
                break

    def show_color_picker(self):
        if not self.color_dialog:
            self.color_dialog = MDDialogColorPicker(self.budget_color)
            self.color_dialog.bind(on_dismiss = self.get_color)

        self.color_dialog.open()

    def get_color(self, event):
        self.budget_color = self.color_dialog.color_pick

    def show_note_dialog(self):
        if not self.note_dialog:
            self.note_dialog = MDDialogNote(self.budget_note)
            self.note_dialog.bind(on_dismiss = self.get_note)
        self.note_dialog.open()

    def get_note(self, instance):
        self.budget_note = self.note_dialog.note

    def expense_list_update(self):
        if not self.expense_dialog:
            self.expense_dialog = MDDialog(
                title = self.expense_dialog_title,
                type = 'custom',
                content_cls = AffectationDialog(data = self.expense_data, budget = self.input_budget['designation']),
                buttons = [
                        MDRaisedButton(
                            text = self.cancel_button,
                            on_press = self.affectation_cancel
                        ),
                        MDRaisedButton(
                            text= self.ok_button,
                            on_press = self.affectation_ok
                        )
                    ]
            )
            self.expense_dialog.ids.container.padding = [dp(25),dp(25),dp(8),dp(0)]

            self.expense_dialog.bind(on_dismiss = self.reset_affectation_list)

            for item in self.expense_dialog.items:
                if item.text == self.budget['account']:
                    item.ids.check.active = True


        self.expense_dialog.open()

    def reset_affectation_list(self, *args):
        expense_designation_budget = [expense_budget['designation'] for expense_budget in self.budget_expense]
        for item in self.expense_dialog.content_cls.ids.list.children:
            if item.ids.designation.text in expense_designation_budget:
                item.ids.check.active = True
            else:
                item.ids.check.active = False

    def affectation_cancel(self, *args):
        self.reset_affectation_list()
        self.expense_dialog.dismiss()

    def affectation_ok(self, *args):
        expense_list = []
        for index, item in enumerate(reversed(self.expense_dialog.content_cls.ids.list.children)):
            if item.ids.check.active == True:
                expense_list.append(self.expense_data[index])

        self.budget_expense = expense_list

        self.compute_budget_amount()
        self.set_expense_list(None)
        self.expense_dialog.dismiss()
