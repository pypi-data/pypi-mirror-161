import os
from configparser import ConfigParser
from getpass import getpass

import click

from max_ard.admin import AccountManager
from max_ard.commands.grid import cell
from max_ard.commands.order import order
from max_ard.commands.select import select
from max_ard.commands.storage import storage
from max_ard.session import get_self, get_user_session, read_token, write_config


def check_access():
    get_self(get_user_session())
    return True


@click.group()
def max_ard():
    """Maxar ARD tools"""
    pass


@click.command()
@click.option("--username", help="ARD username")
@click.option("--password", help="ARD password")
def login(username, password):
    """Creates credential file using passed options --username and --password and tests access
    to the ARD system. If run without options,
    will only check if existing credential file at ~/.ard-config contains valid credentials"""

    if username or password:
        click.secho("... Creating config file ~/.ard-config", fg="cyan")
        write_config(username, password)
    else:
        if not os.path.exists(os.path.expanduser("~/.ard-config")):
            click.secho("No credential file exists - let's make a new one.")
            username = input("ARD account name? ")
            password = getpass(prompt="ARD account password? ")
            write_config(username, password)
    try:
        click.secho("... Checking access", fg="cyan")
        check_access()
        click.secho("ARD access confirmed", fg="green")
    except Exception as ex:
        click.secho(f"There was an error logging in: {ex}", fg="red", err=True)


@click.command()
@click.option("--reset", "-r", is_flag=True, help="Resets token (removes it from the config file)")
def token(reset):
    """ If run without options, returns the current token. 

        Handy for substitution in bash commands like curl:

            \b
            curl -H 'Accept: application/json' \\
                 -H "Authorization: Bearer $(max_ard token)" \\
                 https://hostname/api/myresource
    """

    if reset:
        config_file = os.path.expanduser("~/.ard-config")
        cfg = ConfigParser()
        cfg.read(config_file)
        cfg.remove_section("ard_token")
        click.secho("Token reset", fg="green")
        with open(config_file, "w") as sink:
            cfg.write(sink)
    else:
        check_access()
        click.secho(read_token(), fg="green")


@click.command()
def account():
    """Get basic account information for the current user"""

    self = get_self(get_user_session())
    user = self["user"]
    limits = user["limits"]

    click.secho(f'Account ID: {user["account_id"]}')
    click.secho(f'User ID: {user["user_id"]}')
    click.secho(f'User Name: {user["name"]}')
    click.secho(f'User Email: {user["email"]}')
    if any(limits.values()):
        click.secho(f"Usage Limits:")
        click.secho(f'  Area: {limits["annual_subscription_fee_limit"]} sq.km')
        click.secho(f'  Subscription: ${limits["fresh_imagery_fee_limit"]}')
        click.secho(f'  Fresh Imagery: ${limits["fresh_imagery_fee_limit"]}')
        click.secho(f'  Standard Imagery: ${limits["standard_imagery_fee_limit"]}')
        click.secho(f'  Training Imagery: ${limits["training_imagery_fee_limit"]}')
    else:
        click.secho(f"Usage Limits: None")
    click.secho("")


@click.command()
@click.option("--user", help="ARD user ID")
@click.option("--account", help="ARD account")
@click.option("--start-date", "start_date", help="Start date YYYY-MM-DD")
@click.option("--end-date", "end_date", help="End date YYYY-MM-DD")
def usage(user, account, start_date, end_date):
    """Get the usage for an account or a user"""

    self = get_self(get_user_session())
    while not any([user, account, start_date, end_date]):
        source = input("Get usage for an [a]ccount or [u]ser? ")
        if source.lower() not in ["a", "u"]:
            click.secho('Please press "a" for account or "u" for user', fg="red")
            continue
        if source.lower() == "a":
            account = input("Account number [current account]? ")
            if not account:
                account = self["user"]["account_id"]
        else:
            user = input("User ID [current user]? ")
            if not user:
                user = self["user"]["user_id"]
        start_date = input("Start date YYYY-MM-DD [none]? ")
        end_date = input("End date YYYY-MM-DD [none]? ")

    manager = AccountManager(account)

    try:
        if user:
            usage = manager.get_user_usage(user, start_date, end_date)
        else:
            usage = manager.get_account_usage(start_date, end_date)
    except Exception as e:
        click.secho(
            f"Error: {e}",
            err=True,
            fg="red",
        )
        exit(1)

    click.secho(str(usage), fg="cyan")


max_ard.add_command(login)
max_ard.add_command(token)
max_ard.add_command(usage)
max_ard.add_command(account)


max_ard.add_command(storage)
max_ard.add_command(cell)
max_ard.add_command(cell)
max_ard.add_command(select)
max_ard.add_command(order)

if __name__ == "__main__":
    max_ard()
