from distutils import config
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window

from datetime import datetime, date
from locale import setlocale, LC_TIME

from functools import partial
from decimal import Decimal as D
import numpy as np
import pandas as pd

import main as DB
#import that register deisng for kv usage
from design.screens.connection import ConnectionScreen
from design.screens.home import HomeScreen
from design.screens.ticket import TicketScreen
from design.screens.ticket_affectation import TicketAffectationScreen
from design.screens.budget import BudgetScreen
from design.screens.budget_configuration import BudgetConfigurationScreen
from design.screens.event import EventScreen

#import function
from design.widget_functions import number_input_control

#configuration
from design.config import app_config


Window.clearcolor = (1, 0, 1, 1)
Window.size = (app_config['general_settings']['window_width'], app_config['general_settings']['window_height'])
setlocale(LC_TIME, app_config['general_settings']['time_format'])
AmountFormat = D(app_config['general_settings']['AmountFormat_string'])

#TODO CRITICAL : storing float value in DB as DECIMAL(X,2)
# --> change main  but check https://stackoverflow.com/a/6319513
# or string

#TODO: Ecran dépense parametrage
#TODO: Si données existes, créer un bouton pour accéder à l'historique (note, montant ...)
#bug effacement montant budget


#General notes
#TODO: create page for help, appli description
#TODO: care about account name
#TODO: check navigationdrawer when select, text in black, height
#TODO: check ToolBar height
#TODO: add color attribute to account so that account and budget have the same color
#TODO: connect db to pandas ?
#TODO: use MDFloattingActionButton (FAB) for princpal action for on screen page (ex gestion budget)
#TODO: Check if PR needed to update button size as texte changes
#TODO: create mode to access mock data, to present the app without exposing 
#       one's own data
#TODO: create page with mail to give feedback

#TODO: create expense page, allow automatic ticket creation from event on defined date
#       where expense designation = ticket reason
#TODO: clean _create_data_for_screens, supress self for useless temp df
class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.today = date.today()
        self.current_month = self.today.month
        self.current_year = self.today.year
        self._initiliaze_data()
        self._create_data_for_screens()

    def _initiliaze_data(self):
        #Creation of mock data in dataframe
        #change to load from SQLITE DataBase

        #Jupyter n°2
        self.account_df = pd.DataFrame.from_dict({
            'id_account' : [1, 2, 3],
            'designation': ['compte courant', 'livret A', 'SwissLife'],
            'credit_card': [1, 0, 0],
            'checkbook': [1, 0, 0],
            'bank_transfer': [1, 1, 1]
        })
        #Jupyter n°3
        self.budget_df = pd.DataFrame.from_dict({
            'id_budget': [1, 2, 3, 4],
            'designation': ['charges', 'loisir perso', 'Securite', 'Placement long terme'],
            'id_account': [1, 1, 2, 3],
            'cap': [D('1000.00'), D('700.00'), D('5000.00'), D('1000.00')],
            'note': ['transactions courantes du mois', 'cadeau perso', 'montant de sécurité accessible', ''],
            'color': [[1,0,0,1], [0,1,0,1], [0,0,1,1], [1,0.5,0.5,1]]
        })

        #Jupyter n°4
        #creation of transitionnal budget for each account, used to get input event such as salary, and used for temp tickets
        max_id_budget = self.budget_df['id_budget'].max()
        for index, account in self.account_df.iterrows():
            transitionnal_budget_account_df = pd.DataFrame.from_dict({
                'id_budget': max_id_budget + index + 1,
                'designation': 'transtion' + ' ' + account['designation'],
                'id_account': account['id_account'],
                'cap': None,
                'note': 'budget de transit pour le compte' + ' ' + account['designation'],
                'color': [[0,1,0,1]]        
            })
            self.budget_df = pd.concat([self.budget_df, transitionnal_budget_account_df], ignore_index=True)        

        #Jupyter n°5
        self.monthly_event_df = pd.DataFrame.from_dict({
                'id_event': [1, 2, 3, 4, 5],
                'designation': ['internet', 'navigo', 'salaire', 'Placement securitaire', 'PlacementSwissLife'],
                'amount': [D('20.00'), D('70.00'), D('2500'), D('100.00'), D('160.00')],
                'id_transaction_type': [1, 1, 2, 3, 3],
                'id_from_budget': [1, 1, 0, 5, 5],
                'id_to_budget': [0, 0, 5, 3, 4],
                'note': ['', 'remboursement 50% employeur', '', 'renflouement securite', 'Assurance vie'],
                'payment_day': [10, 27, 5, 15, 5],   
        })
        #Jupyter n°6
        self.Transaction_type_df = pd.DataFrame.from_dict({
            'id_transaction_type': [1, 2, 3],
            'transaction_type': ['Sortie', 'Entrée', 'Interne']
        })
        #Jupyter n°7
        self.ticket_state_df = pd.DataFrame.from_dict({
            'id_ticket_state': [1, 2, 3],
            'ticket_state': ['A jour', 'En attente', 'En attente - virtuel']
        })        
        #Jupyter n°8
        self.ticket_df = pd.DataFrame.from_dict({
            'id_ticket': range(1,13),
            'date': [
                '20/12/2022',
                '2/10/2022',
                '3/10/2022',
                '4/10/2022',
                '5/10/2022',
                '6/10/2022',
                '7/11/2022',
                '8/10/2022',
                '9/12/2022',
                '2/10/2022',
                '01/01/2022',
                '03/12/2022'],
            'recipient': [
                'Auchan',
                'Maboite',
                'LeClerc',
                'Fnac',
                'Boulanger',
                'Commun',
                'AuchanDrive',
                'Amazone',
                'SwissLife',
                'VandB',
                'Perso',
                'Expleo'
            ],
            'reason': [
                'vêtement',
                'salaire',
                'course',
                'livre',
                'ordinateur',
                'virement mensuel',
                'course',
                'carte decorative',
                'placement',
                'sortie apéro',
                'initialisation',
                'salaire decembre'
            ],
            'id_event': [0, 3,0, 0, 0, 4, 0, 0, 5, 0, 0, 3],
            'id_transaction_type': [1, 2, 1, 1, 1, 3, 1, 1, 1, 1, 2, 2],
            'amount': [
                D('45.00'),
                D('2195.00'),
                D('112.12'),
                D('8.96'),
                D('1245.99'),
                D('1000.00'),
                D('44.99'),
                D('30'),
                D('40.00'),
                D('36.00'),
                D('17000.00'),
                D('2500.00')
            ],
            'id_account': [1, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1, 1],
            'id_ticket_state': [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 3],
            'note': ['', '', '', '', '','','','','','', '', '']
        })
        self.ticket_df['date'] = pd.to_datetime(self.ticket_df['date'], dayfirst = True)
        self.ticket_df['date'] = self.ticket_df['date'].dt.date
        #Jupyter n°9
        self.ticket_affectation_df = pd.DataFrame.from_dict({
            'id_ticket_affectation': range(1,18),
            'id_ticket': [1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10, 10, 11, 11, 11, 11, 12],
            'id_budget': [1, 5, 1, 1, 3, 5, 4, 1, 1, 4, 2, 1, 1, 2, 3, 4, 5],
            'budget_affectation':[
                D('89.00'),
                D('2195.00'),
                D('112.12'),
                D('8.96'),
                D('1245.99'),
                D('-1000.00'),
                D('1000.00'),
                D('44.99'),
                D('20.00'),
                D('71.00'),
                D('16.00'),
                D('16.00'),
                D('1500'),
                D('5000.00'),
                D('7000.00'),
                D('10000.00'),
                D('2500.00')
            ]
        })

    def _create_data_for_screens(self):
        #create base df for ticket analysis

        #Jupyter n°10
        self.transaction_df = pd.merge(
            self.ticket_affectation_df,
            self.ticket_df[['id_ticket','date','id_transaction_type','id_ticket_state','id_event']],
            how = 'inner',
            left_on = 'id_ticket',
            right_on = 'id_ticket'
        )

        self.transaction_df['budget_affectation'] = np.where(
            self.transaction_df['id_transaction_type'] == 1,
            - self.transaction_df['budget_affectation'],
            self.transaction_df['budget_affectation']
)
        #Jupyter n°11
        #compute budget amount at the end of the previous month
        self.budget_last_month_amount_df = self.transaction_df[self.transaction_df['date'] < self.today.replace(day = 1)].groupby(['id_budget']).agg({'budget_affectation': 'sum'})
        #compute current budget amount
        self.budget_current_amount_df = self.transaction_df.groupby(['id_budget']).agg({'budget_affectation': 'sum'})
        #regroup budget amount analysis
        self.budget_abstract_df = pd.merge(
            self.budget_last_month_amount_df.rename(columns = {'budget_affectation': 'end_of_last_month_budget_amount'}),
            self.budget_current_amount_df.rename(columns = {'budget_affectation': 'budget_amount'}),
            how = 'outer',
            left_on = 'id_budget',
            right_on = 'id_budget'
        )
        #Jupyter n°12
        #compute month output budget
        self.budget_month_expense_df = - self.transaction_df[
            (self.transaction_df['date'] >= self.today.replace(day = 1)) &
            (self.transaction_df['budget_affectation'] < 0)
        ].groupby(['id_budget']).agg({'budget_affectation': 'sum'})

        self.budget_abstract_df = pd.merge(
            self.budget_abstract_df,
            self.budget_month_expense_df.rename(columns = {'budget_affectation': 'budget_month_expense'}),
            how = 'outer',
            left_on = 'id_budget',
            right_on = 'id_budget'
        )
        #Jupyter n°13
        #compute current updated amount of budget
        self.budget_updated_status_df = self.transaction_df[self.transaction_df['id_ticket_state'] == 1].groupby(['id_budget']).agg({'budget_affectation': 'sum'}) 

        self.budget_abstract_df = pd.merge(
            self.budget_abstract_df,
            self.budget_updated_status_df.rename(columns = {'budget_affectation': 'budget_updated_amount'}),
            how = 'outer',
            left_on = 'id_budget',
            right_on = 'id_budget'  
        )
        #Jupyter n°14
        #compute the amount that have not been paid yet based on expenditure
        self.event_during_month_df = self.transaction_df[['id_event', 'date']][
            (self.transaction_df['date'] >= self.today.replace(day = 1))
            & ~(self.transaction_df['id_event'].isnull())]
        #Jupyter n°15
        self.expected_event_df = pd.merge(
            self.monthly_event_df,
            self.event_during_month_df.rename(columns = {'id_event': 'id_happened_event'}),    
            how = 'left',
            left_on ='id_event',
            right_on ='id_happened_event'
        )
        self.expected_event_df = self.expected_event_df[self.expected_event_df['id_happened_event'].isnull()]
        #Jupyter n°16
        self.cumul_of_expected_input_df = + self.expected_event_df.groupby(['id_to_budget']).agg({'amount': 'sum'})
        self.cumul_of_expected_input_df['id_budget'] = self.cumul_of_expected_input_df.index

        self.cumul_of_expected_output_df = - self.expected_event_df.groupby(['id_from_budget']).agg({'amount': 'sum'})
        self.cumul_of_expected_output_df['id_budget'] = self.cumul_of_expected_output_df.index

        self.cumul_of_expected_event_df = pd.concat([self.cumul_of_expected_input_df, self.cumul_of_expected_output_df])
        self.cumul_of_expected_event_df = self.cumul_of_expected_event_df.groupby(['id_budget'], as_index = False).agg({'amount': 'sum'})

        self.cumul_of_expected_event_df = self.cumul_of_expected_event_df[self.cumul_of_expected_event_df['id_budget'] != 0]        

        #Jupyter n°17
        self.budget_abstract_df = pd.merge(
            self.budget_abstract_df,
            self.cumul_of_expected_event_df.rename(columns = {'amount': 'currently_expected_amount'}),
            how = 'outer',
            left_on = 'id_budget',
            right_on = 'id_budget'  
        )
        #Jupyter n°18
        self.cumul_of_event_input_df = + self.monthly_event_df.groupby(['id_to_budget']).agg({'amount': 'sum'})
        self.cumul_of_event_input_df['id_budget'] = self.cumul_of_event_input_df.index
        #Jupyter n°19
        self.cumul_of_event_output_df = - self.monthly_event_df.groupby(['id_from_budget']).agg({'amount': 'sum'})
        self.cumul_of_event_output_df['id_budget'] = self.cumul_of_event_output_df.index
        #Jupyter n°20
        self.cumul_of_event_df = pd.concat([self.cumul_of_event_input_df, self.cumul_of_event_output_df])
        self.cumul_of_event_df = self.cumul_of_event_df.groupby(['id_budget'], as_index = False).agg({'amount': 'sum'})

        self.cumul_of_event_df = self.cumul_of_event_df[self.cumul_of_event_df['id_budget'] != 0]
        #Jupyter n°21
        self.budget_data_prevision_df = pd.merge(
            self.budget_df[['id_budget','designation','id_account' ,'cap', 'color']],
            self.cumul_of_event_df.rename(columns = {'amount': 'monthly_expected_balance'}),
            how = 'left',
            left_on = 'id_budget',
            right_on = 'id_budget'  
        )
        #Jupyter n°22
        self.budget_monthly_output_df = self.cumul_of_event_output_df.rename(columns = {'amount': 'monthly_output_amount'})
        self.budget_monthly_output_df['monthly_output_amount'] = - self.budget_monthly_output_df['monthly_output_amount']

        self.budget_data_prevision_df = pd.merge(
            self.budget_data_prevision_df,
            self.budget_monthly_output_df,
            how = 'left',
            left_on = 'id_budget',
            right_on = 'id_budget'  
        )
        #Jupyter n°23
        self.budget_data_prevision_df = pd.merge(
            self.budget_data_prevision_df,
            self.cumul_of_event_input_df.rename(columns = {'amount': 'monthly_input_amount'}),
            how = 'left',
            left_on = 'id_budget',
            right_on = 'id_budget'  
        )
        self.budget_data_prevision_df.replace(np.nan, D('0.00'), inplace = True)        
        #Jupyter n°24
        self.budget_data_df = pd.merge(
            self.budget_data_prevision_df,
            self.budget_abstract_df,
            how = 'left',
            left_on = 'id_budget',
            right_on = 'id_budget'
        )
        self.budget_data_df.replace(np.NaN, D('0.00'), inplace = True)
        #Jupyter n°25
        self.account_data_df = self.budget_data_df.groupby(['id_account']).agg({
            'monthly_expected_balance': 'sum',
            'currently_expected_amount': 'sum',
            'budget_amount': 'sum',
            'monthly_output_amount': 'sum',
            'budget_updated_amount': 'sum',
            'budget_month_expense': 'sum'})
        self.account_data_df.rename(columns = {
            'monthly_expected_amount': 'month_balance',
            'currently_expected_amount': 'yet_to_happen',
            'budget_amount': 'real_amount',
            'budget_updated_amount': 'bank_amount',
            'budget_month_expense': 'month_expenditure'
            }, inplace = True)

        self.account_data_df['account_status'] = np.where(
            (self.account_data_df['bank_amount'] + self.account_data_df['yet_to_happen']) > 0,
            0,
            np.where(
                    (self.account_data_df['bank_amount'] + self.account_data_df['yet_to_happen']) == 0,
                    1,
                    0
            )        
        )
        #Jupyter n°26
        self.account_info_df = pd.merge(
            self.account_df,
            self.account_data_df,
            how = 'left',
            left_on = 'id_account',
            right_on = 'id_account'
        )
        self.account_info_df.replace(np.NaN, D('0.00'), inplace = True)
        #Jupyter n°27
        self.budget_info_df = pd.merge(
            self.budget_data_df,
            self.account_info_df[['id_account', 'designation', 'account_status']].rename(columns = {'designation': 'account_designation'}),
            how = 'left',
            left_on = 'id_account',
            right_on = 'id_account'
        )
        self.budget_info_df.replace(np.NaN, D('0.00'), inplace = True)
        #Jupyter n°28
        self.ticket_affectation_mono_budget_df = self.ticket_affectation_df.groupby(['id_ticket']).agg({
            'id_ticket_affectation': 'count',
                'id_budget': 'sum'
        })
        self.ticket_affectation_mono_budget_df = self.ticket_affectation_mono_budget_df.rename(columns = {'id_ticket_affectation': 'number_of_budget'})
        self.ticket_affectation_mono_budget_df['id_ticket'] = self.ticket_affectation_mono_budget_df.index      
        #Jupyter n°29
        self.ticket_affectation_mono_budget_df = pd.merge(
            self.ticket_affectation_mono_budget_df[
                self.ticket_affectation_mono_budget_df['number_of_budget'] == 1],
            self.budget_df[['id_budget', 'designation', 'color']],
            how = 'left',
            left_on = 'id_budget',
            right_on = 'id_budget'
        )
        self.ticket_affectation_mono_budget_df = self.ticket_affectation_mono_budget_df.rename(columns = {'designation': 'budget_designation', 'color': 'budget_color'})
        #Jupyter n°30
        self.ticket_simple_info_df = pd.merge(
            self.ticket_df[['id_ticket', 'date', 'recipient', 'reason', 'amount', 'id_transaction_type', 'id_ticket_state', 'id_account']],
            self.ticket_affectation_mono_budget_df[['id_ticket','id_budget', 'budget_designation', 'budget_color']],
            how = 'inner',
            left_on = 'id_ticket',
            right_on = 'id_ticket'
        )
        #Jupyter n°31
        self.budget_complexe_df = pd.DataFrame.from_dict({
            'id_budget': 0,
            'budget_designation': 'multi-budgets',
            'budget_color': [[1.0, 1.0, 1.0, 1.0]]
        })
        self.ticket_complexe = self.ticket_df[~self.ticket_df['id_ticket'].isin(self.ticket_simple_info_df['id_ticket'])]
        self.ticket_complexe['id_budget'] = 0

        self.ticket_complexe_info_df = pd.merge(
            self.ticket_complexe[['id_ticket', 'date', 'recipient', 'reason', 'amount', 'id_transaction_type', 'id_ticket_state','id_budget', 'id_account']],
            self.budget_complexe_df,
            how = 'inner',
            left_on = 'id_budget',
            right_on = 'id_budget'
        )
        #Jupyter n°32
        self.ticket_global_df = pd.concat([self.ticket_simple_info_df, self.ticket_complexe_info_df])
        self.ticket_global_info_df = pd.merge(
            self.ticket_global_df,
            self.account_df[['id_account', 'designation']].rename(columns= {'designation': 'account_designation'}),
            how = 'left',
            left_on = 'id_account',
            right_on = 'id_account'
        )        
        #Jupyter n°33
        self.ticket_info_temp_df = pd.merge(
            self.ticket_global_info_df,
            self.ticket_state_df,
            how = 'left',
            left_on = 'id_ticket_state',
            right_on = 'id_ticket_state'
        )

        self.ticket_info_df = pd.merge(
            self.ticket_info_temp_df,
            self.Transaction_type_df,
            how = 'left',
            left_on = 'id_transaction_type',
            right_on = 'id_transaction_type'
        )


        self.ticket_info_df = self.ticket_info_df.sort_values(by= ['date'], ascending = False)

        self.ticket_info_df['signed_amount'] = np.where(
            self.ticket_info_df['id_transaction_type'] == 1,
            - self.ticket_info_df['amount'],
            self.ticket_info_df['amount']
        )
        self.ticket_info_df['id_budget'].replace(np.NaN, 0, inplace = True)
        self.ticket_info_df = self.ticket_info_df.reset_index(drop = True)
    

#General
class MyApp(MDApp):
    def build(self):
        self.theme_cls.material_style = app_config['general_settings']['material_style']
        self.theme_cls.theme_style = app_config['general_settings']['theme_style']
        self.theme_cls.primary_palette = app_config['general_settings']['primary_palette']
        self.theme_cls.primary_hue = app_config['general_settings']['primary_hue']
        self.title = app_config['general_settings']['title']

        self.complementary_palet = app_config['general_settings']['complementary_color']

        screen_manager = MyScreenManager()
        # connection_screen = ConnectionScreen()
        # home_screen = HomeScreen(screen_manager)
        ticket_screen = TicketScreen(screen_manager = screen_manager)
        # ticket_affectation_screen = TicketAffectationScreen()
        # budget_screen = BudgetScreen()
        # # budget_configuration_screen = BudgetConfigurationScreen()
        # event_sceen = EventScreen()

        # screen_manager.add_widget(event_sceen)
        # screen_manager.add_widget(budget_configuration_screen)
        # screen_manager.add_widget(budget_screen)
        # screen_manager.add_widget(ticket_affectation_screen)
        screen_manager.add_widget(ticket_screen)
        #screen_manager.add_widget(home_screen)
        # screen_manager.add_widget(connection_screen)

        return screen_manager

#Data for test
#TODO: add amount column to budget
data = {'ID': [1, 2, 3],
    'designation': ['Expense1', 'Expense2', 'Expense3']
}
TEST_expense_data = pd.DataFrame(data)

if __name__ == '__main__':
    MyApp().run()

