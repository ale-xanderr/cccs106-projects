import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    # window setup
    page.title = "User Login"
    page.window_width = 400
    page.window_height = 350
    page.window.title_bar_hidden = True
    page.window_frameless = True
    page.window.alignment = ft.alignment.center
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.AMBER_ACCENT

    title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER,
    )

    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        prefix_icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True, # obscure text
        can_reveal_password=True, # allows revealing of the password
        prefix_icon=ft.Icons.PASSWORD,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    async def login_click(e):

        # dialogs
        success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Login Successful"),
            content=ft.Text(f"Welcome! {username_field.value}"),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))], 
            icon=ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        )

        failure_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Login Failed"),
            content=ft.Text("Invalid username or password"),
            alignment= ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(failure_dialog))],
            icon=ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
        )

        invalid_input_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Input Error"),
            content=ft.Text("Please enter username and password"),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(invalid_input_dialog))],
            icon=ft.Icon(name=ft.Icons.INFO, color=ft.Colors.BLUE)
        )

        database_error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database"),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(database_error_dialog))],
        )

        # input validation
        if not username_field.value or not password_field.value:
            page.open(invalid_input_dialog)
            page.update()
            return

        # database logic
        try:
            # establish DB connection
            connection = connect_db()
            if not connection:
                page.open(database_error_dialog)
                page.update()
                return

            cursor = connection.cursor(dictionary=True)

            # execute parameterized query
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username_field.value, password_field.value)
            )

            result = cursor.fetchone()

            # close DB connection
            cursor.close()
            connection.close()

            # check result
            if result:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)

        except mysql.connector.Error as e:
            page.open(database_error_dialog)
        
        page.update()

    login_button =ft.ElevatedButton(
            text="Login",
            width=100,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLUE_500,
            icon=ft.Icons.LOGIN,
            on_click=login_click
        )

    # page layout
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(
       ft.SafeArea(
            ft.Container(
                ft.Column([title, username_field, password_field,
                ft.Container(content=login_button, alignment=ft.alignment.center_left, margin=ft.margin.Margin(680, 20, 0, 0))],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,), 
                alignment=ft.alignment.center,
            ), expand=True
       )
    )

ft.app(target=main)     #run the flet app