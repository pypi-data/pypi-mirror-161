from enum import Enum


class AnyMimeType(str, Enum):
    OCTET_STREAM = "application/octet-stream"

    TEXT_HTML = "text/html"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    TEXT_TAB_SEPARATED_VALUES = "text/tab-separated-values"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_SVG_XML = "image/svg+xml"
    ZIP = "application/zip"
    EPUB_ZIP = "application/epub+zip"
    RTF = "application/rtf"
    PDF = "application/pdf"
    OPEN_OFFICE_TEXT = "application/vnd.oasis.opendocument.text"
    OPEN_OFFICE_SPREADSHEET = "application/x-vnd.oasis.opendocument.spreadsheet"
    OPEN_OFFICE_PRESENTATION = "application/vnd.oasis.opendocument.presentation"
    MS_OFFICE_WORD = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    MS_OFFICE_EXCEL = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    MS_OFFICE_POWERPOINT = (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    APP_SCRIPT_JSON = "application/vnd.google-apps.script+json"
    GOOGLE_AUDIO = "application/vnd.google-apps.audio"
    GOOGLE_DOCUMENT = "application/vnd.google-apps.document"
    GOOGLE_DRIVE_SDK = "application/vnd.google-apps.drive-sdk"
    GOOGLE_DRAWING = "application/vnd.google-apps.drawing"
    GOOGLE_FILE = "application/vnd.google-apps.file"
    GOOGLE_FOLDER = "application/vnd.google-apps.folder"
    GOOGLE_FORM = "application/vnd.google-apps.form"
    GOOGLE_FUSIONTABLE = "application/vnd.google-apps.fusiontable"
    GOOGLE_JAM = "application/vnd.google-apps.jam"
    GOOGLE_MAP = "application/vnd.google-apps.map"
    GOOGLE_PHOTO = "application/vnd.google-apps.photo"
    GOOGLE_PRESENTATION = "application/vnd.google-apps.presentation"
    GOOGLE_SCRIPT = "application/vnd.google-apps.script"
    GOOGLE_SHORTCUT = "application/vnd.google-apps.shortcut"
    GOOGLE_SITE = "application/vnd.google-apps.site"
    GOOGLE_SPREADSHEET = "application/vnd.google-apps.spreadsheet"
    GOOGLE_UNKNOWN = "application/vnd.google-apps.unknown"
    GOOGLE_VIDEO = "application/vnd.google-apps.video"
