from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Literal, Optional, Union

from aiofiles.tempfile import AsyncBufferedIOBase
from pydantic import Field, PrivateAttr
from tygle.base import Resource, RESTs
from tygle_drive.types.enums.files import (
    AnyMimeType,
    ExportMimeType,
    IncludePermissionsForView,
    Space,
)
from tygle_drive.types.resources.permissions import Permission

from .capabilities import Capabilities
from .content_hints import ContentHints
from .content_restriction import ContentRestriction
from .image_media_metadata import ImageMediaMetadata
from .link_share_metadata import LinkShareMetadata
from .user import User
from .video_media_metadata import VideoMediaMetadata

if TYPE_CHECKING:
    from tygle_drive.rest.files import Files


class FileRESTs(RESTs):
    def __init__(self, Files: "Files") -> None:
        self.Files = Files


class File(Resource):
    __rests__: ClassVar[FileRESTs] = PrivateAttr()

    def get(
        self,
        /,
        *,
        acknowledge_abuse: Optional[bool] = None,
        fields: Optional[str] = None,
        include_permissions_for_view: Optional[IncludePermissionsForView] = None,
        supports_all_drives: Optional[bool] = None,
    ):
        if self.id:
            return self.__rests__.Files.get(
                self.id,
                acknowledge_abuse=acknowledge_abuse,
                fields=fields,
                include_permissions_for_view=include_permissions_for_view,
                supports_all_drives=supports_all_drives,
            )
        raise ValueError("id attribute of File object wasn't set.")

    def create(
        self,
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
    ):
        return self.__rests__.Files.create(
            self,
            path,
            buffer,
            fields=fields,
            ignore_default_visibility=ignore_default_visibility,
            include_permissions_for_view=include_permissions_for_view,
            keep_revision_forever=keep_revision_forever,
            ocr_language=ocr_language,
            supports_all_drives=supports_all_drives,
            use_content_as_indexable_text=use_content_as_indexable_text,
        )

    def copy(
        self,
        /,
        file: Optional["File"] = None,
        *,
        fields: Optional[str] = None,
        ignore_default_visibility: Optional[bool] = None,
        include_labels: Optional[str] = None,
        include_permissions_for_view: Optional[str] = None,
        keep_revision_forever: Optional[bool] = None,
        ocr_language: Optional[str] = None,
        supports_all_drives: Optional[bool] = None,
    ):
        return self.__rests__.Files.copy(
            self.id,
            file,
            fields=fields,
            ignore_default_visibility=ignore_default_visibility,
            include_labels=include_labels,
            include_permissions_for_view=include_permissions_for_view,
            keep_revision_forever=keep_revision_forever,
            ocr_language=ocr_language,
            supports_all_drives=supports_all_drives,
        )

    def export_to_path(
        self,
        path: Path,
        /,
        mime_type: ExportMimeType,
        *,
        fields: Optional[str] = None,
    ):
        if self.id:
            return self.__rests__.Files.export_to_path(
                self.id, path, mime_type, fields=fields
            )
        raise ValueError("id attribute of File object wasn't set.")

    def export_to_buffer(
        self,
        buffer: AsyncBufferedIOBase,
        /,
        mime_type: ExportMimeType,
        *,
        fields: Optional[str] = None,
    ):
        if self.id:
            return self.__rests__.Files.export_to_buffer(
                self.id, buffer, mime_type, fields=fields
            )
        raise ValueError("id attribute of File object wasn't set.")

    kind: Literal["drive#file"] = Field("drive#file")
    id: Optional[str] = Field(
        None,
    )
    name: Optional[str] = Field(None)
    mime_type: Optional[Union[AnyMimeType, str]] = Field(None, alias="mimeType")
    description: Optional[str] = Field(None)
    starred: Optional[bool] = Field(None)
    trashed: Optional[bool] = Field(None)
    explicitly_trashed: Optional[bool] = Field(None, alias="explicitlyTrashed")
    parents: Optional[List[str]] = Field(None)
    properties: Optional[Dict[str, Any]] = Field(None)
    app_properties: Optional[Dict[str, Any]] = Field(None, alias="appProperties")
    spaces: Optional[List[Space]] = Field(None)
    version: Optional[int] = Field(None)
    web_content_link: Optional[str] = Field(None, alias="webContentLink")
    web_view_link: Optional[str] = Field(None, alias="webViewLink")
    icon_link: Optional[str] = Field(None, alias="iconLink")
    thumbnail_link: Optional[str] = Field(None, alias="thumbnailLink")
    viewed_by_me: Optional[bool] = Field(None, alias="viewedByMe")
    viewed_by_me_time: Optional[datetime] = Field(None, alias="viewedByMeTime")
    created_time: Optional[datetime] = Field(None, alias="createdTime")
    modified_time: Optional[datetime] = Field(None, alias="modifiedTime")
    modified_by_me_time: Optional[datetime] = Field(None, alias="modifiedByMeTime")
    shared_with_me_time: Optional[datetime] = Field(None, alias="sharedWithMeTime")
    sharing_user: Optional[User] = Field(None, alias="sharingUser")
    owners: Optional[List[User]] = Field(None)
    last_modifying_user: Optional[User] = Field(None, alias="lastModifyingUser")
    shared: Optional[bool] = Field(None)
    owned_by_me: Optional[bool] = Field(None, alias="ownedByMe")
    writers_can_share: Optional[bool] = Field(None, alias="writersCanShare")
    permissions: Optional[Permission] = Field(None)
    folder_color_rgb: Optional[str] = Field(None, alias="folderColorRgb")
    original_filename: Optional[str] = Field(None, alias="originalFilename")
    full_file_extension: Optional[str] = Field(None, alias="fullFileExtension")
    file_extension: Optional[str] = Field(None, alias="fileExtension")
    md5_checksum: Optional[str] = Field(None, alias="md5Checksum")
    size: Optional[int] = Field(None)
    quota_bytes_used: Optional[int] = Field(None, alias="quotaBytesUsed")
    head_revision_id: Optional[str] = Field(None, alias="headRevisionId")
    content_hints: Optional[ContentHints] = Field(None, alias="contentHints")
    image_media_metadata: Optional[ImageMediaMetadata] = Field(
        None, alias="imageMediaMetadata"
    )
    video_media_metadata: Optional[VideoMediaMetadata] = Field(
        None, alias="videoMediaMetadata"
    )
    capabilities: Optional[Capabilities] = Field(None)
    is_app_authorized: Optional[bool] = Field(None, alias="isAppAuthorized")
    has_thumbnail: Optional[bool] = Field(None, alias="hasThumbnail")
    thumbnail_version: Optional[int] = Field(None, alias="thumbnailVersion")
    modified_by_me: Optional[bool] = Field(None, alias="modifiedByMe")
    trashing_user: Optional[User] = Field(None, alias="trashingUser")
    trashed_time: Optional[datetime] = Field(None, alias="trashedTime")
    has_augmented_permissions: Optional[bool] = Field(
        None, alias="hasAugmentedPermissions"
    )
    permission_ids: Optional[List[str]] = Field(None, alias="permissionIds")
    copy_requires_writer_permission: Optional[bool] = Field(
        None, alias="copyRequiresWriterPermission"
    )
    export_links: Optional[Dict[str, Any]] = Field(None, alias="exportLinks")
    drive_id: Optional[str] = Field(None, alias="driveId")
    shortcut_details: Optional[Dict[str, Any]] = Field(None, alias="shortcutDetails")
    content_restrictions: Optional[List[ContentRestriction]] = Field(
        None, alias="contentRestrictions"
    )
    resource_key: Optional[str] = Field(None, alias="resourceKey")
    link_share_metadata: Optional[LinkShareMetadata] = Field(
        None,
        alias="linkShareMetadata",
    )
