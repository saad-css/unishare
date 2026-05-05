from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
import requests

from ..core.api import post_json
from ..core.i18n import t, font


class LoginScreen(MDScreen):
    def refresh_lang(self):
        # English-only UI refresh.
        self.ids.app_sub_lbl.text = t('app_sub')
        self.ids.email_input.hint_text = t('email_hint')
        self.ids.pass_input.hint_text = t('pass_hint')
        self.ids.login_btn.text = t('login_btn')
        self.ids.no_account_btn.text = t('no_account')

    def do_login(self):
        # Validate login fields, call the API, and redirect based on user role.
        email = self.ids.email_input.text.strip().lower()
        pwd = self.ids.pass_input.text.strip()

        if not email or not pwd:
            self.ids.error_label.text = t('err_fields')
            self.ids.error_label.font_name = font()
            return

        try:
            # Send login request using email and password.
            response = post_json('/login', {
                'email': email,
                'password': pwd,
            })

            if response.status_code == 200:
                data = response.json()

                # Store logged-in user data in HomeScreen.
                home_screen = self.manager.get_screen('home')
                home_screen.user_id = data['user_id']
                home_screen.user_name = data.get('full_name', email)
                home_screen.is_admin = data.get('is_admin', False)

                # Store admin data in AdminScreen for future permission checks.
                admin_screen = self.manager.get_screen('admin')
                admin_screen.user_id = data['user_id']
                admin_screen.user_name = data.get('full_name', email)

                self.ids.error_label.text = ''
                self.manager.transition = SlideTransition(direction='left', duration=0.25)
                self.manager.current = 'admin' if data.get('is_admin', False) else 'home'
                return

            if response.status_code == 401:
                self.ids.error_label.text = t('err_creds')
            else:
                self.ids.error_label.text = response.json().get('error', t('err_server'))

        except requests.exceptions.ConnectionError:
            self.ids.error_label.text = t('err_offline')
        except Exception as e:
            print('Login error:', e)
            self.ids.error_label.text = t('err_unexpected')

        self.ids.error_label.font_name = font()
