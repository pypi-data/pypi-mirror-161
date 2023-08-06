"""CLI (Command Line Interface) module."""

import sys
from typing import Optional

from click import group, option, confirmation_option

from notelist import app
from notelist.tools import get_uuid, get_hash
from notelist.schemas.users import UserSchema
from notelist.db import get_main_db
from notelist.db.main import MainDbManager


# Option descriptions
des_host = "Host."
des_port = "Port."
des_debug = "Enable debug mode."
des_id = "ID."
des_username = "Username."
des_password = "Password."
des_admin = "Whether the user is an administrator or not."
des_enabled = "Whether the user is enabled or not."
des_name = "Name."
des_email = "E-mail address."

# Messages
conf_cre_db = "Are you sure that you want to create the database?"
conf_del_db = "Are you sure that you want to delete the database?"
conf_del_user = "Are you sure that you want to delete the user?"

# Schemas
schema = UserSchema()


@group()
def cli():
    """Welcome to Notelist 0.10.0.

    Notelist is a tag based note taking REST API.
    """
    pass


@cli.group()
def db():
    """Manage database."""
    pass


@cli.group()
def user():
    """Manage users."""
    pass


@db.command("create")
@confirmation_option(prompt=conf_cre_db)
def create_db():
    """Create the database."""
    print("Creating database...")

    try:
        db = get_main_db()
        db.create_db()
    except Exception as e:
        sys.exit(f"Error: {e}")

    print("Done")


@db.command("delete")
@confirmation_option(prompt=conf_del_db)
def delete_db():
    """Delete the database."""
    print("Deleting database...")

    try:
        db = get_main_db()
        db.delete_db()
    except Exception as e:
        sys.exit(f"Error: {e}")

    print("Done")


def get_ls_header() -> str:
    """Get the header in the User Ls command.

    :returns: Header.
    """
    return (
        "ID" + (" " * 31) + "| Username" + (" " * 13) + "| Administrator | "
        "Enabled |\n"
    )


def get_ls_user_line(user: dict) -> str:
    """Get a string representing a user in the User Ls command.

    :param user: User data.
    :returns: User string.
    """
    line = user["id"] + " | "
    username = user["username"]
    c = len(username)

    if c <= 20:
        username = username + (" " * (20 - c))
    else:
        username = f"{username[:17]}..."

    admin = "Yes" if user["admin"] else "No "
    enabled = "Yes" if user["enabled"] else "No "

    line += username + " | "
    line += admin + (" " * 11) + "| "
    line += enabled + (" " * 5) + "|"

    return line


@user.command("ls")
def list_users():
    """List users."""
    try:
        db = get_main_db()
        users = db.users.get_all()
        c = len(users)

        if c > 0:
            print("\n" + get_ls_header())

            for u in users:
                print(get_ls_user_line(u))

        s = "s" if c != 1 else ""
        print(f"\n{c} user{s}\n")
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command("get")
@option("--id", required=True, help=des_id)
def get_user(id: str):
    """Get a user."""
    try:
        db = get_main_db()
        user = db.users.get_by_id(id)

        if user is None:
            raise Exception("User not found.")

        _id = user["id"]
        username = user["username"]
        admin = "Yes" if user["admin"] else "No"
        enabled = "Yes" if user["enabled"] else "No"
        name = user.get("name")
        email = user.get("email")
        created = user["created"].replace("T", " ")
        last_mod = user["last_modified"].replace("T", " ")

        print("\nID:" + (" " * 12) + _id)
        print("Username: " + (" " * 5) + username)
        print(f"Administrator: {admin}")
        print("Enabled:" + (" " * 7) + enabled)

        if name is not None:
            print("Name:" + (" " * 10) + name)

        if email is not None:
            print("E-mail:" + (" " * 8) + email)

        print("Created:" + (" " * 7) + created)
        print(f"Last modified: {last_mod}\n")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def put_user(
    db: MainDbManager, _id: str, username: str, password: str, admin: bool,
    enabled: bool, name: Optional[str], email: Optional[str],
    created: Optional[str] = None
):
    """Put (create/update) a user.

    :param _id: ID.
    :param username: Username.
    :param password: Password.
    :param admin: Whether the user is an administrator or not.
    :param enabled: Whether the user is enabled or not.
    :param name: Name.
    :param email: E-mail.
    """
    user = {
        "id": _id,
        "username": username,
        "password": password,
        "admin": admin,
        "enabled": enabled
    }

    if name is not None:
        user["name"] = name

    if email is not None:
        user["email"] = email

    # If we are updating the user instead of creating it, we keep the value of
    # the Created field of the current user document.
    if created is not None:
        user["created"] = created

    # Load/deserialize the data with the standard schema to generate the value
    # of the Last Modified field and process all the fields.
    user = schema.load(user)

    # Encrypt password
    user["password"] = get_hash(password)

    db.users.put(user)


@user.command("create")
@option("--username", required=True, help=des_username)
@option(
    "--password", prompt=True, confirmation_prompt=True, hide_input=True,
    help=des_password
)
@option("--admin", default=False, help=des_admin)
@option("--enabled", default=False, help=des_enabled)
@option("--name", help=des_name)
@option("--email", help=des_email)
def create_user(
    username: str, password: str, admin: bool, enabled: bool,
    name: Optional[str], email: Optional[str]
):
    """Create a user."""
    try:
        db = get_main_db()

        if db.users.get_by_username(username):
            raise Exception("A user with the same username already exists.")

        put_user(
            db, get_uuid(), username, password, admin, enabled, name, email
        )
        print("User created")
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command("update")
@option("--id", required=True, help=des_id)
@option("--username", required=True, help=des_username)
@option(
    "--password", prompt=True, confirmation_prompt=True, hide_input=True,
    help=des_password
)
@option("--admin", default=False, help=des_admin)
@option("--enabled", default=False, help=des_enabled)
@option("--name", help=des_name)
@option("--email", help=des_email)
def update_user(
    id: str, username: str, password: str, admin: bool, enabled: bool,
    name: Optional[str], email: Optional[str]
):
    """Update a user."""
    try:
        db = get_main_db()
        user = db.users.get_by_id(id)  # Current user

        if user is None:
            raise Exception("User not found.")

        if (
            username != user["username"] and
            db.users.get_by_username(username) is not None
        ):
            raise Exception("A user with the same username already exists.")

        created = user["created"]

        put_user(
            db, id, username, password, admin, enabled, name, email, created
        )

        print("User updated")
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command("delete")
@option("--id", required=True, help=des_id)
@confirmation_option(prompt=conf_del_db)
def delete_user(id: str):
    """Delete a user."""
    try:
        db = get_main_db()
        user = db.users.get_by_id(id)

        if user is None:
            raise Exception("User not found.")

        db.users.delete(id)
        print("User deleted")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


@cli.command("run")
@option("--host", default="localhost", help=des_host)
@option("--port", default=5000, help=des_port)
@option("--debug", default=False, help=des_debug)
def run(host: str, port: int, debug: bool):
    """Run the Notelist API."""
    app.run(host=host, port=port, debug=debug)
