import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600
    
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_switch.label = "Light Mode"
            theme_switch.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_switch.label = "Dark Mode"
            theme_switch.icon = ft.Icons.DARK_MODE
        page.update()
    
    theme_switch = ft.ElevatedButton(
        text="Dark Mode",
        icon=ft.Icons.DARK_MODE,
        on_click=toggle_theme
    )

    # Initialize DB
    db_conn = init_db()

    # Input fields
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    inputs = (name_input, phone_input, email_input)
    search_input = ft.TextField(label="Search", width=350, on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_input.value))

    # Contact list view
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    # Add button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    # Layout
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    # Header with theme toggle
                    ft.Row(
                        [
                            ft.Text("Contact Book", size=24, weight=ft.FontWeight.BOLD),
                            theme_switch
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(),

                    # Add contact section
                    ft.Text("Add New Contact:", size=18, weight=ft.FontWeight.W_500),
                    ft.Row([ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE), name_input], alignment=ft.MainAxisAlignment.CENTER), 
                    ft.Row([ft.Icon(ft.Icons.PHONE, color=ft.Colors.BLUE), phone_input], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE), email_input], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([add_button], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20),

                    # Search / Contact List section 
                    ft.Text("Your Contacts:", size=18, weight=ft.FontWeight.W_500),
                    ft.Row([ft.Icon(ft.Icons.SEARCH, color=ft.Colors.BLUE), search_input], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=10),

                    ft.Container(
                        content=contacts_list_view,
                        expand=True,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=8,
                        padding=10,
                    ),
                ],
                spacing=10,
            ),
            padding=20,
            expand=True
        )
    )


    # Load contacts on start
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)
