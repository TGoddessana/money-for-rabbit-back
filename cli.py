from sqlite3 import IntegrityError

import click
from flask.cli import with_appcontext
from pymysql import IntegrityError

from api.models.user import UserModel


@click.command(name="createadminuser")
@with_appcontext
def create_admin_user():
    username = input("Enter username : ")
    email = input("Enter email : ")
    password = input("Enter password : ")

    try:
        superuser = UserModel(
            username=username,
            email=email,
            password=password,
            is_active=True,
            is_admin=True,
        ).create_user()
    except IntegrityError:
        print("\033[31m" + "Error : username or email already exists.")
    print(f"User created! : {email}")
