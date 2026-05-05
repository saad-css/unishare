from kivymd.uix.screen import MDScreen

from ..core.api import get_json
from ..widgets.file_card import FileCard


class FilesScreen(MDScreen):
    def refresh_lang(self):
        # English-only version: keep file cards updated.
        for card in self.ids.full_file_grid.children:
            if hasattr(card, "refresh_lang"):
                card.refresh_lang()

    def load(self, course_id, course_name):
        # Load all files for one course into the dedicated files screen.
        self.ids.files_title_lbl.text = course_name

        grid = self.ids.full_file_grid
        grid.clear_widgets()

        try:
            files = get_json(f"/files/{course_id}")
        except Exception:
            files = []

        for item in files:
            card = FileCard()

            card.storage_name = item.get("storage_name", "")
            filename = item.get("filename", "Unknown file")
            uploader = item.get("uploader", "Unknown")

            card.ids.title.text = filename
            card.ids.uploader.text = f"By: {uploader}"

            icon, color = card.get_icon_and_color(filename)
            card.ids.file_icon.icon = icon
            card.ids.file_icon.text_color = color

            card.refresh_lang()
            grid.add_widget(card)