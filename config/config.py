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
from config.categorizer import categorizer_dict
from config import bank_data

categorizer = PayeeCategorizer(categorizer_dict)


CONFIG = [
    apply_hooks(
        ECImporter(
            bank_data.iban,
            'Assets:Stefano:DibaChecking',
            'Stefano Merlo',
            file_encoding='ISO-8859-1',
            ), [categorizer, PredictPostings()]),
    apply_hooks(
        ComdirectImporter(
            bank_data.knt,
            'Assets:Family:Comdirect',
            file_encoding='ISO-8859-1',
            ), [categorizer, PredictPostings()])
]
