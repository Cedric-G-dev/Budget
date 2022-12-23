"""
Register Personal widgets to use without import.
"""

from kivy.factory import Factory

register = Factory.register
#widgets
register("MyTextField", module="design.widgets.MyTextField")
register("MDDialogDate", module="design.widgets.MyDialogPicker")
register("MDDialogDayOfMonth", module="design.widgets.MyDialogPicker")
register("LabelAmountListItem", module="design.widgets.MyListItem")
register("BillLine", module="design.widgets.MyListItem")
register("ListInOutItem", module="design.widgets.MyListItem")
register("AccountAbstract", module="design.widgets.MyAbstract")
register("BudgetAbstract", module="design.widgets.MyAbstract")
register("CancelOkButtons", module="design.widgets.MyButton")
register("RepartitionGraph", module="design.widgets.MyGraph")

#screens