from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
import requests

from ..core.api import post_json


class RegisterScreen(MDScreen):

    def do_register(self):
        # Read and clean user input.
        name = self.ids.name_input.text.strip()
        email = self.ids.email_input.text.strip().lower()
        password = self.ids.pass_input.text.strip()

        # Validate required fields before sending the request.
        if not name or not email or not password:
            self.ids.error_label.text = "Please fill in all fields"
            return

        try:
            # Send registration data to the backend API.
            response = post_json('/signup', {
                'full_name': name,
                'email': email,
                'password': password
            })

            # Handle successful registration and return to login screen.
            if response.status_code == 201:
                print("Account created successfully")
                self.ids.error_label.text = ""
                self.manager.transition = SlideTransition(direction='right', duration=0.25)
                self.manager.current = 'login'
                return

            # Handle duplicate email error.
            if response.status_code == 409:
                self.ids.error_label.text = "Email already registered"
            else:
                # Show backend error message if available.
                try:
                    self.ids.error_label.text = response.json().get(
                        'error',
                        "Registration failed"
                    )
                except Exception:
                    self.ids.error_label.text = "Registration failed"

        except requests.exceptions.ConnectionError:
            # Backend server is unreachable.
            self.ids.error_label.text = "Server is offline"
        except Exception as e:
            # Print unexpected errors for debugging.
            print("Register error:", e)
            self.ids.error_label.text = "Unexpected error"