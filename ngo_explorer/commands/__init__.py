from .countries import update_countries


def add_custom_commands(app):
    # add custom commands
    @app.cli.command("update-countries")
    def cli_update_countries():
        update_countries()
