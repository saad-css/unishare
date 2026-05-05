import os

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.filemanager import MDFileManager

from ..core.api import get_json, upload_file
from ..core.i18n import t, font, ar
from ..widgets.file_card import FileCard


class HomeScreen(MDScreen):
    user_id = None
    user_name = ''
    selected_course = None
    _drawer_open = False
    _file_manager = None

    def on_enter(self):
        # Reload profile and major list every time the user enters the screen.
        self._load_profile()
        self._load_drawer()
        self.refresh_lang()

    def refresh_lang(self):
        # Update all dynamic texts for the current language.
        fn = font()
        chip_txt = 'EN' if MDApp.get_running_app().lang == 'ar' else 'AR'

        self.ids.home_title_lbl.text = t('home_title')
        self.ids.home_title_lbl.font_name = fn
        self.ids.lang_chip_home.text = chip_txt
        self.ids.selected_course_label.font_name = fn
        self.ids.empty_title_lbl.text = t('empty_title')
        self.ids.empty_title_lbl.font_name = fn
        self.ids.empty_sub_lbl.text = t('empty_sub')
        self.ids.empty_sub_lbl.font_name = fn
        self.ids.colleges_hdr_lbl.text = t('colleges_hdr')
        self.ids.colleges_hdr_lbl.font_name = fn
        self.ids.logout_lbl.text = t('logout_lbl')
        self.ids.logout_lbl.font_name = fn
        self.ids.welcome_label.font_name = fn
        self.ids.files_label.font_name = fn
        self.ids.drawer_name.font_name = fn
        self.ids.drawer_email.font_name = fn

        if self.selected_course:
            name = self.selected_course.get('name', '')
            self.ids.selected_course_label.text = ar(name) if MDApp.get_running_app().lang == 'ar' else name
        else:
            self.ids.selected_course_label.text = t('pick_course')

        for card in self.ids.file_grid.children:
            if hasattr(card, 'refresh_lang'):
                card.refresh_lang()

    def _load_profile(self):
        # Request the logged-in user profile and show upload statistics.
        if not self.user_id:
            return

        try:
            payload = get_json(f'/user_info/{self.user_id}')
            lang = MDApp.get_running_app().lang

            self.ids.welcome_label.text = (
                ar(f"مرحباً، {payload['full_name']} 👋")
                if lang == 'ar'
                else f"Hello, {payload['full_name']} 👋"
            )

            self.ids.files_label.text = (
                ar(f"الملفات المرفوعة: {payload['files_count']}")
                if lang == 'ar'
                else f"Files Uploaded: {payload['files_count']}"
            )

            self.ids.drawer_name.text = ar(payload['full_name']) if lang == 'ar' else payload['full_name']
            self.ids.drawer_email.text = ar(f"البريد الإلكتروني: {payload['email']}") if lang == 'ar' else f"Email: {payload['email']}"

        except Exception as e:
            # Keep the screen usable even if profile loading fails.
            print("Profile load error:", e)
            self.ids.welcome_label.text = t('welcome')

    def _load_drawer(self):
        # Fetch majors from the API and render them as drawer rows.
        drawer_list = self.ids.drawer_list
        drawer_list.clear_widgets()

        try:
            majors = get_json('/majors')
        except Exception as e:
            print("Majors load error:", e)
            majors = []

        for major in majors:
            row = self._make_row(
                'book-outline',
                (0.255, 0.647, 0.961, 1),
                major['name'],
                lambda m=major: self._load_courses(m)
            )
            drawer_list.add_widget(row)

    def _load_courses(self, major):
        # Replace the majors list with the selected major's courses.
        from kivymd.uix.label import MDLabel

        drawer_list = self.ids.drawer_list
        drawer_list.clear_widgets()

        drawer_list.add_widget(
            self._make_row(
                'arrow-right',
                (0.6, 0.6, 0.6, 1),
                t('back_lbl'),
                self._load_drawer
            )
        )

        header_text = ar(major['name']) if MDApp.get_running_app().lang == 'ar' else major['name']
        drawer_list.add_widget(
            MDLabel(
                text=header_text,
                font_style='Caption',
                bold=True,
                theme_text_color='Custom',
                text_color=(0.255, 0.647, 0.961, 1),
                size_hint_y=None,
                height='30dp',
                font_name=font(),
            )
        )

        try:
            courses = get_json(f"/courses/{major['id']}")
        except Exception as e:
            print("Courses load error:", e)
            courses = []

        for course in courses:
            row = self._make_row(
                'folder-outline',
                (0.133, 0.647, 0.322, 1),
                course['name'],
                lambda c=course: self._select_course(c)
            )
            drawer_list.add_widget(row)

    def _select_course(self, course):
        # Update the selected course state and load its files into the grid.
        self.selected_course = course

        name = ar(course['name']) if MDApp.get_running_app().lang == 'ar' else course['name']
        self.ids.selected_course_label.text = name
        self.ids.selected_course_label.font_name = font()

        self._load_files(course['id'])

        if self._drawer_open:
            self.toggle_drawer()

    def _load_files(self, course_id):
        # Fetch approved course files from the API and rebuild the file cards.
        grid = self.ids.file_grid
        empty_box = self.ids.empty_box

        grid.clear_widgets()
        empty_box.opacity = 0

        try:
            files = get_json(f'/files/{course_id}')
        except Exception as e:
            print('Files load error:', e)
            files = []

        if not files:
            empty_box.opacity = 1
            return

        for item in files:
            card = FileCard()
            card.storage_name = item.get('storage_name', '')
            card.file_id = item.get('id')
            card.user_id = self.user_id

            filename = item.get('filename', 'Unknown file')
            uploader = item.get('uploader', 'Unknown')

            card.ids.title.text = filename
            card.ids.uploader.text = f'By: {uploader}'

            icon, color = card.get_icon_and_color(filename)
            card.ids.file_icon.icon = icon
            card.ids.file_icon.text_color = color

            card.refresh_lang()
            grid.add_widget(card)

    def _make_row(self, icon, icon_color, text, on_tap):
        # Build one tappable item row for the drawer menu.
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.boxlayout import MDBoxLayout

        row = MDBoxLayout(
            size_hint_y=None,
            height='52dp',
            padding=['16dp', '0dp'],
            spacing='10dp'
        )

        icon_widget = MDIconButton(
            icon=icon,
            theme_text_color='Custom',
            text_color=icon_color,
            size_hint=(None, None),
            size=('32dp', '52dp'),
            pos_hint={'center_y': 0.5}
        )
        icon_widget.bind(on_release=lambda _x: on_tap())

        lang = MDApp.get_running_app().lang
        display_text = ar(text) if lang == 'ar' and any('\u0600' <= c <= '\u06ff' for c in text) else text

        label = MDLabel(
            text=display_text,
            font_style='Body1',
            theme_text_color='Custom',
            text_color=(0.15, 0.15, 0.15, 1),
            valign='center',
            font_name=font()
        )

        def tap_row(instance, touch):
            # Trigger the same action when the user taps anywhere on the row.
            if instance.collide_point(*touch.pos):
                on_tap()
                return True
            return False

        row.bind(on_touch_down=tap_row)
        row.add_widget(icon_widget)
        row.add_widget(label)

        return row

    def toggle_drawer(self):
        # Animate the drawer panel open and closed.
        panel = self.ids.drawer_panel

        if self._drawer_open:
            Animation(width=0, opacity=0, duration=0.22).start(panel)
        else:
            Animation(width=280, opacity=1, duration=0.22).start(panel)

        self._drawer_open = not self._drawer_open

    def upload_file(self):
        # Handle upload button click and open the file manager.
        print("Upload button clicked")

        # The user must select a course before uploading a file.
        if not self.selected_course:
            print(t('pick_first'))
            return

        # Open file manager from the user's home directory.
        start_path = os.path.expanduser("~")
        print("Opening file manager at:", start_path)

        self._file_manager = MDFileManager(
            exit_manager=self._close_file_manager,
            select_path=self._file_selected,
        )
        self._file_manager.show(start_path)

    def _close_file_manager(self, *args):
        # Safely close the file manager if it exists.
        if self._file_manager:
            self._file_manager.close()

    def _file_selected(self, path):
        # Close file manager after selecting a file.
        self._close_file_manager()

        try:
            # Upload selected file to the backend API.
            response = upload_file(
                '/upload',
                path,
                {
                    'course_id': self.selected_course['id'],
                    'user_id': self.user_id
                }
            )

            # Print backend response for debugging.
            print("Upload status:", response.status_code)

            try:
                print("Upload response:", response.json())
            except Exception:
                print("Upload response text:", response.text)

            # Refresh files and profile after successful upload.
            if response.status_code == 201:
                print(t('upload_snack'))
                self._load_files(self.selected_course['id'])
                self._load_profile()
            else:
                print(t('upload_fail'))

        except Exception as e:
            # Print unexpected upload errors.
            print("Upload exception:", e)

    def logout(self):
        # Reset local UI state and return the user to the login screen.
        Animation(width=0, opacity=0, duration=0.18).start(self.ids.drawer_panel)

        self._drawer_open = False
        self.selected_course = None

        self.ids.file_grid.clear_widgets()
        self.ids.empty_box.opacity = 1

        self.manager.transition = FadeTransition(duration=0.22)
        self.manager.current = 'login'