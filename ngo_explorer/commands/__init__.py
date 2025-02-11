import click
from flask import Flask

from ngo_explorer.commands.countries import update_countries
from ngo_explorer.commands.fetchftc import fetch_ftc


def add_custom_commands(app: Flask):
    # add custom commands
    @app.cli.command("update-countries")
    def cli_update_countries():
        update_countries()

    @app.cli.command("fetch-ftc")
    @click.option("--sample", type=int, default=None)
    def cli_fetch_ftc(sample=None):
        fetch_ftc(sample)
