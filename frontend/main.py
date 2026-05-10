from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.app import MDApp
from kivy.properties import OptionProperty

from unishare.widgets.file_card import FileCard
from unishare.screens.login_screen import LoginScreen
from unishare.screens.register_screen import RegisterScreen
from unishare.screens.home_screen import HomeScreen
from unishare.screens.files_screen import FilesScreen
from unishare.screens.admin_screen import AdminScreen


class UniShareApp(MDApp):
    lang = OptionProperty('en', options=['en', 'ar'])

    def build(self):
        # Configure the global Material theme before loading the interface.
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'

        Factory.register('FileCard', cls=FileCard)
        Factory.register('LoginScreen', cls=LoginScreen)
        Factory.register('RegisterScreen', cls=RegisterScreen)
        Factory.register('HomeScreen', cls=HomeScreen)
        Factory.register('FilesScreen', cls=FilesScreen)
        Factory.register('AdminScreen', cls=AdminScreen)
        return Builder.load_file('unishare/ui.kv')

    def switch_lang(self):
        # English-only version: language switching is disabled.
        self.lang = 'en'
        for screen_name in self.root.screen_names:
            screen = self.root.get_screen(screen_name)
            if hasattr(screen, 'refresh_lang'):
                screen.refresh_lang()

    def get_text(self, key: str) -> str:
        return t(key)


if __name__ == '__main__':
    UniShareApp().run()
