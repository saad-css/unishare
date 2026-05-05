from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.app import MDApp

from unishare.core.i18n import t
from unishare.widgets.file_card import FileCard
from unishare.screens.login_screen import LoginScreen
from unishare.screens.register_screen import RegisterScreen
from unishare.screens.home_screen import HomeScreen
from unishare.screens.files_screen import FilesScreen
from unishare.screens.admin_screen import AdminScreen


class UniShareApp(MDApp):
    def build(self):
        # Configure the global Material theme before loading the interface.
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'

        # Register custom classes used by the KV interface.
        Factory.register('FileCard', cls=FileCard)
        Factory.register('LoginScreen', cls=LoginScreen)
        Factory.register('RegisterScreen', cls=RegisterScreen)
        Factory.register('HomeScreen', cls=HomeScreen)
        Factory.register('FilesScreen', cls=FilesScreen)
        Factory.register('AdminScreen', cls=AdminScreen)
        return Builder.load_file('unishare/ui.kv')

    def get_text(self, key: str) -> str:
        # English-only text helper for future KV bindings.
        return t(key)


if __name__ == '__main__':
    UniShareApp().run()
