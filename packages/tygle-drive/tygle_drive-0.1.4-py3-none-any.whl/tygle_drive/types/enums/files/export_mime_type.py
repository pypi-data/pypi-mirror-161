from enum import Enum


class ExportMimeType(str, Enum):
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
