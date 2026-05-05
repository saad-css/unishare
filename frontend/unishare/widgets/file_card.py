import os
import urllib.request
from kivymd.uix.card import MDCard

from ..core.config import BASE_URL
from ..core.api import post_json


class FileCard(MDCard):
    # Server-side unique file name used for downloading.
    storage_name = ''

    # Database file ID used for reporting.
    file_id = None

    # Logged-in user ID used when reporting a file.
    user_id = None

    def refresh_lang(self):
        # English-only version: keep labels consistent.
        self.ids.dl_btn.text = 'DOWNLOAD'

    def get_icon_and_color(self, filename):
        # Choose icon based on file extension.
        ext = os.path.splitext(filename)[-1].lower()

        icons = {
            '.pdf': ('file-pdf-box', (0.86, 0.21, 0.21, 1)),
            '.doc': ('file-word-box', (0.13, 0.47, 0.87, 1)),
            '.docx': ('file-word-box', (0.13, 0.47, 0.87, 1)),
            '.ppt': ('file-powerpoint-box', (0.91, 0.46, 0.13, 1)),
            '.pptx': ('file-powerpoint-box', (0.91, 0.46, 0.13, 1)),
            '.xls': ('file-excel-box', (0.13, 0.65, 0.32, 1)),
            '.xlsx': ('file-excel-box', (0.13, 0.65, 0.32, 1)),
            '.zip': ('folder-zip-outline', (0.9, 0.7, 0.1, 1)),
            '.png': ('file-image-outline', (0.56, 0.27, 0.87, 1)),
            '.jpg': ('file-image-outline', (0.56, 0.27, 0.87, 1)),
            '.jpeg': ('file-image-outline', (0.56, 0.27, 0.87, 1)),
        }

        return icons.get(ext, ('file-document-outline', (0.255, 0.647, 0.961, 1)))

    def download_file(self):
        # Download the file using its server-side storage name.
        try:
            filename = self.ids.title.text
            downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            os.makedirs(downloads_dir, exist_ok=True)
            save_path = os.path.join(downloads_dir, filename)

            if not self.storage_name:
                print('Download failed: missing storage_name')
                return

            url = f'{BASE_URL}/download/{self.storage_name}'
            urllib.request.urlretrieve(url, save_path)
            print('Saved to Downloads')

        except Exception as e:
            print('Download failed:', e)

    def report_file(self):
        # Send a file report to the backend for admin review.
        if not self.file_id or not self.user_id:
            print('Report failed: missing file_id or user_id')
            return

        try:
            response = post_json(f'/files/{self.file_id}/report', {
                'user_id': self.user_id,
                'reason': 'Reported by user'
            })
            print('Report response:', response.status_code, response.text)
        except Exception as e:
            print('Report error:', e)
