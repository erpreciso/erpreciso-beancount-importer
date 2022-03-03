# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 13:10:48 2021

@author: c740
"""

import sys
sys.path.append('..')

from smart_importer import apply_hooks, PredictPostings
from beancount_categorizer import PayeeCategorizer


from src.importers.ec import ECImporter
from src.importers.comdirect import ComdirectImporter



"""
Example of categorizer:
    
    categorizer_dict = {
        "Expenses:Family:Groceries": ["PENNY AUF DER WANNE",
                                      "Penny Auf der Wanne",
                                      "NAH UND GUT",
                                      "KAUFLAND",
                                      "DM DROGERIEMARKT SAGT DANKE"],
        "Expenses:Family:House:TV-Tax": ["Rundfunk ARD, ZDF, DRadio"],
    }
    
"""

from config.categorizer import categorizer_dict
categorizer = PayeeCategorizer(categorizer_dict)

"""
Sensitive data are stored in separate file 'personal_data'.

Example:
    ing_iban = "valid IBAN"
    comdirect_account_number = "valid 10-digits account number"
    ing_account = 'Assets:blabla'
    comdirect_account = 'Assets:blabla'
    ing_identifier = 'John Doe'

"""

from config import personal_data
CONFIG = [
    apply_hooks(
        ECImporter(
            personal_data.ing_iban,
            personal_data.ing_account,
            personal_data.ing_identifier,
            file_encoding='ISO-8859-1',
            ), [categorizer, PredictPostings()]),
    apply_hooks(
        ComdirectImporter(
            personal_data.comdirect_account_number,
            personal_data.comdirect_account,
            file_encoding='ISO-8859-1',
            ), [categorizer, PredictPostings()])
]
