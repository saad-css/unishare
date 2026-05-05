from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
import requests

from ..core.api import post_json
from ..core.i18n import t, font


class LoginScreen(MDScreen):
    def refresh_lang(self):
        # Update labels and placeholders when the language changes.
        fn = font()
        chip_txt = 'EN' if MDApp.get_running_app().lang == 'ar' else 'AR'

        self.ids.app_sub_lbl.text = t('app_sub')
        self.ids.app_sub_lbl.font_name = fn

        # Use email for authentication instead of student ID.
        self.ids.email_input.hint_text = t('email_hint')
        self.ids.email_input.font_name = fn

        self.ids.pass_input.hint_text = t('pass_hint')
        self.ids.pass_input.font_name = fn

        self.ids.login_btn.text = t('login_btn')
        self.ids.login_btn.font_name = fn

        self.ids.no_account_btn.text = t('no_account')
        self.ids.no_account_btn.font_name = fn

        self.ids.lang_chip_login.text = chip_txt

    def do_login(self):
        # Validate login fields, call the API, and redirect based on user role.
        email = self.ids.email_input.text.strip().lower()
        pwd = self.ids.pass_input.text.strip()

        # Validate required fields before sending the request.
        if not email or not pwd:
            self.ids.error_label.text = t('err_fields')
            self.ids.error_label.font_name = font()
            return

        try:
            # Send login request using email and password.
            response = post_json('/login', {
                'email': email,
                'password': pwd
            })

            if response.status_code == 200:
                data = response.json()

                # Store logged-in user data in HomeScreen and AdminScreen.
                home_screen = self.manager.get_screen('home')
                home_screen.user_id = data['user_id']
                home_screen.user_name = data.get('full_name', email)
                home_screen.is_admin = data.get('is_admin', False)

                admin_screen = self.manager.get_screen('admin')
                admin_screen.admin_user_id = data['user_id']

                self.ids.error_label.text = ''
                self.manager.transition = SlideTransition(direction='left', duration=0.25)

                # Redirect admin users to AdminScreen, otherwise go to HomeScreen.
                if data.get('is_admin', False):
                    self.manager.current = 'admin'
                else:
                    self.manager.current = 'home'

            elif response.status_code == 401:
                self.ids.error_label.text = t('err_creds')
            else:
                try:
                    self.ids.error_label.text = response.json().get('error', t('err_server'))
                except Exception:
                    self.ids.error_label.text = t('err_server')

        except requests.exceptions.ConnectionError:
            self.ids.error_label.text = t('err_offline')
        except Exception as e:
            # Print unexpected errors for debugging.
            print("Login error:", e)
            self.ids.error_label.text = t('err_unexpected')

        self.ids.error_label.font_name = font()