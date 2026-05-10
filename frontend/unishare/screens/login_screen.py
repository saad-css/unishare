from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
import requests

from ..core.api import post_json


class LoginScreen(MDScreen):
    def refresh_lang(self):
        # English-only app: set static labels and hints.
        self.ids.app_sub_lbl.text = "Student Collaboration Platform"
        self.ids.email_input.hint_text = "Email"
        self.ids.pass_input.hint_text = "Password"
        self.ids.login_btn.text = "LOGIN"
        self.ids.no_account_btn.text = "No account? Create one"

    def do_login(self):
        # Validate login fields, call the API, and redirect based on user role.
        email = self.ids.email_input.text.strip().lower()
        password = self.ids.pass_input.text.strip()

        # Validate required fields before sending the request.
        if not email or not password:
            self.ids.error_label.text = "Please fill in all fields"
            return

        try:
            # Send login request using email and password.
            response = post_json("/login", {
                "email": email,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()

                # Store logged-in user data in HomeScreen.
                home_screen = self.manager.get_screen("home")
                home_screen.user_id = data["user_id"]
                home_screen.user_name = data.get("full_name", email)
                home_screen.is_admin = data.get("is_admin", False)

                # Store admin user id if AdminScreen exists.
                if "admin" in self.manager.screen_names:
                    admin_screen = self.manager.get_screen("admin")
                    admin_screen.admin_user_id = data["user_id"]

                self.ids.error_label.text = ""
                self.manager.transition = SlideTransition(direction="left", duration=0.25)

                # Redirect admin users to AdminScreen, otherwise go to HomeScreen.
                if data.get("is_admin", False) and "admin" in self.manager.screen_names:
                    self.manager.current = "admin"
                else:
                    self.manager.current = "home"

            elif response.status_code == 401:
                self.ids.error_label.text = "Invalid email or password"
            else:
                try:
                    self.ids.error_label.text = response.json().get(
                        "error",
                        "Server error"
                    )
                except Exception:
                    self.ids.error_label.text = "Server error"

        except requests.exceptions.ConnectionError:
            self.ids.error_label.text = "Server is offline"
        except Exception as e:
            # Print unexpected errors for debugging.
            print("Login error:", e)
            self.ids.error_label.text = "Unexpected error"