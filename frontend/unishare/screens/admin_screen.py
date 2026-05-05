from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDFlatButton

from ..core.api import get_json, post_json


class AdminScreen(MDScreen):
    user_id = None
    user_name = ''

    def on_enter(self):
        # Load reports first because reported files are the main admin task.
        self.load_reports()

    def _clear_list(self, message=''):
        # Clear the admin content list and optionally show a message.
        self.ids.admin_list.clear_widgets()
        self.ids.admin_status.text = message

    def _add_item_card(self, title, subtitle, approve_text, reject_text, approve_callback, reject_callback):
        # Build one admin review card with Accept/Reject buttons.
        card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height='178dp',
            padding='14dp',
            spacing='8dp',
            radius=[18, 18, 18, 18],
            elevation=2,
            md_bg_color=(1, 1, 1, 1),
        )

        title_label = MDLabel(
            text=title,
            bold=True,
            theme_text_color='Custom',
            text_color=(0.1, 0.1, 0.1, 1),
            adaptive_height=True,
        )
        subtitle_label = MDLabel(
            text=subtitle,
            theme_text_color='Custom',
            text_color=(0.35, 0.35, 0.35, 1),
            adaptive_height=True,
        )

        actions = MDBoxLayout(size_hint_y=None, height='46dp', spacing='8dp')
        approve_btn = MDFillRoundFlatButton(text=approve_text, size_hint_x=1)
        reject_btn = MDFlatButton(text=reject_text, size_hint_x=1)

        approve_btn.bind(on_release=lambda *_args: approve_callback())
        reject_btn.bind(on_release=lambda *_args: reject_callback())

        actions.add_widget(approve_btn)
        actions.add_widget(reject_btn)

        card.add_widget(title_label)
        card.add_widget(subtitle_label)
        card.add_widget(actions)
        self.ids.admin_list.add_widget(card)

    def load_pending_files(self):
        # Fetch files that need manual admin review and render action cards.
        self._clear_list('Loading pending files...')
        try:
            files = get_json('/admin/pending-files')
        except Exception as e:
            self._clear_list(f'Could not load pending files: {e}')
            return

        self._clear_list('Pending files')
        if not files:
            self.ids.admin_status.text = 'No pending files.'
            return

        for item in files:
            file_id = item['id']
            title = f"File: {item.get('filename', 'Unknown')}"
            subtitle = (
                f"Course: {item.get('course', '-') }\n"
                f"Uploader: {item.get('uploader', '-') }\n"
                f"Reason: {item.get('review_reason') or '-'}"
            )
            self._add_item_card(
                title,
                subtitle,
                'Approve File',
                'Reject File',
                lambda fid=file_id: self.approve_file(fid),
                lambda fid=file_id: self.reject_file(fid),
            )

    def load_reports(self):
        # Fetch user reports and render action cards.
        self._clear_list('Loading reports...')
        try:
            reports = get_json('/admin/reports')
        except Exception as e:
            self._clear_list(f'Could not load reports: {e}')
            return

        self._clear_list('Open reports')
        if not reports:
            self.ids.admin_status.text = 'No open reports.'
            return

        for item in reports:
            report_id = item['id']
            title = f"Reported File: {item.get('filename', 'Unknown')}"
            subtitle = (
                f"Course: {item.get('course', '-') }\n"
                f"Reported by: {item.get('reported_by', '-') }\n"
                f"Reason: {item.get('reason') or '-'}"
            )
            self._add_item_card(
                title,
                subtitle,
                'Accept Report',
                'Reject Report',
                lambda rid=report_id: self.accept_report(rid),
                lambda rid=report_id: self.reject_report(rid),
            )

    def approve_file(self, file_id):
        # Approve a file that is waiting for review.
        try:
            post_json(f'/admin/files/{file_id}/approve', {})
            self.load_pending_files()
        except Exception as e:
            self.ids.admin_status.text = f'Approve failed: {e}'

    def reject_file(self, file_id):
        # Reject a file that is waiting for review.
        try:
            post_json(f'/admin/files/{file_id}/reject', {})
            self.load_pending_files()
        except Exception as e:
            self.ids.admin_status.text = f'Reject failed: {e}'

    def accept_report(self, report_id):
        # Accept a report and remove/reject the reported file.
        try:
            post_json(f'/admin/reports/{report_id}/accept', {})
            self.load_reports()
        except Exception as e:
            self.ids.admin_status.text = f'Accept report failed: {e}'

    def reject_report(self, report_id):
        # Reject a report and keep the file available.
        try:
            post_json(f'/admin/reports/{report_id}/reject', {})
            self.load_reports()
        except Exception as e:
            self.ids.admin_status.text = f'Reject report failed: {e}'

    def logout(self):
        # Return admin to login screen.
        self.manager.transition = FadeTransition(duration=0.22)
        self.manager.current = 'login'
