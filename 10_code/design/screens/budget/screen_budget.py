__all__ = ("BudgetScreen",)

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, DictProperty

from design.widgets.MyAbstract import BudgetExpensesExpansion

from design import screens_path


with open(
    os.path.join(screens_path, "budget", "screen_budget.kv"), encoding="utf-8"
) as kv_file:
    Builder.load_string(kv_file.read())


#TODO: when clicking on budget line go to corresponding budget info page
#TODO: amount integer, think with D('XX.YY') definition
class BudgetScreen(Screen):

    #label
    title_separator = StringProperty('Récapitulatif Budget-Dépenses :')

    budgets = DictProperty({
        'Budget1': {'amount' : 1000, 'color' : [1, 0, 0], 'expense': {
                'expense1': 100,
                'expense2': 200,
            }
        },
        'Budget2': {'amount' : 200, 'color' : [1, 0.5, 0], 'expense': {
                'expense3': 300,
            }
        },
        'Budget3': {'amount' : 300, 'color' : [1, 1, 0], 'expense': {
                'expense4': 400,
                'expense5': 500,
            }
        },
        'Budget4': {'amount' : 0, 'color' : [0.5, 0.5, 0],'expense': {
                'expense6': 600,
                'expense7': 700,
            }
        },
        'Budget123456785XXXXXXXXXXXXXX': {'amount' : 150, 'color' : [0.2, 0.2, 0.2], 'expense': {
                'expense8': 800,
            }
        }
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._set_budget_list)

    def _set_budget_list(self, interval):
        for budget, data in self.budgets.items():
            # list_item = BudgetItem(
            #     color = data['color'],
            #     designation = budget,
            #     amount = data['amount']
            # )
            list_item = BudgetExpensesExpansion(
                budget_designation = budget,
                budget_dict = data,
            )
            self.ids.budget_list.add_widget(list_item)

    def create_new_budget(self):
        print('got to page to create new budget')

