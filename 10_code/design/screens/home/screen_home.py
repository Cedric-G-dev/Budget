__all__ = ("HomeScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty, DictProperty

from design.widgets.MyDialogPicker import MDDialogFilter
from design.widgets.MyListItem import ListInOutItem
from design.widgets.MyAbstract import AccountAbstract, BudgetAbstract

import pandas as pd

from design import screens_path
from design.config import app_config
from design.screens.ticket import TicketScreen


with open(
    os.path.join(screens_path, "home", "screen_home.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#TODO: create date filter for ticket
#TODO: regroup filter in a list of button displayed like ButtonSpeedDial
#TODO: create like segmented control to select the info displayed in ticket
# -> create custom because current widget not mature (ex: fixedwidth 320, no icon ...)
#TODO: think about abstract widget closing when action on one

#TODO: account and budget value have to be update on ticket creation
#TODO: account and budget status computed in abstract widget, but may be stored in DB to avoid computation cost
#TODO: account and budget amount computed on all data --> create historic with last ticket id for computation
#TODO: bug for ListInOutItem when state icon width is too large: the computation is good but the value is not assigned correctly
#       observe for 1 item, with progress question

#TODO: optimize the adding of list in out item when overscrolling
#TODO: link filter account and budget

class HomeScreen(Screen):
    #Screen variables
    account_nav = 'account'
    budget_nav = 'budget'
    ticket_nav = 'ticket'

    list_scroll_position = NumericProperty(0)

    budget_nav_account_filter_dialog = None
    ticket_nav_account_filter_dialog = None
    ticket_nav_budget_filter_dialog = None
    ticket_nav_ticket_state_filter_dialog = None

    #item for filtering in the different navigation pages
    budget_nav_account_filter = DictProperty()
    budget_nav_budget_abstract_dict = {}

    ticket_nav_account_filter = DictProperty()
    ticket_nav_budget_filter = DictProperty()
    ticket_nav_ticket_state_filter = DictProperty()

    def __init__(self, screen_manager, **kwargs):
        self.screen_manager = screen_manager
        self.general_settings = app_config['general_settings']
        self.screen_settings = app_config['HomeScreen']

        self._set_ticket_state_filter()
        super().__init__(**kwargs)

    def _set_ticket_state_filter(self):
        self.active_ticket = self.screen_manager.ticket_state_df.loc[
            self.screen_manager.ticket_state_df['id_ticket_state'] == 1,
            ['ticket_state']
        ]._get_value(0, 'ticket_state')

        for index, ticket_state in self.screen_manager.ticket_state_df.iterrows():
            self.ticket_nav_ticket_state_filter[ticket_state['ticket_state']] = True

    def on_enter(self):
        self._set_account_abstracts()
        self._set_budget_abstracts()
        self._set_ticket_list()

    def _set_account_abstracts(self):
        for index, account in self.screen_manager.account_info_df.iterrows():
            account_abstract = AccountAbstract(
                account_id = account['id_account'],
                account_designation = account['designation'],
                account_bank_amount = account['bank_amount'],
                account_real_amount = account['real_amount'],
                account_month_expenditure = account['month_expenditure'],
                account_month_prevision = account['monthly_output_amount']
            )

            account_abstract.bind(graph_button = self.display_account_related_tickets)
            account_abstract.bind(list_button_1 = self.display_account_related_budgets)
            account_abstract.bind(list_button_2 = self.display_account_pending_tickets)

            self.ids.accounts.add_widget(account_abstract)

            #initiate account filter
            self.budget_nav_budget_abstract_dict[account['designation']] = dict()
            self.budget_nav_budget_abstract_dict[account['designation']]['display'] = True
            self.budget_nav_budget_abstract_dict[account['designation']]['associated_budgets'] = list()

            self.budget_nav_account_filter[account['designation']] = True

            self.ticket_nav_account_filter[account['designation']] = True

    def _set_budget_abstracts(self):
        for index, budget in self.screen_manager.budget_info_df.iterrows():
            budget_abstract = BudgetAbstract(
                budget_id = budget['id_budget'],
                budget_designation = budget['designation'],
                budget_amount = budget['budget_amount'],
                budget_month_expenditure = budget['budget_month_expense'],
                budget_month_prevision = budget['monthly_output_amount'],
                budget_cap = budget['cap'],
                bugdet_last_month =  budget['end_of_last_month_budget_amount'],
                account_id = budget['id_account'],
                account_name = budget['account_designation'],
                account_status = budget['account_status']
            )

            budget_abstract.bind(graph_button = self.display_budget_related_tickets)
            budget_abstract.bind(list_button_1 = self.UNKWOWN)
            budget_abstract.bind(list_button_2 = self.display_related_account_abstract)            

            self.budget_nav_budget_abstract_dict[budget['account_designation']]['associated_budgets'].append(budget_abstract)
            
            self.ids.budgets.add_widget(budget_abstract)

            self.ticket_nav_budget_filter[budget['designation']] = True

    def _set_ticket_list(self):
        self.display_indicator_up_to_index_ticket = self.screen_settings['transaction']['number_of_tickets']
        
        self.add_ticket_to_list(self.screen_manager.ticket_info_df.iloc[0:(self.display_indicator_up_to_index_ticket-1),:])

        self.filtered_ticket_info_df = self.screen_manager.ticket_info_df

    def on_budget_nav_account_filter(self, instance, value):
        if self.budget_nav_account_filter_dialog:
            self.budget_nav_account_filter_dialog.content_dict = value

        for account, display_choice in self.budget_nav_account_filter.items():
            self.budget_nav_budget_abstract_dict[account]['display'] = display_choice

    def on_ticket_nav_account_filter(self, instance, value):
        if self.ticket_nav_account_filter_dialog:
            self.ticket_nav_account_filter_dialog.content_dict = value

    def on_ticket_nav_budget_filter(self, instance, value):
        if self.ticket_nav_budget_filter_dialog:
            self.ticket_nav_budget_filter_dialog.content_dict = value

    def on_ticket_nav_ticket_state_filter(self, instance, value):
        if self.ticket_nav_ticket_state_filter_dialog:
            self.ticket_nav_ticket_state_filter_dialog.content_dict = value

    def display_account_related_tickets(self, instance, value):
        self.reset_ticket_nav_filters()
        self.ticket_nav_switch_account_filter(False)
        self.ticket_nav_account_filter[instance.name] = True

        self.ticket_nav_update()
        self.ids.nav.switch_tab(self.ticket_nav)

    def display_account_related_budgets(self, instance, event):
        self.switch_budget_nav_filter(False)
        self.budget_nav_account_filter[instance.name] = True

        self.budget_nav_update()
        self.ids.nav.switch_tab(self.budget_nav)

    def display_account_pending_tickets(self, instance, value):
        self.reset_ticket_nav_filters()
        self.ticket_nav_switch_account_filter(False)
        self.ticket_nav_account_filter[instance.name] = True
        self.ticket_nav_ticket_state_filter[self.active_ticket] = False

        self.ticket_nav_update()
        self.ids.nav.switch_tab(self.ticket_nav)

    def display_budget_related_tickets(self, instance, value):
        self.reset_ticket_nav_filters()
        self.ticket_nav_switch_budget_filter(False)
        self.ticket_nav_budget_filter[instance.name] = True

        self.ticket_nav_update()
        self.ids.nav.switch_tab(self.ticket_nav)

    def UNKWOWN(slef, instance, value):
        print('think about function')

    def display_related_account_abstract(self, instance, value):
        account_abstract_open = False

        for abstract in self.ids.accounts.children:
            if not account_abstract_open:
                if instance.account_name == abstract.name :
                    if not abstract.expansion:
                        abstract.expand()
                    account_abstract_open = True
                elif abstract.expansion:
                    abstract.expand()
            elif abstract.expansion:
                abstract.expand()                    

                
        self.ids.nav.switch_tab(self.account_nav)

    def add_ticket_to_list(self, ticket_to_add_df):
        for index, ticket in ticket_to_add_df.iterrows():
            ticket_list_item = ListInOutItem(
                ticket_id = ticket['id_ticket'],
                date_text = ticket['date'].strftime(self.screen_settings['transaction']['date_format']),
                recipient_text = ticket['recipient'],
                reason_text = ticket['reason'],
                ticket_state = ticket['id_ticket_state'],
                amount = float(ticket['signed_amount']),
                main_budget = str(ticket['budget_designation']),
                budget_color = ticket['budget_color'],
                intern = True if ticket['id_transaction_type'] == 3 else False
            )
            ticket_list_item.bind(on_release = self.open_ticket)

            self.ids.ticket_list.add_widget(ticket_list_item)  

    def show_budget_nav_account_filter(self):
        if not self.budget_nav_account_filter_dialog:
            self.budget_nav_account_filter_dialog = MDDialogFilter(
                self.budget_nav_account_filter,
                self.general_settings['commun_widget']['dialog']['title']['account_filter_name'],
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']
            )
            self.budget_nav_account_filter_dialog.bind(external_ok_action = self.filter_budget_nav_account)
        self.budget_nav_account_filter_dialog.open()

    def filter_budget_nav_account(self, instance, event):
        self.budget_nav_account_filter = self.budget_nav_account_filter_dialog.content_dict
        self.budget_nav_update()

    def budget_nav_update(self):
        self.ids.budgets.clear_widgets()

        for account in self.budget_nav_budget_abstract_dict.keys():
            if self.budget_nav_budget_abstract_dict[account]['display']:
                for budget_abstract in self.budget_nav_budget_abstract_dict[account]['associated_budgets']:
                    self.ids.budgets.add_widget(budget_abstract)        

    def show_ticket_nav_account_filter(self):
        if not self.ticket_nav_account_filter_dialog:
            self.ticket_nav_account_filter_dialog = MDDialogFilter(
                self.ticket_nav_account_filter,
                self.general_settings['commun_widget']['dialog']['title']['account_filter_name'],
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']
            )
            self.ticket_nav_account_filter_dialog.bind(external_ok_action = self.filter_ticket_nav_account)
        self.ticket_nav_account_filter_dialog.open()

    def filter_ticket_nav_account(self, instance, event):
        self.ticket_nav_account_filter = self.ticket_nav_account_filter_dialog.content_dict
        self.ticket_nav_update()

    def show_ticket_nav_budget_filter(self):
        if not self.ticket_nav_budget_filter_dialog:
            self.ticket_nav_budget_filter_dialog = MDDialogFilter(
                self.ticket_nav_budget_filter,
                self.general_settings['commun_widget']['dialog']['title']['budget_filter_name'],
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']
            )
            self.ticket_nav_budget_filter_dialog.bind(external_ok_action = self.filter_ticket_nav_budget)
        self.ticket_nav_budget_filter_dialog.open()

    def filter_ticket_nav_budget(self, instance, event):
        self.ticket_nav_budget_filter = self.ticket_nav_budget_filter_dialog.content_dict
        self.ticket_nav_update()

    def show_ticket_nav_ticket_state_filter(self):
        if not self.ticket_nav_ticket_state_filter_dialog:
            self.ticket_nav_ticket_state_filter_dialog = MDDialogFilter(
                self.ticket_nav_ticket_state_filter,
                self.general_settings['commun_widget']['dialog']['title']['ticket_state_filter_name'],
                self.general_settings['commun_widget']['buttons']['cancel'],
                self.general_settings['commun_widget']['buttons']['validate']
            )
            self.ticket_nav_ticket_state_filter_dialog.bind(external_ok_action = self.filter_ticket_nav_ticket_state)
        self.ticket_nav_ticket_state_filter_dialog.open()

    def filter_ticket_nav_ticket_state(self, instance, event):
        self.ticket_nav_ticket_state_filter = self.ticket_nav_ticket_state_filter_dialog.content_dict
        self.ticket_nav_update()

    def ticket_nav_update(self):
        self.ids.ticket_list.clear_widgets()
        self.display_indicator_up_to_index_ticket = self.screen_settings['transaction']['number_of_tickets'] 

        account_to_display = [account for account in self.ticket_nav_account_filter.keys()
            if self.ticket_nav_account_filter[account] is True]

        budget_to_display = [budget for budget in self.ticket_nav_budget_filter.keys()
            if self.ticket_nav_budget_filter[budget] is True]

        state_to_display = [state for state in self.ticket_nav_ticket_state_filter.keys()
            if self.ticket_nav_ticket_state_filter[state] is True]

        self.filtered_ticket_info_df = self.screen_manager.ticket_info_df[
            self.screen_manager.ticket_info_df['account_designation'].isin(account_to_display) &
            self.screen_manager.ticket_info_df['budget_designation'].isin(budget_to_display) &
            self.screen_manager.ticket_info_df['ticket_state'].isin(state_to_display)
        ]

        self.add_ticket_to_list(self.filtered_ticket_info_df.iloc[0:(self.display_indicator_up_to_index_ticket-1),:])

    def ticket_nav_switch_account_filter(self, boolean):
        for account in self.ticket_nav_account_filter.keys():
            self.ticket_nav_account_filter[account] = boolean
        
    def ticket_nav_switch_budget_filter(self, boolean):
        for budget in self.ticket_nav_budget_filter.keys():
            self.ticket_nav_account_filter[budget] = boolean

    def ticket_nav_switch_state_filter(self, boolean):
        for state in self.ticket_nav_ticket_state_filter.keys():
            self.ticket_nav_ticket_state_filter[state] = boolean        

    def switch_budget_nav_filter(self, boolean):
        for account in self.budget_nav_account_filter.keys():
            self.budget_nav_account_filter[account] = boolean

    def reset_ticket_nav_filters(self):
        self.ticket_nav_switch_account_filter(True)
        self.ticket_nav_switch_budget_filter(True)
        self.ticket_nav_switch_state_filter(True)

    def in_out_line_scroll(self, instance):
        if self.list_scroll_position == 1:
            self.list_scroll_position = 0
        else:
            self.list_scroll_position = 1

        for item in self.ids.in_out_scroll.children[0].children:
            item.scroll_position = self.list_scroll_position

    def add_to_scroll(self, instance):
        if instance._viewport:
            if instance.vbar[0] * instance._viewport.height <  ListInOutItem().height * 5:
                ticket_to_load_df = self.filtered_ticket_info_df.iloc[
                    self.display_indicator_up_to_index_ticket : (self.display_indicator_up_to_index_ticket * 2 -1),
                    :
                ]

                self.add_ticket_to_list(ticket_to_load_df)

                self.display_indicator_up_to_index_ticket += self.display_indicator_up_to_index_ticket 

    def open_ticket(self, instance):
        print('open ticket details', instance.ticket_id)

        # ticket_screen = TicketScreen(
        #     self.screen_manager,
        #     instance.ticket_id
        # )
        # self.screen_manager.add_widget(ticket_screen)

