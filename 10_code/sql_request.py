def main():
    pass

if __name__ == "__main__":
    print('file not intended to be run, it only contains FULL sql request')

#SQL Table creation requests
#TODO: each time a new account is inserted, create IN PYTHON 
#   a corresponding pending budget : '[new_account]_tmp'

create_table_account ='''
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER NOT NULL PRIMARY KEY,
            designation TEXT NOT NULL UNIQUE,
            credit_card INTEGER,
            checkbook INTEGER,
            bank_transfer INTEGER);
        '''

create_table_budget = '''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER NOT NULL PRIMARY KEY,
            designation TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL);
        '''

create_table_historic_budget = '''
        CREATE TABLE IF NOT EXISTS historic_budget (
            id INTEGER NOT NULL PRIMARY KEY,
            update_date TEXT NOT NULL,            
            id_budget INTEGER NOT NULL,
            id_account INTEGER NOT NULL,
            cap FLOAT NOT NULL,
            note TEXT,
            FOREIGN KEY (id_budget)
                REFERENCES budget (id),
            FOREIGN KEY (id_account)
                REFERENCES account (id));
        '''

create_table_expense = '''
        CREATE TABLE IF NOT EXISTS expense (
            id INTEGER NOT NULL PRIMARY KEY,
            designation TEXT NOT NULL UNIQUE);
        '''

create_table_historic_expense = '''
        CREATE TABLE IF NOT EXISTS historic_expense (
            id INTEGER NOT NULL PRIMARY KEY,
            update_date TEXT NOT NULL,
            id_expense INTEGER NOT NULL,
            id_budget INTEGER NOT NULL,
            amount REAL,
            note TEXT,
            payment_date INTEGER,
            FOREIGN KEY (id_expense)
                REFERENCES expense (id),
            FOREIGN KEY (id_budget)
                REFERENCES budget (id));
        '''

create_table_ticket = '''
        CREATE TABLE IF NOT EXISTS ticket (
            id INTEGER NOT NULL PRIMARY KEY,
            date TEXT NOT NULL,
            recipient TEXT NOT NULL,
            reason TEXT NOT NULL,
            transaction_type INTEGER NULL,
            payment_type TEXT NOT NULL,
            amount FLOAT NOT NULL,
            ticket_state INTEGER NOT NULL,
            note TEXT);    
        '''

create_table_ticket_affectation = '''
        CREATE TABLE IF NOT EXISTS ticket_affectation (
            id_ticket INTEGER NOT NULL,
            id_budget INTEGER NOT NULL,
            budget_affectation_cost FLOAT NOT NULL,
            FOREIGN KEY (id_budget)
                REFERENCES budget (id),
            FOREIGN KEY (id_ticket)
                REFERENCES ticket (id)
            PRIMARY KEY(id_ticket, id_budget));  
        '''

#SQL Instance creation requests       
create_black_hole_account = '''
    INSERT INTO account 
        (designation, credit_card, checkbook, bank_transfer)
    VALUES
        ('black_hole', 0 , 0, 0);
    '''

create_1st_bank_account = '''
    INSERT INTO account
        (designation, credit_card, checkbook, bank_transfer)
    VALUES
        ('My Account', 1, 1, 1);
'''

create_black_hole_budget = '''
    INSERT INTO budget
        (designation, color)
    VALUES
        ('black_hole', '0, 0, 0, 0');
'''

create_pending_budget = '''
    INSERT INTO budget
        (designation, color)
    VALUES
        ('pending', '0, 0, 0, 0');
'''

#cap is not null so cap added
linking_pending_budget_to_1st_account = '''
    INSERT INTO historic_budget
        (update_date, id_budget, id_account, cap, note)
    VALUES
        ({}, 2, 2, 1000000, 'initialization');
'''