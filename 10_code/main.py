from datetime import datetime
import sqlite3
import sql_request

from kivymd.app import MDApp

dev_path = 'C:\\Users\\cguimier\\Documents\\00_App_gestion\\10_code\\'

#list of variable
payment_type  = ['cb', 'checkbook', 'bank_transfert']
boolean = [0, 1]

#TODO : get db_path from db_name (info in json after db creation?)
#TODO : secure connection with password?
# !!! type de donnée sqlite pour nombre à virgule!!
def DB_connection(db_name):
    global dev_path
    db_path = dev_path
    try:
        conn = sqlite3.connect(db_path + db_name + '.db')
    except:
        print('Connection error')
    
    return conn

def DB_creation(db_name):
    # create db from sql_request request
    conn = DB_connection(db_name)
    c = conn.cursor()
    with conn:
        c.execute(sql_request.create_table_account)
        c.execute(sql_request.create_table_budget)
        c.execute(sql_request.create_table_historic_budget)
        c.execute(sql_request.create_table_expense)        
        c.execute(sql_request.create_table_historic_expense)
        c.execute(sql_request.create_table_ticket)
        c.execute(sql_request.create_table_ticket_affectation)

        c.execute(sql_request.create_black_hole_account)
        c.execute(sql_request.create_black_hole_budget)

        c.execute(sql_request.create_pending_budget)
        c.execute(sql_request.create_1st_bank_account)

        #transforming into string for use in sql request
        creation_date = '\'' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '\''
        c.execute(sql_request.linking_pending_budget_to_1st_account.format(creation_date))

    conn.close


#function to fetch data
def fetch_data(cursor, table_name, column_name, condition):
    #create list of tuple
    cursor.execute('''
        SELECT * FROM {} WHERE {} = :condition;
        '''.format(table_name, column_name),{
            'condition': condition
    })
    data = cursor.fetchall()

    return data

def fetch_last_historical_data(cursor, table_name, column_name, condition):
    #create a tuple
    cursor.execute('''
        SELECT * FROM {} WHERE {} = :condition ORDER BY datetime(update_date) DESC LIMIT 1;
        '''.format(table_name, column_name),{
            'condition': condition
        })
    data = cursor.fetchone()

    return data

#TODO : add color for account for display (graphics ...)?
#Object definition
class Account():
    def __init__(self,designation,credit_card,checkbook,bank_transfer):
        self.designation = designation
        self.credit_card = credit_card
        self.checkbook = checkbook
        self.bank_transfer = bank_transfer
    
    def add_account_to_db(self,db_name):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
                INSERT INTO account (designation, credit_card, checkbook, bank_transfer)
                VALUES (:designation, :credit_card, :checkbook, :bank_transfer);
                ''',{
                    'designation': self.designation,
                    'credit_card': self.credit_card,
                    'checkbook': self.checkbook,
                    'bank_transfer': self.bank_transfer})
        
        conn.close()
    
    def update_account(self,db_name,id_account):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
                UPDATE account SET
                    designation = '{}',
                    credit_card = {},
                    checkbook = {},
                    bank_transfer = {}                    
                WHERE id = {};
                '''.format(
                    self.designation,
                    self.credit_card,
                    self.checkbook,
                    self.bank_transfer,                    
                    id_account)
                )

        conn.close()

    def delete_account(self,db_name,id_account):
        self.credit_card = 0
        self.checkbook = 0
        self.bank_transfer = 0
        self.update_account(db_name, id_account)


class Budget():
    def __init__(self, designation, color, update_date, account, cap, note):
        self.designation = designation
        self.color = color
        self.update_date = update_date
        self.account = account
        self.cap = cap
        self.note = note

    def add_budget_to_db(self,db_name):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
            INSERT INTO budget (designation, color)
            VALUES (:designation, :color);
            ''', {
                'designation': self.designation,
                'color': self.color}
            )

            id_budget = fetch_data(c, 'budget', 'designation', self.designation)[-1][0]
            id_account = fetch_data(c, 'account', 'designation', self.account)[-1][0]

            c.execute('''
                INSERT INTO historic_budget (update_date, id_budget, id_account, cap, note)
                VALUES (:update_date, :id_budget, :id_account, :cap, :note);
                ''',{
                    'update_date': self.update_date,                    
                    'id_budget': id_budget,
                    'id_account': id_account,
                    'cap': self.cap,
                    'note': self.note})

        conn.close()
    
    def update_budget(self,db_name,id_budget):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
                UPDATE budget SET 
                    designation = '{}',
                    color = '{}'
                WHERE id = {};
                '''.format(self.designation, self.color, id_budget)
            )
        
            id_account = fetch_data(c, 'account', 'designation', self.account)[-1][0]

            c.execute('''
                INSERT INTO historic_budget (update_date, id_budget, id_account, cap, note)
                VALUES (:update_date, :id_budget, :id_account, :cap, :note);
                ''',{
                    'update_date': self.update_date,
                    'id_budget': id_budget,
                    'id_account': id_account,
                    'cap': self.cap,
                    'note': self.note})

        conn.close()            

    def delete_budget(self,db_name,id_budget):
        self.cap = 0
        self.note = 'budget suppression'
        self.account = 'black_hole'
        self.color = '0.2, 0.2, 0.2'
        self.update_budget(db_name, id_budget)
 

class Expense():
    def __init__(self, designation, update_date, budget, amount, note, payment_date):
        self.designation = designation
        self.update_date = update_date        
        self.budget = budget
        self.amount = amount       
        self.note = note
        self.payment_date = payment_date
    
    def add_expense_to_db(self,db_name):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
            INSERT INTO expense (designation)
            VALUES (:designation);
            ''', {
                'designation': self.designation})
  
            id_expense = fetch_data(c, 'expense', 'designation', self.designation)[-1][0]
            id_budget = fetch_data(c, 'budget', 'designation', self.budget)[-1][0]

            c.execute('''
            INSERT INTO historic_expense (update_date, id_expense, id_budget, amount, note, payment_date)
            VALUES (:update_date, :id_expense, :id_budget,:amount, :note, :payment_date);
            ''',{
                'update_date': self.update_date,
                'id_expense': id_expense,
                'id_budget': id_budget,
                'amount': self.amount,
                'note': self.note,
                'payment_date': self.payment_date})

        conn.close()

    def update_expense(self,db_name,id_expense):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
                UPDATE expense SET 
                    designation = '{}'
                WHERE id = {}
                ;'''.format(
                    self.designation,
                    id_expense)
                )

            id_budget = fetch_data(c, 'budget', 'designation', self.budget)[-1][0]

            c.execute('''
            INSERT INTO historic_expense (update_date, id_expense, id_budget, amount, note, payment_date)
            VALUES (:update_date, :id_expense, :id_budget, :amount, :note, :payment_date);
            ''',{
                'update_date': self.update_date,
                'id_expense': id_expense, 
                'id_budget': id_budget,
                'amount': self.amount,
                'note': self.note,
                'payment_date': self.payment_date})

        conn.close()

    def delete_expense(self, db_name, id_expense):
        self.amount = 0
        self.note = 'expense suppression'
        self.budget = 'black_hole'
        self.payment_date = None
        self.update_expense(db_name, id_expense)


class Ticket():
    def __init__(self, date, recipient, reason,transaction_type, payment_type, amount, ticket_state, note, budget_dico):
        self.date = date
        self.recipient = recipient
        self.reason = reason
        #transaction_type:
        # 0: ouput
        # 1: input
        # 2: intern
        self.transaction_type = transaction_type
        self.payment_type = payment_type
        self.amount = amount
        #ticket state:
        # 0: not noticed on real account yet
        # 1: real ticket, observable on account
        # 2: not noticed yet, but possible to delete to regroupe several one with state 2
        #       -> example: expected refill (possible to group to simplify)
        self.ticket_state = ticket_state
        self.note = note
        self.budget_dico = budget_dico

    def add_ticket_to_db(self,db_name):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
            INSERT INTO ticket (date, recipient, reason, transaction_type, payment_type,amount, ticket_state, note)
            VALUES (:date, :recipient, :reason, :transaction_type, :payment_type, :amount, :ticket_state, :note);
            ''', {
                'date': self.date,
                'recipient': self.recipient, 
                'reason': self.reason,
                'transaction_type': self.transaction_type,
                'payment_type': self.payment_type,
                'amount': self.amount,
                'ticket_state': self.ticket_state,
                'note': self.note
            })

            c.execute('''SELECT id FROM ticket ORDER BY id DESC LIMIT 1;''')
            id_ticket = c.fetchone()[-1]

            for budget, money in self.budget_dico.items():                
                id_budget = fetch_data(c, 'budget', 'designation', budget)[-1][0]

                c.execute('''
                INSERT INTO ticket_affectation (id_ticket, id_budget, budget_affectation_cost)
                VALUES (:id_ticket, :id_budget, :budget_affectation_cost);
                ''', {
                    'id_ticket': id_ticket,
                    'id_budget': id_budget,
                    'budget_affectation_cost': money
                })       

        conn.close()

    def update_ticket(self, db_name, id_ticket):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
                UPDATE ticket SET 
                    'date' = '{}',
                    'recipient' = '{}',
                    'reason' = '{}',
                    'transaction_type' = '{}',
                    'payment_type' = '{}',
                    'amount' =  {},
                    'ticket_state' = {},
                    'note' = '{}'
                WHERE id = {};
                '''.format(
                    self.date,
                    self.recipient,
                    self.reason,
                    self.transaction_type,
                    self.payment_type,
                    self.amount,
                    self.ticket_state,
                    self.note,
                    id_ticket)
            )

            c.execute('''DELETE FROM ticket_affectation WHERE id_ticket = :id_ticket;''',{'id_ticket': id_ticket})

            for budget, money in self.budget_dico.items():                
                id_budget = fetch_data(c, 'budget', 'designation', budget)[-1][0]

                c.execute('''
                INSERT INTO ticket_affectation (id_ticket, id_budget, budget_affectation_cost)
                VALUES (:id_ticket, :id_budget, :budget_affectation_cost);
                ''', {
                    'id_ticket': id_ticket,
                    'id_budget': id_budget,
                    'budget_affectation_cost': money
                }) 

        conn.close()

    def delete_ticket(self, db_name, id_ticket):
        conn = DB_connection(db_name)
        c = conn.cursor()
        with conn:
                c.execute('''DELETE FROM ticket WHERE id = :id;''',{'id': id_ticket})
                c.execute('''DELETE FROM ticket_affectation WHERE id_ticket = :id_ticket;''',{'id_ticket': id_ticket})

        conn.close()


#function fetching data of the selected item
#TODO: create a function to return the id cf interface
def current_account_data(db_name, id_account):
    conn = DB_connection(db_name)
    c = conn.cursor()
    with conn:
        current_data = fetch_data(c, 'account', 'id', id_account)[-1]
    
    conn.close()

    current_data_account = Account(current_data[1], current_data[2],current_data[3], current_data[4])
  
    return current_data_account

def current_budget_data(db_name, id_budget):
    conn = DB_connection(db_name)
    c = conn.cursor()
    with conn:
        current_budget_data = fetch_data(c, 'budget', 'id', id_budget)[-1]
        current_budget_historic_data = fetch_last_historical_data(c, 'historic_budget', 'id_budget', current_budget_data[0])
        account_id = current_budget_historic_data[3]
        accout_name = fetch_data(c, 'account', 'id', account_id)[-1][1]

    conn.close()

    current_data_budget = Budget(
        current_budget_data[1],
        current_budget_historic_data[1],
        accout_name,
        current_budget_historic_data[4],
        current_budget_historic_data[5])

    return current_data_budget

def current_expense_data(db_name, id_expense):
    conn = DB_connection(db_name)
    c = conn.cursor()
    with conn:
        current_expense_data = fetch_data(c, 'expense', 'id', id_expense)[-1]
        current_expense_historic_data = fetch_last_historical_data(c, 'historic_expense', 'id_expense', current_expense_data[0])
        budget_id = current_expense_historic_data[3]
        budget_name = fetch_data(c, 'budget', 'id', budget_id)[-1][1]

    conn.close()

    current_data_expense = Expense(
        current_expense_data[1],
        current_expense_historic_data[1],
        budget_name,
        current_expense_historic_data[4],
        current_expense_historic_data[5],
        current_expense_historic_data[6])

    return current_data_expense

def current_ticket_data(db_name, id_ticket):
    conn = DB_connection(db_name)
    c = conn.cursor()
    with conn:
        current_ticket_data = fetch_data(c, 'ticket', 'id', id_ticket)[-1]
        current_ticket_affectation_data = fetch_data(c, 'ticket_affectation', 'id_ticket', id_ticket)

        budget_dico = {}
        id_budget_list = [i[1] for i in current_ticket_affectation_data]
        cost_budget_list = [i[2] for i in current_ticket_affectation_data]
        
        for id_budget, cost_budget in zip(id_budget_list, cost_budget_list):
            budget_name =  fetch_data(db_name, 'budget', 'id', id_budget)[-1][1]
            budget_dico[budget_name] = cost_budget

    conn.close()

    current_data_ticket = Ticket(
        current_ticket_data[1],
        current_ticket_data[2],
        current_ticket_data[3],
        current_ticket_data[4],
        current_ticket_data[5],
        current_ticket_data[6],
        budget_dico)

    return current_data_ticket

def main():
    #DB_creation('test_main')
    pass

if __name__== "__main__":
	main()


### attention traitement de la date, pour linstant ppté de l'objet
