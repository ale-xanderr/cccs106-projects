import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def display_contacts(page, contacts_list_view, db_conn, search=""):
    """Fetches and displays all contacts in the ListView with optional search."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contacts_list_view.controls.append(
            ft.Card(
                elevation=4,
                margin=10,
                content=ft.Container(
                    padding=15,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            # Left side: contact details
                            ft.Column(
                                spacing=5,
                                alignment=ft.MainAxisAlignment.START,
                                controls=[
                                    ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.BLUE),
                                            ft.Text(phone or "N/A", size=14)
                                        ],
                                        spacing=8,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.EMAIL, size=16, color=ft.Colors.RED),
                                            ft.Text(email or "N/A", size=14)
                                        ],
                                        spacing=8,
                                    ),
                                ],
                            ),
                            # Right side: menu button
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(
                                        text="Edit",
                                        icon=ft.Icons.EDIT,
                                        on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                                    ),
                                    ft.PopupMenuItem(),  # separator
                                    ft.PopupMenuItem(
                                        text="Delete",
                                        icon=ft.Icons.DELETE,
                                        on_click=lambda _, cid=contact_id: delete_contact(page, cid, db_conn, contacts_list_view)
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            )
        )
    page.update()

def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs

    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty!"
        page.update()
        return

    name_input.error_text = None

    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    # Clear fields
    for field in inputs:
        field.value = ""
    display_contacts(page, contacts_list_view, db_conn)
    page.update()


def delete_contact(page, contact_id, db_conn, contacts_list_view):
    """Deletes a contact (with confirmation) and refreshes the list."""
    def confirm_delete(e):
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn, "")
        confirmation_dialog.open = False
        page.update()

    confirmation_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("YES", on_click=confirm_delete),
            ft.TextButton("NO", on_click=lambda e: setattr(confirmation_dialog, 'open', False) or page.update()),
        ],
    )
    page.open(confirmation_dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        update_contact_db(
            db_conn,
            contact_id,
            edit_name.value,
            edit_phone.value,
            edit_email.value
        )
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=lambda e: setattr(dialog, 'open', False) or page.update()
            ),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)