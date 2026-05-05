from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton

from ..core.api import get_json, post_json


class AdminScreen(MDScreen):
    # Filled after admin login.
    admin_user_id = None

    def on_enter(self):
        # Load all files when the admin panel opens.
        self.load_all_files()

    def _clear(self, message=''):
        self.ids.admin_list.clear_widgets()
        self.ids.admin_status.text = message

    def _admin_query(self):
        return f'?admin_user_id={self.admin_user_id}'

    def _admin_payload(self):
        return {'admin_user_id': self.admin_user_id}

    def _add_card(self, title, details, actions):
        # Build one admin card with action buttons.
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height='190dp',
            padding='12dp',
            spacing='8dp',
            radius=[16, 16, 16, 16],
            elevation=1,
        )

        card.add_widget(MDLabel(
            text=title,
            bold=True,
            adaptive_height=True,
            theme_text_color='Custom',
            text_color=(0.1, 0.1, 0.1, 1),
        ))

        card.add_widget(MDLabel(
            text=details,
            adaptive_height=True,
            theme_text_color='Custom',
            text_color=(0.35, 0.35, 0.35, 1),
        ))

        row = MDBoxLayout(size_hint_y=None, height='42dp', spacing='8dp')
        for label, callback, danger in actions:
            btn_cls = MDFlatButton if danger else MDFillRoundFlatButton
            btn = btn_cls(text=label, size_hint_x=1)
            btn.bind(on_release=lambda _btn, cb=callback: cb())
            row.add_widget(btn)

        card.add_widget(row)
        self.ids.admin_list.add_widget(card)

    def load_all_files(self):
        # Show all files regardless of status.
        if not self.admin_user_id:
            self._clear('Admin user is missing. Login again with admin email.')
            return

        try:
            files = get_json(f'/admin/files{self._admin_query()}')
            self._clear(f'All files: {len(files)}')

            if not files:
                self.ids.admin_status.text = 'No files found.'
                return

            for item in files:
                title = f"#{item['id']} - {item['filename']}"
                details = (
                    f"Course: {item.get('course', '')}\n"
                    f"Uploader: {item.get('uploader', '')}\n"
                    f"Status: {item.get('status', '')}\n"
                    f"Reason: {item.get('review_reason') or ''}"
                )
                file_id = item['id']
                self._add_card(title, details, [
                    ('Approve', lambda fid=file_id: self.approve_file(fid), False),
                    ('Reject', lambda fid=file_id: self.reject_file(fid), False),
                    ('Delete', lambda fid=file_id: self.delete_file(fid), True),
                ])
        except Exception as e:
            self._clear(f'Load all files error: {e}')

    def load_pending_files(self):
        # Show files that the algorithm could not decide.
        if not self.admin_user_id:
            self._clear('Admin user is missing. Login again with admin email.')
            return

        try:
            files = get_json(f'/admin/pending-files{self._admin_query()}')
            self._clear(f'Pending files: {len(files)}')

            if not files:
                self.ids.admin_status.text = 'No pending files.'
                return

            for item in files:
                title = f"#{item['id']} - {item['filename']}"
                details = (
                    f"Course: {item.get('course', '')}\n"
                    f"Uploader: {item.get('uploader', '')}\n"
                    f"Reason: {item.get('review_reason') or ''}"
                )
                file_id = item['id']
                self._add_card(title, details, [
                    ('Approve', lambda fid=file_id: self.approve_file(fid), False),
                    ('Reject', lambda fid=file_id: self.reject_file(fid), False),
                    ('Delete', lambda fid=file_id: self.delete_file(fid), True),
                ])
        except Exception as e:
            self._clear(f'Pending files error: {e}')

    def load_reports(self):
        # Show open reports for admin decision.
        if not self.admin_user_id:
            self._clear('Admin user is missing. Login again with admin email.')
            return

        try:
            reports = get_json(f'/admin/reports{self._admin_query()}')
            self._clear(f'Open reports: {len(reports)}')

            if not reports:
                self.ids.admin_status.text = 'No open reports.'
                return

            for item in reports:
                title = f"Report #{item['id']} - {item.get('filename', '')}"
                details = (
                    f"Course: {item.get('course', '')}\n"
                    f"Uploader: {item.get('uploader', '')}\n"
                    f"Reported by: {item.get('reported_by', '')}\n"
                    f"Reason: {item.get('reason', '')}"
                )
                report_id = item['id']
                self._add_card(title, details, [
                    ('Accept Report', lambda rid=report_id: self.accept_report(rid), False),
                    ('Reject Report', lambda rid=report_id: self.reject_report(rid), False),
                ])
        except Exception as e:
            self._clear(f'Reports error: {e}')

    def approve_file(self, file_id):
        # Admin approves a file.
        response = post_json(f'/admin/files/{file_id}/approve', self._admin_payload())
        print('Approve response:', response.status_code, response.text)
        self.load_all_files()

    def reject_file(self, file_id):
        # Admin rejects a file.
        response = post_json(f'/admin/files/{file_id}/reject', self._admin_payload())
        print('Reject response:', response.status_code, response.text)
        self.load_all_files()

    def delete_file(self, file_id):
        # Admin deletes a file permanently without needing a report.
        response = post_json(f'/admin/files/{file_id}/delete', self._admin_payload())
        print('Delete response:', response.status_code, response.text)
        self.load_all_files()

    def accept_report(self, report_id):
        # Accept report and reject the reported file.
        response = post_json(f'/admin/reports/{report_id}/accept', self._admin_payload())
        print('Accept report response:', response.status_code, response.text)
        self.load_reports()

    def reject_report(self, report_id):
        # Reject report and keep the file available.
        response = post_json(f'/admin/reports/{report_id}/reject', self._admin_payload())
        print('Reject report response:', response.status_code, response.text)
        self.load_reports()

    def logout(self):
        # Return admin to login screen.
        self.admin_user_id = None
        self.manager.transition = FadeTransition(duration=0.22)
        self.manager.current = 'login'
