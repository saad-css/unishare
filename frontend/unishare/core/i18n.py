"""English-only text helpers for UniShare."""

STRINGS = {
    'app_name': 'UniShare',
    'app_sub': 'Student Collaboration Platform',
    'email_hint': 'Email',
    'pass_hint': 'Password',
    'login_btn': 'LOGIN',
    'no_account': 'No account? Create one',
    'register_title': 'Create Account',
    'fullname_hint': 'Full Name',
    'create_btn': 'REGISTER',
    'have_acc': 'Already have an account? Login',
    'home_title': 'Home - UniShare',
    'welcome': 'Hello ...',
    'pick_course': 'Select a course from the side panel',
    'empty_title': 'No files yet',
    'empty_sub': 'Start sharing your study materials with classmates',
    'colleges_hdr': 'Majors',
    'logout_lbl': 'Logout',
    'back_lbl': '← Back',
    'files_title': 'Course Files',
    'download_btn': 'DOWNLOAD',
    'report_btn': 'REPORT',
    'upload_snack': 'File uploaded successfully!',
    'upload_fail': 'Upload failed — check connection',
    'pick_first': 'Select a course first',
    'dl_ok': 'Saved to Downloads',
    'dl_fail': 'Download failed — check connection',
    'report_ok': 'Report submitted successfully',
    'report_fail': 'Report failed — check connection',
    'err_fields': 'Please fill in all fields',
    'err_creds': 'Invalid email or password',
    'err_server': 'Server error',
    'err_offline': 'Server is offline',
    'err_unexpected': 'Unexpected error',
    'err_dup': 'Email already registered',
    'err_reg_fail': 'Registration failed',
    'reg_ok': 'Account created successfully!',
}


def t(key: str) -> str:
    """Return English UI text by key."""
    return STRINGS.get(key, key)


def font() -> str:
    """Return the default app font."""
    return 'Roboto'


def ar(text: str) -> str:
    """Compatibility helper kept so old imports do not break."""
    return text
