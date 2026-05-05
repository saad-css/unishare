import os

from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.filemanager import MDFileManager

from ..core.api import get_json, upload_file
from ..core.i18n import t, font
from ..widgets.file_card import FileCard


class HomeScreen(MDScreen):
    user_id = None
    user_name = ''
    is_admin = False
    selected_course = None
    _drawer_open = False
    _file_manager = None

    def on_enter(self):
        # Reload profile and major list every time the user enters the screen.
        self._load_profile()
        self._load_drawer()
        self.refresh_lang()

    def refresh_lang(self):
        # English-only UI refresh.
        self.ids.home_title_lbl.text = t('home_title')
        self.ids.selected_course_label.font_name = font()
        self.ids.empty_title_lbl.text = t('empty_title')
        self.ids.empty_sub_lbl.text = t('empty_sub')
        self.ids.colleges_hdr_lbl.text = t('colleges_hdr')
        self.ids.logout_lbl.text = t('logout_lbl')

        if self.selected_course:
            self.ids.selected_course_label.text = self.selected_course.get('name', '')
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
            self.ids.welcome_label.text = f"Hello, {payload['full_name']} 👋"
            self.ids.files_label.text = f"Files Uploaded: {payload['files_count']}"
            self.ids.drawer_name.text = payload['full_name']
            self.ids.drawer_email.text = f"Email: {payload['email']}"
        except Exception as e:
            # Keep the screen usable even if profile loading fails.
            print('Profile load error:', e)
            self.ids.welcome_label.text = t('welcome')

    def _load_drawer(self):
        # Fetch majors from the API and render them as drawer rows.
        drawer_list = self.ids.drawer_list
        drawer_list.clear_widgets()

        try:
            majors = get_json('/majors')
        except Exception as e:
            print('Majors load error:', e)
            majors = []

        for major in majors:
            row = self._make_row(
                'book-outline',
                (0.255, 0.647, 0.961, 1),
                major['name'],
                lambda m=major: self._load_courses(m),
            )
            drawer_list.add_widget(row)

    def _load_courses(self, major):
        # Replace the majors list with the selected major's courses.
        from kivymd.uix.label import MDLabel

        drawer_list = self.ids.drawer_list
        drawer_list.clear_widgets()

        drawer_list.add_widget(
            self._make_row('arrow-left', (0.6, 0.6, 0.6, 1), t('back_lbl'), self._load_drawer)
        )

        drawer_list.add_widget(
            MDLabel(
                text=major['name'],
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
            print('Courses load error:', e)
            courses = []

        for course in courses:
            row = self._make_row(
                'folder-outline',
                (0.133, 0.647, 0.322, 1),
                course['name'],
                lambda c=course: self._select_course(c),
            )
            drawer_list.add_widget(row)

    def _select_course(self, course):
        # Update the selected course state and load its files into the grid.
        self.selected_course = course
        self.ids.selected_course_label.text = course['name']
        self._load_files(course['id'])

        if self._drawer_open:
            self.toggle_drawer()

    def _load_files(self, course_id):
        # Fetch course files from the API and rebuild the file cards.
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

        row = MDBoxLayout(size_hint_y=None, height='52dp', padding=['16dp', '0dp'], spacing='10dp')

        icon_widget = MDIconButton(
            icon=icon,
            theme_text_color='Custom',
            text_color=icon_color,
            size_hint=(None, None),
            size=('32dp', '52dp'),
            pos_hint={'center_y': 0.5},
        )
        icon_widget.bind(on_release=lambda _x: on_tap())

        label = MDLabel(
            text=text,
            font_style='Body1',
            theme_text_color='Custom',
            text_color=(0.15, 0.15, 0.15, 1),
            valign='center',
            font_name=font(),
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
            Animation(width=260, opacity=1, duration=0.22).start(panel)
        self._drawer_open = not self._drawer_open

    def upload_file(self):
        # Open the native file manager and upload the selected file.
        if not self.selected_course:
            print(t('pick_first'))
            return

        self._file_manager = MDFileManager(
            exit_manager=lambda *_args: self._file_manager.close(),
            select_path=self._file_selected,
        )
        self._file_manager.show(os.path.expanduser('~'))

    def _file_selected(self, path):
        # Upload the selected local file to the backend.
        self._file_manager.close()
        try:
            response = upload_file('/upload', path, {
                'course_id': str(self.selected_course['id']),
                'user_id': str(self.user_id),
            })
            print('Upload response:', response.status_code, response.text)
            self._load_files(self.selected_course['id'])
            self._load_profile()
        except Exception as e:
            print('Upload error:', e)
            print(t('upload_fail'))

    def logout(self):
        # Clear the user state and return to login.
        if self._drawer_open:
            Animation(width=0, opacity=0, duration=0.18).start(self.ids.drawer_panel)
        self._drawer_open = False
        self.selected_course = None
        self.ids.file_grid.clear_widgets()
        self.ids.empty_box.opacity = 1
        self.manager.transition = FadeTransition(duration=0.22)
        self.manager.current = 'login'
