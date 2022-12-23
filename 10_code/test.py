from kivymd.app import MDApp
from kivy.lang import Builder
from datetime import datetime, date
import design
from decimal import Decimal as D
from design.widgets.MyExpansionItem import ExpansionScrollItem

screen_helper = '''
BoxLayout:
    orientation: 'vertical'
    Button:
        text: 'Button1'
        on_press: app._set_recursion_widget(root)
    Button:
        text: 'Button2'
        on_release :app._set_recursion_widget(root)
'''

#General
class MyApp(MDApp):
    Account_Budget_bill = {
            'compte1' : {'budget1' : D('100.00'), 'budget2' :  False, 'compte1_tmp': False},
            'compte2' : {'budget3' :  False, 'budget4' : False},
            'compte3' : {'budget5' : D('100.00'), 'budget6' :  D('100.00'),
                'budget7' : False},
            'compte4' : {'budget8': False} 
        }
    icon_list = ['database-search', 'bank', 'database']

    def _set_recursion_widget(self, instance):
        for account, account_dict in self.Account_Budget_bill.items():
            recursion_widget = ExpansionScrollItem(
                data_recursion = account_dict,
                icon_recursion = self.icon_list[1:],
                text = account,
                item_icon = self.icon_list[0]                
            )
            instance.add_widget(recursion_widget)  

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'LightGreen'        
        screen = Builder.load_string(screen_helper)
        return screen
    
 

if __name__ == '__main__':
    MyApp().run()
