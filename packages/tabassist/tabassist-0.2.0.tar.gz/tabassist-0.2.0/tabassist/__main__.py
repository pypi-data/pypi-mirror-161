# coding: utf-8
"""Main entrypoint of cli."""
import os
import shutil
from inspect import getmembers, isfunction
from pathlib import Path

import click
import pkg_resources
from tableaudocumentapi import Workbook

from tabassist.check import CheckField, FieldExtended
from tabassist.doc import generate_doc
from tabassist.error import ErrorRegistry
from tabassist.log import get_logger

PACKAGE_DATA_DIR = Path(pkg_resources.resource_filename(__package__, 'data/'))
logger = get_logger(__name__)


@click.group()
def cli():
    """Command line tool for working with Tableau workbook faster."""
    pass


@click.command()
@click.option('--file', '-f',
              required=True,
              help='Tableau filepath for checking.')
@click.option('--summary', '-s',
              is_flag=True,
              help='Show errors statistic for current checking.')
def check(file, summary):
    """Check given Tableau workbook for errors."""
    wb = Workbook(file)
    logger.info(f'File for cheking is {file}')

    errors = ErrorRegistry()

    for source in wb.datasources:
        logger.info(f'datasourse is {source.name}')
        for field in source.fields:
            logger.info(f'field is {source.fields[field].id}')
            for e in CheckField(FieldExtended(source.fields[field], source.name)).run():
                if e:
                    errors.add(e)
    if summary:
        errors.show_summary()
    else:
        errors.show_errors()


cli.add_command(check)


@click.group()
def doc():
    """Generate documentation from Tableau workbook."""
    pass


@click.command()
@click.option('--file', '-f',
              required=True,
              help='Template filepath.')
def add(file):
    """Add new template for generation."""
    try:
        src_path = Path(file)
        abs_src_path = src_path.resolve(strict=True)
    except FileNotFoundError:
        click.echo('File not found.')
    else:
        if src_path.is_file():
            # TODO: Check if it's a readable text file
            # TODO: Prompt user to owerride existing file
            shutil.copyfile(abs_src_path, PACKAGE_DATA_DIR.joinpath(abs_src_path.name))
            click.echo(f'File was copied to {PACKAGE_DATA_DIR}')
        else:
            click.echo("It's not an appropriate file.")


@click.command()
@click.option('--template_name', '-tn',
              required=True,
              help='Name of template.')
def delete(template_name):
    """Delete existing template for generation."""
    if template_name in os.listdir(PACKAGE_DATA_DIR):
        os.remove(PACKAGE_DATA_DIR.joinpath(template_name))
        click.echo(f'Template {template_name} was removed.')
    else:
        click.echo('File not found.')


@click.command()
def list():
    """List all templates for generation."""
    for num, f in enumerate(os.listdir(PACKAGE_DATA_DIR)):
        click.echo(f"{num}: {f}")


@click.command()
@click.option('--file', '-f',
              required=True,
              help='Tableau workbook path for generating documetation.')
@click.option('--name', '-n',
              required=True,
              help='File name of generated document.')
@click.option('--template', '-t',
              default='template.md',
              help='Template name for generation.')
def export(file, name, template):
    """Export documentation for given workbook."""
    generate_doc(file, name, template)


cli.add_command(doc)
doc.add_command(add)
doc.add_command(delete)
doc.add_command(list)
doc.add_command(export)

if __name__ == '__main__':
    cli()
