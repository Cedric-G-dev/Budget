__all__ = ("TicketAffectationScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

from design.widgets.MyListItem import BillLine
from design.widgets.MyExpansionItem import ExpansionScrollItem
from design.widgets.MyDialogRefund import MDDialogRefund
from design.widgets.MySnackbar import MessageSnackbar
from design.widgets.MyButton import RefillButton

from design.widget_functions import number_input_control

from decimal import Decimal as D

from design import screens_path
import design.config as conf


with open(
    os.path.join(screens_path, "ticket_affectation", "screen_ticket_affectation.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#TODO: selection list is working, except that scrolling over it can trigger
#       list item function -> disable or change function call
#TODO: finish design rework, refill box, variable with XXProperty
#TODO: when selecting a budget, scroll screen to bottom to see budget lines
#TODO: when adding budget, set the value equal to total amount-sum(budget amount)
class TicketAffectationScreen(Screen):
    bill_amount_txt = StringProperty('MONTANT :')
    bill_icon = StringProperty('account-cash')
    bill_amount = StringProperty()

    budget_total_separator = 'Montant du ticket :'
    budget_selection_separator = 'Choix des budgets :'
    budget_selection_state = BooleanProperty(False)
    budget_definition_separator = 'Repartition sur budget(s) :'

    refund_dialog = None

    # Bool checking if total = sum of budget
    bill_state = BooleanProperty(True)

    #icon list with x-outline sibling
    icon_list = ['database-search', 'bank', 'database']

    Account_Budget_bill = {
            'compte1' : {'budget1' : D('100.00'), 'budget2' :  False, 'compte1_tmp': False},
            'compte2' : {'budget3' :  False, 'budget4' : False},
            'compte3' : {'budget5' : D('100.00'), 'budget6' :  D('100.00'),
                'budget7' : False},
            'compte4' : {'budget8': False}
        }
    amount = D('300.00')
    bill_amount = str(amount)
    #enable refill only for output ticket
    transaction_item = ['Sortie', 'Entrée', 'Interne']
    transaction_input = 'Entrée'
    account_input = 'compte1'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._set_recursion_widget)
        Clock.schedule_once(self._set_bill)
        Clock.schedule_once(self._set_refill_widget)

    def _set_recursion_widget(self, interval):
        for account, account_dict in self.Account_Budget_bill.items():
            recursion_widget = ExpansionScrollItem(
                data_recursion = account_dict,
                icon_recursion = self.icon_list[1:],
                text = account,
                item_icon = self.icon_list[0]
            )
            recursion_widget.bind(indicator_update = self.update_dict)
            self.ids.budget_selection_box.add_widget(recursion_widget)

    def _set_bill(self, interval = None):
        for key, value in self.Account_Budget_bill.items():
            for k, v in value.items():
                if v is not False:
                    box = BillLine(key, k, v, self.bill_state)
                    box.ids.delete.bind(on_release = self.delete_bill_line)
                    box.ids.input.bind(focus = self.bill_input_control)
                    self.ids.bill.add_widget(box)

    def _set_refill_widget(self, interval):
        if self.transaction_input == self.transaction_item[1]:
            refill = RefillButton()
            refill.bind(button_state = self.show_refund)
            self.ids.box.add_widget(refill, 1)

    def expand_selection(self):
        if self.ids.scroll.height != 0:
            self.ids.scroll.height = 0
            self.budget_selection_state = False
        elif self.ids.scroll.height == 0:
            self.ids.scroll.height = self.ids.budget_selection_box.height
            self.budget_selection_state = True

    def update_dict(self, instance, data):
        self.Account_Budget_bill[instance.text] = instance.data_recursion
        self.update_bill()

    def bill_amount_update_control(self, instance):
        if instance.focus is False:
            self.amount = number_input_control(instance)
            self.bill_amount = str(self.amount)

        self.bill_amount_check()

    def delete_bill_line(self, instance):
        account = instance.parent.account
        budget = instance.parent.budget
        self.Account_Budget_bill[account][budget] = False

        #update recursion
        list_exp_1 = self.ids.budget_selection_box.children
        for exp1 in list_exp_1:
            if exp1.text == account:
                list_exp_2 = exp1.ids.value_item_box.children
                for exp2 in list_exp_2:
                    if exp2.text == budget:
                        exp2.item_state = False

        self.bill_amount_check()
        self.update_bill()

    def bill_input_control(self, instance, focus):
        if focus is False:
            account = instance.parent.account
            budget = instance.parent.budget

            self.Account_Budget_bill[account][budget] = D(number_input_control(instance))

            self.bill_amount_check()

    #check if bill list match the bill amount and change textfield color
    def bill_amount_check(self):
        current_amount = self.bill_amount_computation()
        if current_amount != self.amount:
            self.bill_state = False
        else:
            self.bill_state = True

    #compute amount from bill
    def bill_amount_computation(self):
        amount = D('0.00')
        for key, value in self.Account_Budget_bill.items():
            for k, v in value.items():
                if v is not False:
                    amount += v
        return amount

    #change billline textfield color
    def on_bill_state(self, instance, value):
        for item in self.ids.bill.children:
            item.state = self.bill_state

    #construct/update budget bill lines
    def update_bill(self):
        if self.ids.bill.children != []:
            self.ids.bill.clear_widgets()

        self._set_bill()

    #display refill option
    def show_refund(self, instance, value):
        if not self.refund_dialog:
            btn_delete = MDRaisedButton(
                        text = conf.delete_text,
                        on_press = self.delete_refill
                    )
            btn_validate = MDRaisedButton(
                        text = conf.validate_text,
                        on_press = self.construct_refill
                    )

            self.refund_dialog = MDDialogRefund(btn_delete, btn_validate)

        self.refund_dialog.open()

    #display message for refill
    def show_refill_message(self, information):
        refill_message = MessageSnackbar(text = information)
        refill_message.size_hint_x = (Window.width - (refill_message.snackbar_x*2)) / Window.width
        refill_message.open()

    def delete_refill(self, instance):
        self.refund_dialog.dismiss()
        self.refund_dialog = None
        self.show_refill_message('Aucun remboursement défnit')

    def construct_refill(self, instance):
        self.refill_dict = {}
        error_check = False

        for item in self.refund_dialog.content_cls.ids.stack.children:
            #check if reasons are unique
            if item.ids.who.text in self.refill_dict.keys():
                self.show_alert('Deux remboursements ont le même nom !')
                error_check = True
                break
            elif item.ids.howmany.text == '' or item.ids.who.text == '':
                self.show_alert('Champ(s) non renseigné(s) !')
                error_check = True
                break
            elif D(item.ids.howmany.text) == D('0'):
                self.show_alert('Remboursement nul non accepté !')
                error_check = True
                break
            else:
                item.ids.who.text = item.ids.who.text.lower()
                #ok button event triggered before unfocus event --> check_amount call here
                if len(item.ids.howmany.text.split('.')) == 1:
                    text_input = item.ids.howmany.text + '.00'
                else:
                    if len(item.ids.howmany.text.split('.')[1]) == 1:
                        text_input = item.ids.howmany.text + '0'
                    elif len(item.ids.howmany.text.split('.')[1]) == 2:
                        text_input = item.ids.howmany.text
                self.refill_dict[item.ids.who.text] = D(text_input)

        if error_check == True:
            pass
        elif not self.refill_dict:
            self.show_alert('Aucun remboursement définit !')
        else:
            self.refund_dialog.dismiss()
            self.show_refill_message('Liste de remboursement définit')

    def show_alert(self, information):
        alert_account_dialog = MDDialog(
            title = conf.alert_dialog_title,
            text = information
        )
        alert_account_dialog.open()

    def ok_bill(self):
        loop_state = True
        exit_bill_ditc = {}

        #check if amout match the bill
        if self.bill_state == False:
            self.show_alert('Le montant du ticket ne correspond pas au montant affilié au(x) budget(s)')
        #check that for intern transaction, amount is null
        elif self.amount != 0 and self.transaction_input == self.transaction_item[1]:
            self.show_alert('Pour un ticket interne, le montant doit-être 0')
        #check that value > 0 pour output/input transaction
        elif self.amount > 0 and self.transaction_input != self.transaction_item[1]:
            self.show_alert('le montant doit-être > 0')
        #check if all required field are filled
        else:
            for key, value in self.Account_Budget_bill.items():
                if loop_state is False:
                    self.show_alert('Un montant affilié à un budget est 0')
                    break
                for k, v in value.items():
                    if v == D('0.00'):
                        loop_state = False
                        break
                    elif v is not False and v != D('0.00'):
                        exit_bill_ditc[k] = v

            print(exit_bill_ditc)

    def cancel_bill(self):
        pass

    #TODO ok button: check if sum budget + (refill)= amount (0 if interne)
    # on_enter fx
    def test(self):
        print('toto')
