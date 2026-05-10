from kivymd.uix.screen import MDScreen
from kivy.animation import Animation
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.filemanager import MDFileManager

from ..core.api import get_json, upload_file
from ..widgets.file_card import FileCard

import os


class HomeScreen(MDScreen):
    user_id = None
    user_name = ''
    selected_course = None
    _drawer_open = False
    _file_manager = None

    def on_enter(self):
        self._load_profile()
        self._load_drawer()

    def _load_profile(self):
        if not self.user_id:
            return

        try:
            payload = get_json(f'/user_info/{self.user_id}')

            self.ids.welcome_label.text = f"Hello, {payload['full_name']} "
            self.ids.files_label.text = f"Files Uploaded: {payload['files_count']}"
            self.ids.drawer_name.text = payload['full_name']
            self.ids.drawer_email.text = f"Email: {payload['email']}"

        except Exception as e:
            print("Profile load error:", e)

    def _load_drawer(self):
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
        from kivymd.uix.label import MDLabel

        drawer_list = self.ids.drawer_list
        drawer_list.clear_widgets()

        drawer_list.add_widget(
            self._make_row(
                'arrow-left',
                (0.6, 0.6, 0.6, 1),
                "Back",
                self._load_drawer
            )
        )

        drawer_list.add_widget(
            MDLabel(
                text=major['name'],
                size_hint_y=None,
                height='30dp'
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
        self.selected_course = course
        self.ids.selected_course_label.text = course['name']
        self._load_files(course['id'])

        if self._drawer_open:
            self.toggle_drawer()

    def _load_files(self, course_id):
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
            card.ids.uploader.text = f"By: {uploader}"

            icon, color = card.get_icon_and_color(filename)
            card.ids.file_icon.icon = icon
            card.ids.file_icon.text_color = color

            grid.add_widget(card)

    def _make_row(self, icon, color, text, action):
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.boxlayout import MDBoxLayout

        row = MDBoxLayout(size_hint_y=None, height='52dp')

        icon_widget = MDIconButton(icon=icon, text_color=color)
        icon_widget.bind(on_release=lambda x: action())

        label = MDLabel(text=text)

        row.add_widget(icon_widget)
        row.add_widget(label)

        row.bind(on_touch_down=lambda inst, touch: action() if inst.collide_point(*touch.pos) else False)

        return row

    def toggle_drawer(self):
        panel = self.ids.drawer_panel

        if self._drawer_open:
            Animation(width=0, opacity=0, duration=0.2).start(panel)
        else:
            Animation(width=280, opacity=1, duration=0.2).start(panel)

        self._drawer_open = not self._drawer_open

    def upload_file(self):
        if not self.selected_course:
            print("Select a course first")
            return

        start_path = os.path.expanduser("~")

        self._file_manager = MDFileManager(
            exit_manager=self._close_file_manager,
            select_path=self._file_selected,
        )
        self._file_manager.show(start_path)

    def _close_file_manager(self, *args):
        if self._file_manager:
            self._file_manager.close()

    def _file_selected(self, path):
        self._close_file_manager()

        try:
            response = upload_file(
                '/upload',
                path,
                {
                    'course_id': self.selected_course['id'],
                    'user_id': self.user_id
                }
            )

            print("Upload status:", response.status_code)

            if response.status_code == 201:
                self._load_files(self.selected_course['id'])
                self._load_profile()
            else:
                print("Upload failed:", response.text)

        except Exception as e:
            print("Upload error:", e)

    def logout(self):
        Animation(width=0, opacity=0, duration=0.2).start(self.ids.drawer_panel)

        self._drawer_open = False
        self.selected_course = None

        self.ids.file_grid.clear_widgets()
        self.ids.empty_box.opacity = 1

        self.manager.transition = FadeTransition(duration=0.2)
        self.manager.current = 'login'