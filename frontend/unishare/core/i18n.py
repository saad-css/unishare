import os
from kivymd.app import MDApp
from kivy.core.text import LabelBase

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _BIDI_OK = True
except ImportError:
    _BIDI_OK = False

_FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Cairo-Regular.ttf')
if os.path.exists(_FONT_PATH):
    LabelBase.register(name='Cairo', fn_regular=_FONT_PATH)
    ARABIC_FONT = 'Cairo'
else:
    ARABIC_FONT = 'Roboto'

STRINGS = {
    'app_name': {'en': 'UniShare', 'ar': 'UniShare'},
    'app_sub': {'en': 'Student Collaboration Platform', 'ar': 'منصة التعاون الطلابي'},

    # Authentication fields
    'email_hint': {'en': 'Email', 'ar': 'البريد الإلكتروني'},
    'pass_hint': {'en': 'Password', 'ar': 'كلمة المرور'},

    # Login
    'login_title': {'en': 'Student Login', 'ar': 'تسجيل دخول الطالب'},
    'login_btn': {'en': 'LOGIN', 'ar': 'تسجيل الدخول'},
    'no_account': {'en': 'No account? Create one', 'ar': 'ليس لديك حساب؟ إنشاء حساب'},

    # Register
    'register_title': {'en': 'Create Account', 'ar': 'إنشاء حساب جديد'},
    'fullname_hint': {'en': 'Full Name', 'ar': 'الاسم الكامل'},
    'create_btn': {'en': 'REGISTER', 'ar': 'إنشاء الحساب'},
    'have_acc': {'en': 'Already have an account? Login', 'ar': 'لديك حساب؟ تسجيل الدخول'},

    # Home
    'home_title': {'en': 'Home - UniShare', 'ar': 'الرئيسية - UniShare'},
    'welcome': {'en': 'Hello ...', 'ar': 'مرحباً ...'},
    'files_count': {'en': 'Files Uploaded: 0', 'ar': 'الملفات المرفوعة: 0'},
    'pick_course': {'en': 'Select a course from the side panel', 'ar': 'اختر مادة من القائمة الجانبية'},
    'empty_title': {'en': 'No files yet', 'ar': 'لا توجد ملفات بعد'},
    'empty_sub': {'en': 'Start sharing your study materials with classmates', 'ar': 'ابدأ بمشاركة ملفاتك الدراسية مع زملائك'},
    'colleges_hdr': {'en': 'Majors', 'ar': 'التخصصات'},
    'logout_lbl': {'en': 'Logout', 'ar': 'تسجيل الخروج'},
    'back_lbl': {'en': '← Back', 'ar': 'رجوع ←'},

    # Files
    'files_title': {'en': 'Course Files', 'ar': 'ملفات المادة'},
    'download_btn': {'en': 'DOWNLOAD', 'ar': 'تحميل'},

    # Upload / Download
    'upload_snack': {'en': 'File uploaded successfully!', 'ar': 'تم رفع الملف بنجاح!'},
    'upload_fail': {'en': 'Upload failed — check connection', 'ar': 'فشل الرفع — تحقق من الاتصال'},
    'pick_first': {'en': 'Select a course first', 'ar': 'اختر مادة أولاً'},
    'dl_ok': {'en': 'Saved to Downloads', 'ar': 'تم الحفظ في التنزيلات'},
    'dl_fail': {'en': 'Download failed — check connection', 'ar': 'فشل التحميل — تحقق من الاتصال'},

    # Errors
    'err_fields': {'en': 'Please fill in all fields', 'ar': 'يرجى تعبئة جميع الحقول'},
    'err_creds': {'en': 'Invalid email or password', 'ar': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'},
    'err_server': {'en': 'Server error', 'ar': 'خطأ في الخادم'},
    'err_offline': {'en': 'Server is offline', 'ar': 'الخادم غير متاح'},
    'err_unexpected': {'en': 'Unexpected error', 'ar': 'حدث خطأ غير متوقع'},
    'err_dup': {'en': 'Email already registered', 'ar': 'البريد الإلكتروني مسجل مسبقاً'},
    'err_reg_fail': {'en': 'Registration failed', 'ar': 'فشل إنشاء الحساب'},
    'reg_ok': {'en': 'Account created successfully!', 'ar': 'تم إنشاء الحساب بنجاح!'},

    # Shared labels
    'by_lbl': {'en': 'By', 'ar': 'بواسطة'},
}


def ar(text: str) -> str:
    # Reshape Arabic text when the optional libraries are available.
    if not _BIDI_OK:
        return text
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def t(key: str) -> str:
    # Read the translated text based on the current app language.
    app = MDApp.get_running_app()
    lang = getattr(app, 'lang', 'en') if app else 'en'
    text = STRINGS.get(key, {}).get(lang, key)
    return ar(text) if lang == 'ar' else text


def font() -> str:
    # Use the Arabic font when the app is switched to Arabic.
    app = MDApp.get_running_app()
    lang = getattr(app, 'lang', 'en') if app else 'en'
    return ARABIC_FONT if lang == 'ar' else 'Roboto'