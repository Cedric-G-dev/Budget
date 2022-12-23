#configuration
from .config import app_config

# Regroup function called accross different widget
from decimal import Decimal as D


#controle number input display and value in textfield
def number_input_control(widget_instance, value_format = app_config['general_settings']['AmountFormat_string']):
    if widget_instance.text == '':
        controlled_amount = D('0.00')
    else:
        controlled_amount = D(widget_instance.text).quantize(D(value_format))
    
    widget_instance.text = str(controlled_amount)
    
    return controlled_amount