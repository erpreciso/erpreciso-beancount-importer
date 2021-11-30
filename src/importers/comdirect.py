import csv
from datetime import datetime, timedelta
from itertools import count
import re
import warnings
from os import path

from beancount.core.amount import Amount
from beancount.core import data
from beancount.ingest import importer
from src.importers import helpers


BANKS = ('ING', 'ING-DiBa')

META_KEYS = ('IBAN', 'Kontoname', 'Bank', 'Kunde', 'Zeitraum', 'Saldo')

PRE_HEADER = (
    'In der CSV-Datei finden Sie alle bereits gebuchten Umsätze. '
    'Die vorgemerkten Umsätze werden nicht aufgenommen, auch wenn sie in '
    'Ihrem Internetbanking angezeigt werden.'
)

class ComdirectImporter(importer.ImporterProtocol):
    def __init__(
        self,
        knt,
        account,
        file_encoding='ISO-8859-1',
    ):
        self.knt = knt
        self.account = account
        self.file_encoding = file_encoding

        self._date_from = None
        self._date_to = None
        self._line_index = -1

    def file_account(self, _):
        return self.account

    def _is_valid_first_header(self, line):
        return line == ';'

    def _is_valid_second_header(self, line):
        return line == '"Umsätze Girokonto";"Zeitraum: 10 Tage";'

    def identify(self, file_):
        m = r"umsaetze_" + self.knt + r"_\d{8}-\d{4}.csv"
        if not re.match(m, path.basename(file_.name)):
            return False
        with open(file_.name, encoding=self.file_encoding) as fd:
            def _read_line():
                return fd.readline().strip()
            # Header - first line
            line = _read_line()
            if not self._is_valid_first_header(line):
                return False
            # Header - second line (optional)
            line = _read_line()
            if line:
                if not self._is_valid_second_header(line):
                    return False
        return True
    
    def extract(self, file_, existing_entries=None):
        entries = []
        self._line_index = 0
        def _read_line():
            line = fd.readline().strip()
            self._line_index += 1
            return line
        def _read_empty_line():
            line = _read_line()
            if line:
                raise helpers.InvalidFormatError()
        with open(file_.name, encoding=self.file_encoding) as fd:
            # first line
            line = _read_line()
            if not self._is_valid_first_header(line):
                raise helpers.InvalidFormatError()
            # second line
            line = _read_line()
            if line:
                if not self._is_valid_second_header(line):
                    raise helpers.InvalidFormatError()
                # Empty line
                line = _read_line()
                _read_empty_line()

            # Data entries
            reader = csv.reader(
                fd, delimiter=';', quoting=csv.QUOTE_MINIMAL, quotechar='"'
            )
            def remap(names):
                # https://stackoverflow.com/a/31771695
                counter = count(1)
                return [
                    'Währung_{}'.format(next(counter))
                    if name == 'Währung'
                    else name
                    for name in names
                ]
            
            field_names = remap(next(reader))
            def split_payee_desc(date, txt):
                regex = r'Kto/IBAN: |Empfänger: |Auftraggeber: | Buchungstext: '
                s = re.split(regex, txt)
                if len(s)==2 and txt.find('Buchungstext')<0:
                    payee, description = s[0], s[1]
                else:
                    payee, description = s[1], s[2]
                return payee, description
            for row in reader:
                line = dict(zip(field_names, row))
                date = line['Buchungstag']
                payee, description = split_payee_desc(date, line['Buchungstext'])
                amount = line['Umsatz in EUR']
                currency = 'EUR'
                meta = data.new_metadata(filename=file_.name,
                                         lineno=self._line_index,
                                         # kvlist={'source_desc': ';'.join(row)},
                                         )
                amount = Amount(helpers._format_number_de(amount), currency)
                if date == 'offen':
                    m = datetime.today() + timedelta(days=7)
                    date = m.date() 
                else:
                    date = datetime.strptime(date, '%d.%m.%Y').date()
                posting_meta = {'source_desc': ';'.join(row)}
                postings = [
                    # data.Posting('Expenses:FIXME', -amount, None, None, None, None),
                    data.Posting(self.account, amount, None, None, None, posting_meta)
                ]
                entries.append(
                    data.Transaction(
                        meta,
                        date,
                        self.FLAG,
                        payee,
                        description,
                        data.EMPTY_SET,
                        data.EMPTY_SET,
                        postings,
                    )
                )
                self._line_index += 1
        return entries
