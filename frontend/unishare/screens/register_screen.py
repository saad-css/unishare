from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
import requests

from ..core.api import post_json
from ..core.i18n import t, font


class RegisterScreen(MDScreen):
    def refresh_lang(self):
        # English-only UI refresh.
        self.ids.register_title_lbl.text = t('register_title')
        self.ids.name_input.hint_text = t('fullname_hint')
        self.ids.email_input.hint_text = t('email_hint')
        self.ids.pass_input.hint_text = t('pass_hint')
        self.ids.create_btn.text = t('create_btn')
        self.ids.have_acc_btn.text = t('have_acc')

    def do_register(self):
        # Read and clean user input.
        name = self.ids.name_input.text.strip()
        email = self.ids.email_input.text.strip().lower()
        password = self.ids.pass_input.text.strip()

        # Validate required fields before sending the request.
        if not name or not email or not password:
            self.ids.error_label.text = t('err_fields')
            self.ids.error_label.font_name = font()
            return

        try:
            # Send registration data to the backend API.
            response = post_json('/signup', {
                'full_name': name,
                'email': email,
                'password': password,
            })

            # Handle successful registration and return to login screen.
            if response.status_code == 201:
                self.ids.error_label.text = ''
                self.manager.transition = SlideTransition(direction='right', duration=0.25)
                self.manager.current = 'login'
                return

            # Handle duplicate email or any backend validation error.
            if response.status_code == 409:
                self.ids.error_label.text = t('err_dup')
            else:
                self.ids.error_label.text = response.json().get('error', t('err_reg_fail'))

        except requests.exceptions.ConnectionError:
            # Backend server is unreachable.
            self.ids.error_label.text = t('err_offline')
        except Exception as e:
            # Print unexpected errors for debugging.
            print('Register error:', e)
            self.ids.error_label.text = t('err_unexpected')

        self.ids.error_label.font_name = font()
