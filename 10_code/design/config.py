app_config = {
    'general_settings': {
        'window_height': 500,
        'window_width': 300,
        'material_style': 'M3',
        'theme_style': 'Dark',
        'primary_palette': 'Cyan',
        'primary_hue': '400',
        'complementary_color': '#FFD600',
        'title': 'BudgetDompté',
        'time_format': 'fr_FR.utf8',
        'time_format_string': '%d/%m/%Y',
        'AmountFormat_string': '1.00',
        'means_of_paiement': ['CB', 'Virement', 'Chèque'],
        'commun_widget': {
            'dialog': {
                'title': {
                    'account_filter_name' : 'Comptes : ',
                    'budget_filter_name' : 'Budgets : ',
                    'ticket_state_filter_name' : 'Status du ticket : ',
                    'alert_dialog_title' : 'Attention :',
                    'dayofmonth_dialog_title' : 'Jour de dépense :',
                    'note_dialog_title' : 'Note :',
                }
            },
            'buttons': {
                'validate': 'OK',
                'cancel': 'Annuler',
                'delete': 'Supprimer'
            }
        }
    },
    'HomeScreen': {
        'account': {
            'name': 'comptes'
        },
        'budget': {
            'name': 'budgets'
        },
        'transaction': {
            'name': 'transactions',
            'date_format': '%d/%m',
            'number_of_tickets': 20
        }
    },
    'TicketScreen': {
        'buttons': {
            'date': 'Date',
            'transaction_type': 'Type',
            'recipient': 'Ordre',
            'reason': 'Objet',
            'payment_type': 'Paiement',
            'account': 'Compte'
        },
        'separators': {
            'ticket_info': 'Informations Générales',
            'budget_contribution': 'Dépense : '
        },
        'dialog': {
            'title': {
                'note': 'Note :',
                'deletion': 'Suppression du ticket'
            },
            'message': {
                'deletion': 'Etes-vous sûr de vouloir supprimer le ticket ?',
                'no_transaction': 'type de transaction non renseigné !',
                'no_recipient': 'ordre non renseigné !',
                'no_reason': 'objet non renseigné !',
                'no_payment_type': 'moyen de paiment non renseigné !',
                'no_account': 'compte à débiter non renseigné !',
                'account_payment_type_not_existing': 'le type de paiment n\'existe pas pour le compte choisit',
                'intern_ticket_too_many_account': 'Pour un ticket interne, pas plus de 2 comptes impliqués !'

            },
            'hint': {
                'recipient': 'Ordre',
                'reason': 'Objet du ticket'
            }
            
        },
    }
}