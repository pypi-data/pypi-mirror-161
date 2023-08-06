# coding: utf-8
"""Check styleguide for workbook elements."""

import re
from ast import Str
from inspect import getmembers, isfunction

from tableaudocumentapi import Field

from tabassist.error import Error
from tabassist.log import get_logger

logger = get_logger(__name__)


class FieldExtended(Field):
    """Decorator for base class for extanding functionality."""

    def __init__(self, field: Field, parent_source_name: Str = ''):
        """Init wrapper for field."""
        self._field = field
        self._parent_source_name = parent_source_name

    @property
    def id(self):
        """Name of the field as specified in the file, usually surrounded by [ ]."""
        return self._field.id

    @property
    def name(self):
        """Name of the field as displayed in Tableau unless an aliases is defined."""
        return self._field.name

    @property
    def caption(self):
        """Name of the field as displayed in Tableau unless an aliases is defined."""
        return self._field.caption

    @property
    def alias(self):
        """Alias of field as displayed in Tableau."""
        return self._field.alias

    @property
    def datatype(self):
        """Type of the field within Tableau (string, integer, etc)."""
        return self._field.datatype

    @property
    def role(self):
        """Dimension or Measure."""
        return self._field.role

    @property
    def is_quantitative(self):
        """Dependent value, usually a measure of something."""
        return self._field.is_quantitative

    @property
    def is_ordinal(self):
        """Categorical field that has a specific order."""
        return self._field.is_ordinal

    @property
    def is_nominal(self):
        """Categorical field that does not have a specific order."""
        return self._field.is_nominal

    @property
    def calculation(self):
        """If this field is a calculated field, this will be the formula."""
        return self._field.calculation

    @calculation.setter
    def calculation(self, value):
        self._field.calculation = value

    @property
    def default_aggregation(self):
        """Type of aggregation on the field (e.g Sum, Avg)."""
        return self._field.default_aggregation

    @property
    def description(self):
        """Contents of the <desc> tag on a field."""
        return self._field.description

    @property
    def worksheets(self):
        """List of worksheet where field is used."""
        return self._field.worksheets

    @property
    def is_parameter(self):
        """Return True if field is a parameter."""
        if 'parameter' in self._field.id.lower():
            return True
        elif 'parameter' in self._parent_source_name.lower():
            return True
        else:
            return False


class CheckField():
    """Checks for datasource's field in workbook."""

    def __init__(self, field: Field) -> None:
        """Initilize class for given Field object from tableaudocumentapi package."""
        self._field = field
        self.field_name = self._set_field_name()

    def _set_field_name(self):
        if self._field.caption is not None:
            return self._field.caption
        else:
            field_name = self._field.name
            return field_name.replace('[', '').replace(']', '')

    def run(self):
        """Start checks for current field."""
        if self._field.name != '[:Measure Names]':
            for cls_method_name, cls_method in getmembers(CheckField, isfunction):
                if cls_method_name.startswith('check_'):
                    logger.debug(f'{cls_method_name} will be used '
                                 f'for [{self._field.name}]')
                    yield cls_method(self)

    def check_field_in_lowercase(self):
        """Check if field name not in lowercase."""
        for letter in self.field_name:
            if letter.isupper():
                logger.debug(f'{self.field_name} was checked by check_field_in_lowercase')
                return Error('T100',
                             'field not in lowercase',
                             self.field_name)

    def check_trailing_witespace(self):
        """Check if field name contains trailing whitespace."""
        if self.field_name[0] == ' ' or self.field_name[-1] == ' ':
            logger.debug(f'{self.field_name} was checked by check_field_in_lowercase')
            return Error('T101',
                         'field has trailing whitespace',
                         self.field_name)

    def check_non_allowed_symbol(self):
        """Check if field name has non allowed symbols."""
        if bool(re.search(r'[^a-zA-Z0-9_\s%]', self.field_name)):
            return Error('T102',
                         'field has non allowed symbol(s)',
                         self.field_name)

    def check_non_unique_name(self):
        """Check if field name wasn't renamed after duplicating."""
        if '(copy)' in self.field_name:
            return Error('T103',
                         'field has \'(copy)\' as a part of name',
                         self.field_name)

    def _comment_exist(self):
        if self._field.calculation and \
           self._field.caption:
            lines = self._field.calculation.split('\n')
            for line in lines:
                if line[:2] == '//':
                    return True
            return False

    def check_comment_exist(self):
        """Check if inline comment exist in field formula (calculation)."""
        if self._comment_exist() is False and \
           self._field.is_parameter is False:
            return Error('T104',
                         'field doesn’t have comment',
                         self.field_name)

    def check_comment_position(self):
        """Check if inline comment starts from first line."""
        if self._comment_exist() and \
           self._field.calculation:
            if self._field.calculation[:2] != '//':
                return Error('T105',
                             'field has inline comment '
                             'which doesn’t start from first line',
                             self.field_name)

    def check_unused_by_worksheet(self):
        """Check if field is unused by any worksheet."""
        if len(self._field.worksheets) == 0 and \
           self._field.is_parameter is False:
            return Error('T106',
                         'field doesn’t used by any worksheet',
                         self.field_name)
