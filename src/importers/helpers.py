# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 17:25:04 2021

@author: c740
"""

import re
from beancount.core.number import Decimal


def _format_iban(iban):
    return re.sub(r'\s+', '', iban, flags=re.UNICODE)


def _format_number_de(value: str) -> Decimal:
    thousands_sep = '.'
    decimal_sep = ','
    return Decimal(value.replace(thousands_sep, '').replace(decimal_sep, '.'))

class InvalidFormatError(Exception):
    pass