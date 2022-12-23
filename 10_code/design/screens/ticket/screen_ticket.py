__all__ = ("TicketScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty
from kivy.clock import Clock

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from design.widgets.MyDialogPicker import MDDialogResearch, ListItemResearch, MDDialogItemConfiration, MDDialogDate
from design.widgets.MyListItem import LabelAmountListItem 
from design.widgets.MyDialogNote import MDDialogNote
from design.widgets.drawer import NavDrawer

import pandas as pd
from decimal import Decimal as D
from datetime import datetime, date

import main as DB

from design.config import app_config
from design import screens_path


with open(
    os.path.join(screens_path, "ticket", "screen_ticket.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())

#TODO: revoir bouton suprression ticket
#TODO: montant ticket comme budgetscreen (ligne séparatrice, liste)
#TODO: change transaction text -> largeur bouton
#TODO: change bouton color/ forme, OK/annuler forme
#TODO: reformat code so that everything depends on variable definied in as class variable
#TODO: see to update the difference between data entered or not -> just changing the icon is not enough
#           play with color
class TicketScreen(Screen):
    #test ticket
    # for new ticket
        # input_ticket = DictProperty({
        #     'id': False,
        #     'date': datetime.date.today(),
        #     'transaction': '',
        #     'recipient': '',
        #     'reason': '',
        #     'payment_type': '',
        #     'account': '',
        #     'note': ''
        # })

    input_ticket = DictProperty({
        'id': False,
        'date': date.today().strftime('%d/%m/%Y'),
        'transaction': 'Entrée',
        'recipient': 'AuchanXXXXXX',
        'reason': 'chaussures',
        'payment_type': 'CB',
        'account': 'compte1',
        'note': 'bonjour'
    })

    #Screen variable
    abstract_state = BooleanProperty(True)
    #a.s. : True = opened, False = closed

    date_label = StringProperty()
    transaction_label = StringProperty()
    recipient_label = StringProperty()
    payment_type_label = StringProperty()
    reason_label = StringProperty()
    account_label = StringProperty()
    bill_amount_label = StringProperty()

    ticket_date = date.today()
    ticket_transaction = StringProperty()
    ticket_recipient = StringProperty()
    ticket_reason = StringProperty()
    ticket_payment_type = StringProperty()
    ticket_account = StringProperty()
    ticket_note = StringProperty()
    ticket_amount = D('0.00')

    #same object for both research
    research_suggestion = ['test1', 'a_test2', 'b_test3'] * 4

    amount_input = D('400.00')
    #except for intern type transaction, it is not allowed to use tmp budget except for the chosen account
    #thus impacting the construction of the ticket bill dict
    #to create ticket automatically new input in the dict will be added (tmp budget)
    #TODO write a function creating a good dict
    # -> add only the tmp budget of the account chosen
    Account_Budget_bill = {
            'compte1' : {'budget1' : D('100.00'), 'budget2' :  False, 'compte1_tmp': False},
            'compte2' : {'budget3' :  False, 'budget4' : False},
            'compte3' : {'budget5' : D('100.00'), 'budget6' :  False,
                'budget7' : D('100.00')},
            'compte4' : {'budget8': D('100.00')}
        }
    #initialize dialog
    date_picker = None
    transaction_dialog = None
    reason_dialog = None
    recipient_dialog = None
    payment_type_dialog = None
    account_dialog = None
    note_dialog = None
    deletion_dialog = None

    #construction of table for selection, from DB
    Account_Payment_Type = {
        'compte1' : {'CB': True, 'Virement': True, 'Chèque': True},
        'compte2' : {'CB': False, 'Virement': True, 'Chèque': True},
        'compte3' : {'CB': False, 'Virement': True, 'Chèque': False},
        'compte4' : {'CB': False, 'Virement': False, 'Chèque': True}
    }

    def __init__(self, screen_manager, ticket_id = None, **kwargs):
        self.screen_manager = screen_manager
        self.general_settings = app_config['general_settings']
        self.screen_settings = app_config['TicketScreen']

        if ticket_id:
            self._set_screen_variable_for_existing_ticket(ticket_id)
        else:
            self._set_screen_variable_for_new_ticket()


        self._set_dialog_pickers_item_list()
        super(Screen, self).__init__(**kwargs)
        Clock.schedule_once(self._set_budget_list)

    def _set_dialog_pickers_item_list(self):
        self.transaction_item = self.screen_manager.Transaction_type_df['transaction_type']
        self.payment_type_item =self.general_settings['means_of_paiement']
        self.account_list = self.screen_manager.account_df['designation'].to_list()        
        
    def _set_screen_variable_for_new_ticket(self):
        self.date_label = self.screen_settings['buttons']['date']
        self.transaction_label = self.screen_settings['buttons']['transaction_type']
        self.recipient_label = self.screen_settings['buttons']['recipient']
        self.reason_label = self.screen_settings['buttons']['reason']
        self.payment_type_label = self.screen_settings['buttons']['payment_type']
        self.account_label = self.screen_settings['buttons']['account']

    def _set_screen_variable_for_existing_ticket(self, ticket_id):
        self.ticket_df = self.screen_manager.ticket_info_df.loc[
            self.screen_manager.ticket_info_df['id_ticket'] == ticket_id]

        self.ticket_affectation_df = self.screen_manager.ticket_info_df.loc[
            self.screen_manager.ticket_info_df['id_ticket'] == ticket_id]

        # self.ticket_date_string = self.input_ticket['date']
        # self.date_input = datetime.strptime(self.ticket_date_string, '%d/%m/%Y').date()

        self.ticket_date = self.ticket_df.loc[0,'date']
        self.ticket_transaction = self.ticket_df.loc[0, 'transaction_type']
        self.ticket_recipient = self.ticket_df.loc[0,'recipient']
        self.ticket_reason = self.ticket_df.loc[0,'reason']
        self.ticket_payment_type = self.ticket_df.loc[0,'payment_type']
        self.ticket_account = self.ticket_df.loc[0,'account']
        self.ticket_note = self.ticket_df.loc[0,'note']
        self.ticket_amount = self.ticket_df.loc[0, 'amount']

        self.date_label = self.ticket_date.strftime(self.general_settings['time_format_string'])
        self.transaction_label = self.ticket_transaction
        self.recipient_label = self.ticket_recipient
        self.reason_label = self.ticket_reason
        self.payment_type_label = self.ticket_payment_type
        self.account_label = self.ticket_account

    # #TODO: false definition, think about it with ticketbillscreen
    # def compute_ticket_amount(self):
    #     self.ticket_amount = D('0.00')
    #     for account, budget_bill in self.Account_Budget_bill.items():
    #         for amount in budget_bill.values():
    #             self.ticket_amount += amount

    #TODO: think about function when clicking on list item
    def _set_budget_list(self, interval):
        self.ids.budget_list.clear_widgets()
        for budget_account_data in self.Account_Budget_bill.values():
            for budget, amount in budget_account_data.items():
                if amount:
                    list_item = LabelAmountListItem(
                        designation = budget,
                        amount = float(amount)
                    )
                    #list_item.bind(on_release = self.go_to_expense)
                    self.ids.budget_list.add_widget(list_item)

    def open_deletion_dialog(self):
        if not self.deletion_dialog:
            self.deletion_dialog = MDDialog(
                title = self.screen_settings['dialog']['title']['deletion'],
                text = self.screen_settings['dialog']['message']['deletion'],
                buttons = [
                    MDFlatButton(
                        text = self.general_settings['commun_widget']['buttons']['validate']
                    ),
                    MDFlatButton(
                        text = self.general_settings['commun_widget']['buttons']['cancel']
                    ),
                ],
            )
        self.deletion_dialog.open()

    def expand(self):
        if self.ids.scroll.height == self.ids.abstract.height:
            self.ids.scroll.height = 0
            self.abstract_state = False
        elif self.ids.scroll.height == 0:
            self.ids.scroll.height = self.ids.abstract.height
            self.abstract_state = True

    def show_calendar(self):
        if not self.date_picker:
            self.date_picker = MDDialogDate(self.ticket_date)
            self.date_picker.bind(on_dismiss = self.get_date)
        self.date_picker.open()

    def get_date(self, event):
        self.ticket_date = self.date_picker.dialog_date
        self.date_label = self.ticket_date.strftime('%d/%m')

    def show_transaction_list(self):
        if not self.transaction_dialog:
            self.transaction_dialog = MDDialogItemConfiration(self.transaction_item, self.ticket_transaction)
            self.transaction_dialog.bind(on_dismiss = self.get_transaction)

        self.transaction_dialog.open()

    def get_transaction(self, event):
        self.ticket_transaction = self.transaction_dialog.choice
        self.transaction_label = self.ticket_transaction

    def show_recipient_definition(self):
        if not self.recipient_dialog:
            self.recipient_dialog = MDDialogResearch(
                self.ticket_recipient,
                self.screen_settings['dialog']['hint']['recipient'],
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']                
            )
            self.recipient_dialog.content_cls.ids.input.bind(text = self.update_recipient_research_list)
            self.recipient_dialog.bind(on_dismiss = self.get_recipient)
        self.recipient_dialog.open()

    #TODO work on that function when linked with DB done
    def update_recipient_research_list(self, event, text):
        #suppression old suggestion list
        self.recipient_dialog.content_cls.ids.suggestion_list.clear_widgets()
        #call SQL function to make a newnlist
        # list =
        # '''
        # SELECT recipient, COUNT() AS frequency
        # FROM ticket
        # WHERE recipient LIKE '%text%'
        # GROUP BY recipient
        # ORDER BY frequency
        # LIMIT X
        # '''
        if text != '':
            new_list = []
            for item in self.research_suggestion:
                if text in item:
                    new_list.append(item)
            for item in new_list:
                list_widget = ListItemResearch(text = item)
                self.recipient_dialog.content_cls.ids.suggestion_list.add_widget(list_widget)

    def get_recipient(self, event):
        self.ticket_recipient =  self.recipient_dialog.user_input
        #handle name display
        if self.ticket_recipient == '':
            self.recipient_label = self.recipient_label_empty
        else:
            if len(self.ticket_recipient) > 14:
                self.recipient_label = self.ticket_recipient[:13] + '...'
            else:
                self.recipient_label = self.ticket_recipient

    def show_reason_definition(self):
        if not self.reason_dialog:
            self.reason_dialog = MDDialogResearch(
                self.ticket_reason,
                self.screen_settings['dialog']['hint']['reason'],
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']                
            )
            self.reason_dialog.content_cls.ids.input.bind(text = self.update_reason_research_list)
            self.reason_dialog.bind(on_dismiss = self.get_reason)
        self.reason_dialog.open()

    #TODO work on that function when linked with DB done
    def update_reason_research_list(self, event, text):
        #suppression old suggestion list
        self.reason_dialog.content_cls.ids.suggestion_list.clear_widgets()
        #call SQL function to make a newnlist
        # list =
        # '''
        # SELECT recipient, COUNT() AS frequency
        # FROM ticket
        # WHERE recipient LIKE '%text%'
        # GROUP BY recipient
        # ORDER BY frequency
        # LIMIT X
        # '''
        if text != '':
            new_list = []
            for item in self.research_suggestion:
                if text in item:
                    new_list.append(item)
            for item in new_list:
                list_widget = ListItemResearch(text = item)
                self.reason_dialog.content_cls.ids.suggestion_list.add_widget(list_widget)

    def get_reason(self, event):
        self.ticket_reason =  self.reason_dialog.user_input
        #handle name display
        if self.ticket_reason == '':
            self.reason_label = self.reason_label_empty
        else:
            if len(self.ticket_reason) > 14:
                self.reason_label = self.ticket_reason[:13] + '...'
            else:
                self.reason_label = self.ticket_reason

    def show_paiment_list(self):
        if not self.payment_type_dialog:
            self.payment_type_dialog = MDDialogItemConfiration(self.payment_type_item, self.ticket_payment_type)
            self.payment_type_dialog.bind(on_dismiss = self.get_paiment)

        self.payment_type_dialog.open()

    def get_paiment(self, event):
        self.ticket_payment_type = self.payment_type_dialog.choice
        self.payment_type_label = self.ticket_payment_type

    def show_account_list(self):
        if not self.account_dialog:
            self.account_dialog = MDDialogItemConfiration(self.account_list, self.ticket_account)
            self.account_dialog.bind(on_dismiss = self.get_account)

        self.account_dialog.open()

    def get_account(self, event):
        self.ticket_account = self.account_dialog.choice
        self.account_label = self.ticket_account

    def show_note_dialog(self):
        if not self.note_dialog:
            self.note_dialog = MDDialogNote(
                self.screen_settings['dialog']['title']['note'],
                self.ticket_note,
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']
            )
            self.note_dialog.bind(on_dismiss = self.get_note)
        self.note_dialog.open()

    def get_note(self, instance):
        self.ticket_note = self.note_dialog.note

    def open_TicketBillScreen(self):
        if self.ticket_account == None:
            self.show_alert('Choisir un compte avant de poursuivre')
        #TODO
        print('ouverture fenetre modification montant')

    def ok_ticket(self):
        # check if all required field are filled
        if self.ticket_transaction == None:
            self.show_alert(self.screen_settings['dialog']['message']['no_transaction'])
        elif self.ticket_recipient == '':
            self.show_alert(self.screen_settings['dialog']['message']['no_recipient'])
        elif self.ticket_reason == '':
            self.show_alert(self.screen_settings['dialog']['message']['no_reason'])
        elif self.ticket_payment_type == None:
            self.show_alert(self.screen_settings['dialog']['message']['no_payment_type'])
        elif self.ticket_account == None:
            self.show_alert(self.screen_settings['dialog']['message']['no_account'])
        # if account does not have the payment type
        elif not self.Account_Payment_Type[self.ticket_account][self.ticket_payment_type]:
            self.show_alert(self.screen_settings['dialog']['message']['account_payment_type_not_existing'])
        elif self.ticket_transaction == self.transaction_item[2] and self.mutli_account_count() > 2:
            self.show_alert(self.screen_settings['dialog']['message']['intern_ticket_too_many_account'])
        # Db object creation
        else:
            pass
            list_of_ticket = []
            #intern ticket
            #TODO: for intern ticket amount = amount of the transfer
            if self.ticket_transaction == self.transaction_item[2]:
                ticket_dict = {}
                for key, value in self.Account_Budget_bill.items():
                    #TODO: check condition 0 or False
                    if list(value.values()) == [0 for i in value.keys()]:
                        continue
                    #creation of db object
                    else:
                        temp_dict = dict(value)
                        for k, v in value.items():
                            if v is False:
                                del temp_dict[k]
                            else:
                                ticket_dict.update(temp_dict)

                temp_ticket = DB.Ticket(
                    self.ticket_date_string,
                    self.ticket_recipient,
                    self.ticket_reason,
                    self.ticket_transaction,
                    self.ticket_payment_type,
                    self.ticket_amount,
                    0,
                    self.ticket_note,
                    ticket_dict
                )

            elif self.mutli_account_count() == 0:
                temp_ticket = self.real_ticket(self.ticket_account,
                    self.Account_Budget_bill[self.ticket_account], False)

                list_of_ticket.append(temp_ticket)

            else:
                #creation of intern ticket to allow refill the 'true ticket' = real ticket
                #automatisation of intern ticket creation
                #1 creation of real ticket
                #2 creation of intern ticket on each account (on budget account_tmp)-> non real ticket
                #3 creation of refill ticket for each account -> real intern mouvement to be done
                # --> this allow to delete refill ticket to sum multiple ones, thus simplifying
                #       real refill ticket

                if self.ticket_transaction == self.transaction_item[0]:
                    for key, value in self.Account_Budget_bill.items():
                        if list(value.values()) == [0 for i in value.keys()]:
                            continue
                        #creation of db object
                        else:
                            if key != self.ticket_account:
                                temp_dict = dict(value)
                                temp_refill_dict = {}
                                temp_amount = D('0.00')

                                for k, v in value.items():
                                    if v is False:
                                        del temp_dict[k]
                                    else:
                                        temp_dict[k] = -v
                                        temp_amount += v

                                temp_dict[key + '_tmp'] = temp_amount
                                temp_refill_dict[key + '_tmp'] = - temp_amount
                                temp_refill_dict[self.ticket_account +'_tmp'] = temp_amount

                                temp_ticket = DB.Ticket(
                                    self.date_input,
                                    'Moi',
                                    'P.I. ' + self.ticket_reason,
                                    self.transaction_item[2],
                                    self.payment_type_item[1],
                                    D('0.00'),
                                    1,
                                    ('Payement Interne ' + self.ticket_reason
                                        + ' ' + self.ticket_recipient
                                        + ' ' + self.ticket_date_string),
                                    temp_dict
                                )

                                temp_refill_ticket = DB.Ticket(
                                    self.date_input,
                                    'Moi',
                                    'R. ' + self.ticket_reason,
                                    self.transaction_item[2],
                                    self.payment_type_item[1],
                                    D('0.00'),
                                    2,
                                    ('Remboursement ' + self.ticket_reason
                                        + ' ' + self.ticket_recipient
                                        + ' ' + self.ticket_date_string),
                                    temp_refill_dict
                                )

                                list_of_ticket.append(temp_ticket)
                                list_of_ticket.append(temp_refill_ticket)

                            else:
                                temp_ticket = self.real_ticket(key, value, True)
                                list_of_ticket.insert(0, temp_ticket)

                else:
                    for key, value in self.Account_Budget_bill.items():
                        if list(value.values()) == [False for i in value.keys()]:
                            continue
                        #creation of db object
                        else:
                            if key != self.ticket_account:
                                temp_dict = dict(value)
                                temp_refill_dict = {}
                                temp_amount = D('0.00')
                                for k, v in value.items():
                                    if v is False:
                                        del temp_dict[k]
                                    else:
                                        temp_dict[k] = v
                                        temp_amount += v

                                temp_dict[key + '_tmp'] = - temp_amount
                                temp_refill_dict[key + '_tmp'] = temp_amount
                                temp_refill_dict[self.ticket_account +'_tmp'] = - temp_amount

                                temp_ticket = DB.Ticket(
                                    self.date_input,
                                    'Moi',
                                    'P.I. ' + self.ticket_reason,
                                    self.transaction_item[2],
                                    self.payment_type_item[1],
                                    D('0.00'),
                                    1,
                                    ('Payement Interne ' + self.ticket_reason
                                        + ' ' + self.ticket_recipient
                                        + ' ' + self.ticket_date_string),
                                    temp_dict
                                )

                                temp_refill_ticket = DB.Ticket(
                                    self.date_input,
                                    'Moi',
                                    'R. ' + self.ticket_reason,
                                    self.transaction_item[2],
                                    self.payment_type_item[1],
                                    D('0.00'),
                                    2,
                                    ('Remboursement ' + self.ticket_reason
                                        + ' ' + self.ticket_recipient
                                        + ' ' + self.ticket_date_string),
                                    temp_refill_dict
                                )

                                list_of_ticket.append(temp_ticket)
                                list_of_ticket.append(temp_refill_ticket)

                            else:
                                temp_ticket = self.real_ticket(key, value, True)
                                list_of_ticket.insert(0, temp_ticket)
            #TODO add refill bill if exist and push to DB

    def cancel_ticket(self):
        pass

    def show_alert(self, information):
        alert_account_dialog = MDDialog(
            title = 'Attention',
            text = information
        )
        alert_account_dialog.open()

    def mutli_account_count(self):
        mutli_account = 0
        for key, value in self.Account_Budget_bill.items():
            if key != self.ticket_account:
                if value.values() != [False for i in value.keys()]:
                    mutli_account += 1

        return mutli_account

    def real_ticket(self, key, value, criteria):
        temp_dict = dict(value)
        temp_amount = D('0.00')

        for k, v in value.items():
            # if k != (key + '_tmp') and v is False:
            #     del temp_dict[k]
            # elif v is False and criteria is False:
            #     del temp_dict[k]
            # elif v is False and criteria is True:
            #     temp_dict[k] = D('0.00')
            # else:
            #     temp_amount += v

            if v is not False:
                temp_amount += v
            elif v is False and k != (key + '_tmp'):
                del temp_dict[k]
            elif v is False and criteria is True:
                temp_dict[k] = D('0.00')
            else:
                del temp_dict[k]

        if (key +'_tmp') in temp_dict.keys():
            temp_dict[key +'_tmp'] += self.amount_input - temp_amount

        ticket = DB.Ticket(
            self.date_input,
            self.ticket_recipient,
            self.ticket_reason,
            self.ticket_transaction,
            self.ticket_payment_type,
            self.amount_input,
            0,
            self.ticket_note,
            temp_dict
        )

        return ticket
