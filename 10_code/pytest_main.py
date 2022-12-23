import main as script
import sqlite3


# TO DO : improve message display with logging
'''
test to realize:
1- db creation
for each table
    a) insertion
    b) update
    c) delete
'''


class Test_db():
    def setup_method(self):
        self.test_tmp_dir = script.dev_path + 'test\\'
        self.test_db_name = 'test'
        self.test_db_table = [
            'account',
            'budget',
            'historic_budget',
            'expense',
            'historic_expense',
            'ticket',
            'ticket_affectation']

    def teardown_method(self):
        pass

    def test_db_creation(self):
        script.DB_creation(self.test_db_name)
        conn = script.DB_connection(self.test_db_name)
        c = conn.cursor()
        with conn:
            c.execute('''
                select name from sqlite_master where type = "table" ORDER BY name;
            ''')
            table_db = c.fetchall()
        conn.close

        table_list_db  = [i[0] for i in table_db]
        self.test_db_table.sort()
        assert self.test_db_table == table_list_db
        # check to do
        print('\ntest 1 : DB successfully created')


class Test_account():
    def setup_method(self):
        self.db = 'test'
        self.designation = 'test_account'
        self.credit_card = 1
        self.checkbook = 1
        self.bank_transfer = 1

    def teardown_method(self):
        pass

    def test_add_account(self):
        test_account = script.Account(self.designation,self.credit_card,self.checkbook,self.bank_transfer)
        test_account.add_account_to_db(self.db)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'account', 'designation', self.designation)[-1])
            id_account_test = data[0]
        conn.close

        input_list = [id_account_test, self.designation, self.credit_card, self.checkbook, self.bank_transfer]
        assert input_list == data
        # check to do
        print('\ntest 2 : Account instance successfully created')

    def test_update_account(self):
        id_account_to_update = 3

        designation = 'compte_update_test'
        credit_card = 0
        checkbook = 0
        bank_transfer = 0

        test_account_update = script.Account(designation, credit_card, checkbook, bank_transfer)
        test_account_update.update_account(self.db, id_account_to_update)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'account', 'designation', designation)[-1])
        conn.close

        input_list = [id_account_to_update, designation, credit_card, checkbook, bank_transfer]
        
        assert input_list == data

        # check to do
        print('\ntest 3 : Account instance successfully updated')

    def test_delete_account(self):
        id_acount_to_delete = 3

        test_account = script.Account(self.designation,self.credit_card,self.checkbook,self.bank_transfer)
        test_account.delete_account(self.db, id_acount_to_delete)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'account', 'designation', self.designation)[-1])
        conn.close

        input_list = [id_acount_to_delete, self.designation, 0, 0, 0]

        assert input_list == data

        # check to do
        print('\ntest 4 : Account instance successfully deleted')


class Test_budget():
    def setup_method(self):
        self.db = 'test'
        self.designation = 'budget_test'
        self.color = '1, 0, 0'
        self.update_date = '2021-01-31 12:30:10'
        self.account = 'black_hole'
        self.cap = 100
        self.note = ''

    def teardown_method(self):
        pass

    def test_add_budget(self):
        test_budget = script.Budget(self.designation, self.color, self.update_date, self.account, self.cap, self.note)
        test_budget.add_budget_to_db(self.db)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            id_budget_test = script.fetch_data(c, 'budget', 'designation', self.designation)[-1][0]
            id_account_test = script.fetch_data(c, 'account', 'designation', self.account)[-1][0]

            data = list(script.fetch_data(c, 'budget', 'designation', self.designation)[-1])

            data_histo = list(script.fetch_last_historical_data(c, 'historic_budget', 'id_budget', id_budget_test))
            data_histo = data_histo[-5:]

        conn.close

        input_list_1 = [id_budget_test, self.designation, self.color]
        input_list_2 = [self.update_date, id_budget_test, id_account_test, self.cap, self.note]

        assert input_list_1 == data and input_list_2 == data_histo
        # check to do
        print('\ntest 5 : Budget instance successfully created')

    def test_update_budget(self):
        id_budget_to_update = 3

        designation = 'budget_test_update'
        color = '1, 1, 1'
        update_date = '2021-02-31 12:30:10'
        account = 'My Account'
        cap = 200        
        note = ''

        test_budget_update = script.Budget(designation, color, update_date, account, cap, note)
        test_budget_update.update_budget(self.db, id_budget_to_update)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            id_account_test = script.fetch_data(c, 'account', 'designation', account)[-1][0]

            data = list(script.fetch_data(c, 'budget', 'designation', designation)[-1])
            id_budget_test = data[0]

            data_histo = list(script.fetch_last_historical_data(c, 'historic_budget', 'id_budget', id_budget_test))
            data_histo = data_histo[-5:]

        conn.close

        input_list_1 = [id_budget_to_update, designation, color]
        input_list_2 = [update_date, id_budget_to_update, id_account_test, cap, note]

        assert input_list_1 == data and input_list_2 == data_histo

        # check to do
        print('\ntest 6 : Budget instance successfully updated')

    def test_delete_budget(self):
        id_budget_to_delete = 3

        delete_date = '2021-03-31 12:30:10'
        designation = 'budget_test_update'

        test_budget = script.Budget(designation, self.color, delete_date, self.account, self.cap, self.note)
        test_budget.delete_budget(self.db, id_budget_to_delete)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'budget', 'designation', designation)[-1])
            id_budget_test = data[0]

            data_histo = list(script.fetch_last_historical_data(c, 'historic_budget', 'id_budget', id_budget_test))
            data_histo = data_histo[-5:]

        conn.close

        input_list_1 = [id_budget_to_delete, designation, '0.2, 0.2, 0.2']
        input_list_2 = [delete_date, id_budget_to_delete, 1, 0, 'budget suppression']

        assert input_list_1 == data and input_list_2 == data_histo

        # check to do
        print('\ntest 7 : Budget instance successfully deleted')

        
class Test_expense():
    def setup_method(self):
        self.db = 'test'
        self.designation = 'expense_test'
        self.update_date = '2021-01-31 12:00:00'
        self.budget = 'black_hole'
        self.amount = 100     
        self.note = ''
        self.payment_date = None

    def teardown_method(self):
        pass

    def test_add_expense(self):
        test_expense = script.Expense(self.designation, self.update_date, self.budget, self.amount, self.note, self.payment_date)
        test_expense.add_expense_to_db(self.db)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            id_budget = script.fetch_data(c, 'budget', 'designation', self.budget)[-1][0]

            data = list(script.fetch_data(c, 'expense', 'designation', self.designation)[-1])
            id_expense_test = data[0]

            data_histo = list(script.fetch_last_historical_data(c, 'historic_expense', 'id_expense', id_expense_test))
            data_histo = data_histo[-6:]

        conn.close

        input_list_1 = [id_expense_test, self.designation]
        input_list_2 = [self.update_date, id_expense_test, id_budget, self.amount, self.note, self.payment_date]


        assert input_list_1 == data and input_list_2 == data_histo
        # check to do
        print('\ntest 8 : Expense instance successfully created')

    def test_update_expense(self):
        id_expense_to_update = 1

        designation = 'expense_test_update'
        update_date = '2021-02-31 12:30:10'
        budget = 'pending'
        amount = 200
        note = ''
        payment_date = 15

        test_expense = script.Expense(designation, update_date, budget, amount, note, payment_date)
        test_expense.update_expense(self.db, id_expense_to_update)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            id_budget = script.fetch_data(c, 'budget', 'designation', budget)[-1][0]

            data = list(script.fetch_data(c, 'expense', 'designation', designation)[-1])
            id_expense_test = data[0]

            data_histo = list(script.fetch_last_historical_data(c, 'historic_expense', 'id_expense', id_expense_test))
            data_histo = data_histo[-6:]
            
        conn.close

        input_list_1 = [id_expense_to_update, designation]
        input_list_2 = [update_date, id_expense_to_update, id_budget, amount, note, payment_date]


        assert input_list_1 == data and input_list_2 == data_histo
        # check to do
        print('\ntest 9 : Expense instance successfully updated')

    def test_delete_expense(self):
        id_expense_to_delete = 1

        delete_date = '2021-03-31 12:30:10'

        test_expense = script.Expense(self.designation, delete_date, self.budget, self.amount, self.note, self.payment_date)
        test_expense.delete_expense(self.db, id_expense_to_delete)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'expense', 'designation', self.designation)[-1])
            id_expense_test = data[0]

            data_histo = list(script.fetch_last_historical_data(c, 'historic_expense', 'id_expense', id_expense_test))
            data_histo = data_histo[-6:]
        conn.close

        input_list_1 = [id_expense_to_delete, self.designation]
        input_list_2 = [delete_date, id_expense_to_delete, 1, 0, 'expense suppression', None]


        assert input_list_1 == data and input_list_2 == data_histo
        # check to do
        print('\ntest 10 : Expense instance successfully deleted')


class Test_tiket():
    def setup_method(self):
        self.db = 'test'
        self.date = '2021-01-31 12:00:00'
        self.recipient = 'recipient_test'
        self.reason = 'reason_test'
        self.transaction_type = 0
        self.payment_type = script.payment_type[0]
        self.amount = 100
        self.ticket_state = 0
        self.note = ''
        self.budget_dico = {'black_hole': 100}

    def teardown_method(self):
        pass

    def test_add_ticket(self):
        num_ticket = 1

        test_ticket = script.Ticket(self.date, self.recipient, self.reason, self.transaction_type, self.payment_type, self.amount,
            self.ticket_state, self.note, self.budget_dico)
        test_ticket.add_ticket_to_db(self.db)
        
        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'ticket', 'id', num_ticket)[-1])
            id_ticket = data[0]
            data = data[-8:]            

            affectation_data = script.fetch_data(c, 'ticket_affectation', 'id_ticket', id_ticket)

            budget_affectation = {}
            for i in affectation_data:
                name_budget = script.fetch_data(c, 'budget', 'id', i[1])[-1][1]
                budget_affectation[name_budget] = i[2]

        conn.close

        input_list_1 = [self.date, self.recipient, self.reason, self.transaction_type, self.payment_type, self.amount, self.ticket_state, self.note]


        assert input_list_1 == data and self.budget_dico == budget_affectation
        # check to do
        print('\ntest 11 : Ticket instance successfully created')

    def test_update_ticket(self):
        id_ticket_to_update = 1

        update_date = '2021-02-31 12:30:10'
        recipient = 'recipient_update_test'
        reason = 'reason_update_test'
        transaction_type = 1
        payment_type = script.payment_type[1]
        amount = 200
        ticket_state = 1
        note = ''
        budget_dico = {'pending': 200}

        test_ticket = script.Ticket(update_date, recipient, reason, transaction_type, payment_type, amount,
            ticket_state, note, budget_dico)
        test_ticket.update_ticket(self.db, id_ticket_to_update)
        
        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            data = list(script.fetch_data(c, 'ticket', 'id', id_ticket_to_update)[-1])
            id_ticket = data[0]
            data = data[-8:]

            affectation_data = script.fetch_data(c, 'ticket_affectation', 'id_ticket', id_ticket)

            budget_affectation = {}
            for i in affectation_data:
                name_budget = script.fetch_data(c, 'budget', 'id', i[1])[-1][1]
                budget_affectation[name_budget] = i[2]

        conn.close

        input_list_1 = [update_date, recipient, reason, transaction_type, payment_type, amount, ticket_state, note]


        assert input_list_1 == data and budget_dico == budget_affectation
        # check to do
        print('\ntest 12 : Ticket instance successfully updated')

    def test_delete_ticket(self):
        id_ticket_to_delete = 1

        test_ticket = script.Ticket(self.date, self.recipient, self.reason, self.transaction_type, self.payment_type, self.amount,
            self.ticket_state, self.note, self.budget_dico)
        test_ticket.delete_ticket(self.db, id_ticket_to_delete)

        conn = script.DB_connection(self.db)
        c = conn.cursor()
        with conn:
            c.execute('''SELECT id FROM ticket;''')
            temp_ticket_result = c.fetchall()
            id_list_ticket = [i[0] for i in temp_ticket_result]

            c.execute('''SELECT id_ticket FROM ticket_affectation;''')
            temp_ticket_affectation_result = c.fetchall()
            id_list_ticket_affectation = [i[0] for i in temp_ticket_affectation_result]

            conn.close
        
        assert id_ticket_to_delete not in id_list_ticket and id_ticket_to_delete not in id_list_ticket_affectation
        # check to do
        print('\ntest 13 : Ticket instance successfully deleted')


        





    
        