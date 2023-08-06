import json
from io import BytesIO
from pathlib import Path
from typing import List, Optional

from aiogoogle import GoogleAPI
from pydantic import create_model
from tygle.base import REST
from tygle.base.requests import (
    DataRequest,
    DownloadToBufferRequest,
    DownloadToPathRequest,
    UploadFromBufferRequest,
    UploadFromPathRequest,
)
from tygle.client import Client
from tygle_drive.types.enums.files import ExportMimeType, IncludePermissionsForView
from tygle_drive.types.resources.files import File, FileRESTs
from tygle_drive.types.responses.files import FileList


class Files(REST):
    def __init__(self, client: Client, parent: GoogleAPI) -> None:
        self.File = create_model("File", __base__=File)
        self.File.__rests__ = FileRESTs(self)

        self.FileList = create_model(
            "FileList",
            files=(Optional[List[self.File]], None),
            __base__=FileList,
        )

        super().__init__(client, parent)

    def create(
        self,
        file: File,
        /,
        path: Optional[Path] = None,
        buffer: Optional[BytesIO] = None,
        *,
        fields: Optional[str] = None,
        ignore_default_visibility: Optional[bool] = None,
        include_permissions_for_view: Optional[IncludePermissionsForView] = None,
        keep_revision_forever: Optional[bool] = None,
        ocr_language: Optional[str] = None,
        supports_all_drives: Optional[bool] = None,
        use_content_as_indexable_text: Optional[bool] = None,
    ) -> DataRequest[File]:
        if path and buffer:
            raise ValueError("Either path or buffer could be set. Not both.")
        request = self.parent.files.create(
            fields=fields,  # Undocumented, but works.
            ignoreDefaultVisibility=ignore_default_visibility,
            includePermissionsForView=include_permissions_for_view,
            keepRevisionForever=keep_revision_forever,
            ocrLanguage=ocr_language,
            supportsAllDrives=supports_all_drives,
            useContentAsIndexableText=use_content_as_indexable_text,
            upload_file=True if path else None,
            pipe_from=True if buffer else None,
            json=json.loads(file.json(by_alias=True, exclude_unset=True)),
        )

        if path:
            return UploadFromPathRequest(
                self.client, request, path, resource_type=self.File
            )
        if buffer:
            return UploadFromBufferRequest(
                self.client, request, buffer, resource_type=self.File
            )
        return DataRequest(self.client, request, self.File)

    def copy(
        self,
        file_id: str,
        /,
        file: Optional[File] = None,
        *,
        fields: Optional[str] = None,
        ignore_default_visibility: Optional[bool] = None,
        include_labels: Optional[str] = None,
        include_permissions_for_view: Optional[str] = None,
        keep_revision_forever: Optional[bool] = None,
        ocr_language: Optional[str] = None,
        supports_all_drives: Optional[bool] = None,
    ) -> DataRequest[File]:
        return DataRequest(
            self.client,
            self.parent.files.copy(
                fileId=file_id,
                fields=fields,
                ignoreDefaultVisibility=ignore_default_visibility,
                includeLabels=include_labels,
                includePermissionsForView=include_permissions_for_view,
                keepRevisionForever=keep_revision_forever,
                ocrLanguage=ocr_language,
                supportsAllDrives=supports_all_drives,
                json=json.loads(file.json()) if file else None,
            ),
            self.File,
        )

    def export_to_path(
        self,
        file_id: str,
        path: Path,
        /,
        mime_type: ExportMimeType,
        *,
        fields: Optional[str] = None,
    ):
        return DownloadToPathRequest(
            self.client,
            self.parent.files.export(
                fileId=file_id,
                mimeType=mime_type,
                fields=fields,
            ),
            path,
        )

    def export_to_buffer(
        self,
        file_id: str,
        /,
        mime_type: ExportMimeType,
        *,
        fields: Optional[str] = None,
    ):
        return DownloadToBufferRequest(
            self.client,
            self.parent.files.export(
                fileId=file_id,
                mimeType=mime_type,
                fields=fields,
            ),
        )

    def get(
        self,
        file_id: str,
        /,
        *,
        acknowledge_abuse: Optional[bool] = None,
        fields: Optional[str] = None,
        include_permissions_for_view: Optional[IncludePermissionsForView] = None,
        supports_all_drives: Optional[bool] = None,
    ) -> DataRequest[File]:
        return DataRequest(
            self.client,
            self.parent.files.get(
                fileId=file_id,
                acknowledgeAbuse=acknowledge_abuse,
                fields=fields,
                includePermissionsForView=include_permissions_for_view,
                supportsAllDrives=supports_all_drives,
            ),
            self.File,
        )

    def list(
        self,
        /,
        *,
        corpora: Optional[str] = None,
        drive_id: Optional[str] = None,
        fields: Optional[str] = None,
        include_items_from_all_drives: Optional[bool] = None,
        include_permissions_for_view: Optional[str] = None,
        order_by: Optional[str] = None,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
        q: Optional[str] = None,
        spaces: Optional[str] = None,
        supports_all_drives: Optional[bool] = None,
    ) -> DataRequest[FileList]:
        return DataRequest(
            self.client,
            self.parent.files.list(
                corpora=corpora,
                driveId=drive_id,
                fields=fields,
                includeItemsFromAllDrives=include_items_from_all_drives,
                includePermissionsForView=include_permissions_for_view,
                orderBy=order_by,
                pageSize=page_size,
                pageToken=page_token,
                q=q,
                spaces=spaces,
                supportsAllDrives=supports_all_drives,
            ),
            self.FileList,
        )
