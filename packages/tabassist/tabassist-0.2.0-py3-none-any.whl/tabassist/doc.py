# coding: utf-8
"""Generate documentation for Tableau workbook."""

import os

import click
from jinja2 import Environment, PackageLoader
from tableaudocumentapi import Workbook

from tabassist.check import FieldExtended
from tabassist.log import get_logger


logger = get_logger(__name__)
env = Environment(
    loader=PackageLoader(__package__, 'data')
)


def generate_doc(file, name, template):
    """Generate documentation by given workbook path.

    Args:
        file (Path): Path to Tableau workbook.
        name (str): Generated document name.
        template (str, optional): Name of template to use. Defaults to 'template.md'.
    """
    wb = Workbook(file)
    logger.debug(f'Workbook for generating docs is {file}')

    def normalize_calculation(field: FieldExtended, mapping: dict):
        for item in mapping.items():
            old_val, new_val = item
            if field.calculation:
                field.calculation = field.calculation.replace(old_val, new_val)
        logger.debug(f'Field calculation {field.name} was updated')
        return field

    # normalize fileds' names
    mapping = {}

    for s in wb.datasources:
        for f in s.fields.values():
            f = FieldExtended(f, s.name)
            if f.is_parameter:
                mapping.update({f._field.id: '[' + str(f._field.caption) + ']'})
            elif f._field.calculation:
                mapping.update({f._field.id: '[' + f._field.name + ']'})

    parameters, *_ = list(filter(lambda x: x.name.lower() == 'parameters',
                                 wb.datasources))

    for s in wb.datasources:
        for field_name in s.calculations:
            logger.debug(f'Field calculation {field_name} will be normalized.')
            field = s.fields[field_name]
            fe = FieldExtended(field, s.name)
            if field_name in parameters.fields:
                logger.debug(f'Field {field_name} is parameter.')
                pass
            elif fe.is_parameter is False:
                try:
                    s.remove_field(field)
                    s.add_calculation(field.caption,
                                      normalize_calculation(fe, mapping).calculation,
                                      field.datatype,
                                      field.role,
                                      field.type)
                except ValueError:
                    logger.warning(f'Field {field_name} from ' /
                                   f'{s.caption} can\'t be updated.')

    template = env.get_template(template)
    rendered_page = template.render(doc_name=name,
                                    datasources=wb.datasources,
                                    autoescape=True)
    cwd = os.getcwd()

    with open(os.path.join(cwd, name), 'w', encoding="utf8") as file:
        file.write(rendered_page)
    click.echo(f"Document exported to '{cwd}'.")
