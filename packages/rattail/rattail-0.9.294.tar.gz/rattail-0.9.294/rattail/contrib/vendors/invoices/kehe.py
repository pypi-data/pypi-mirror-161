# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Vendor invoice parser for KeHE Distributors
"""

from __future__ import unicode_literals, absolute_import

import re
import csv
import datetime

import six

from rattail.vendors.invoices import InvoiceParser


class KeheInvoiceParser(InvoiceParser):
    """
    Vendor invoice parser for KeHE Distributors.

    KeHE has changed their format a few times; hence this parser is
    capable of handling a few similar but different formats.  All are
    essentially text/csv.

    Format #1 is the original and is tab-separated.

    Format #2 came circa 2020-02-11 and is comma-separated.

    Format #3 is like #1 but changed a column header.

    Format #4 is like #2 but changed column headers and data formats.

    See the :meth:`detect_version()` method for details of how the
    parser decides which "version" (format) of file it's dealing with.
    """
    key = 'rattail.contrib.kehe'
    display = "KeHE Distributors"
    vendor_key = 'kehe'

    pack_size_pattern = re.compile('^(?P<case_quantity>\d+)/(?P<size>\d*\.\d+ \w\w)$')

    def detect_version(self, path):
        """
        This will inspect the data file and return the "version" of format it
        thinks we're dealing with.
        """
        with open(path, 'rt') as f:
            line = f.readline()

        delimiter = str('\t') if '\t' in line else ','

        if six.PY3:
            csv_file = open(path, 'rt')
            reader = csv.DictReader(csv_file, delimiter=delimiter)
        else: # PY2
            csv_file = open(path, 'rb')
            reader = csv.DictReader(csv_file, delimiter=delimiter)
        data = next(reader)
        csv_file.close()

        if delimiter == ',': # comma-separated
            if 'OrderQuatity' in data:
                return 4
            return 2

        else: # tab-separated
            if 'InvoiceDate' in data:
                return 3
            return 1

    def parse_invoice_date(self, path):

        # first find out which version of file we have
        version = self.detect_version(path)

        delimiter = str('\t') if version in (1, 3) else ','
        if six.PY3:
            csv_file = open(path, 'rt')
            reader = csv.DictReader(csv_file, delimiter=delimiter)
        else: # PY2
            csv_file = open(path, 'rb')
            reader = csv.DictReader(csv_file, delimiter=delimiter)
        data = next(reader)
        csv_file.close()

        if version == 1:
            return datetime.datetime.strptime(data['Invoice Date'], '%Y-%m-%d').date()
        elif version in (2, 3):
            return datetime.datetime.strptime(data['InvoiceDate'], '%m/%d/%Y %I:%M:%S %p').date()
        elif version == 4:
            return datetime.datetime.strptime(data['InvoiceDate'], '%m/%d/%Y').date()

    def parse_rows(self, path):

        # first find out which version of file we have
        version = self.detect_version(path)
        delimiter = str('\t') if version in (1, 3) else ','

        # default fields for old version 1
        fields = {
            'upc': 'UPC Code',
            'ship_item': 'Ship Item',
            'brand': 'Brand',
            'description': 'Description',
            'order_quantity': 'Order Qty',
            'ship_quantity': 'Ship Qty',
            'net_each': 'Net Each',
            'net_billable': 'Net Billable',
            'pack_size': 'Pack Size',
        }

        if version > 1:
            fields.update({
                'upc': 'Upc',
                'ship_item': 'ShipItem',
                'order_quantity': 'OrderQuantity',
                'ship_quantity': 'ShipQuantity',
                'net_each': 'NetEach',
                'net_billable': 'NetBillable',
                'pack_size': 'PackSize',
            })

        if version == 4:
            fields.update({
                'order_quantity': 'OrderQuatity',
            })

        if six.PY3:
            csv_file = open(path, 'rt')
            reader = csv.DictReader(csv_file, delimiter=delimiter)
        else: # PY2
            csv_file = open(path, 'rb')
            reader = csv.DictReader(csv_file, delimiter=delimiter)

        for data in reader:

            row = self.make_row()
            row.item_entry = data[fields['upc']]
            row.upc = self.app.make_gpc(row.item_entry)
            row.vendor_code = data[fields['ship_item']]
            row.brand_name = data[fields['brand']]
            row.description = data[fields['description']]
            row.ordered_units = self.int_(data[fields['order_quantity']])
            row.shipped_units = self.int_(data[fields['ship_quantity']])
            row.unit_cost = self.decimal(data[fields['net_each']])
            row.total_cost = self.decimal(data[fields['net_billable']])

            # Case quantity may be embedded in size string.
            row.size = data[fields['pack_size']]
            row.case_quantity = 1
            match = self.pack_size_pattern.match(row.size)
            if match:
                row.case_quantity = int(match.group('case_quantity'))
                row.size = match.group('size')

            # attach original raw data to the row we're returning; caller
            # can use as needed, or ignore
            row._raw_data = data

            yield row

        csv_file.close()
