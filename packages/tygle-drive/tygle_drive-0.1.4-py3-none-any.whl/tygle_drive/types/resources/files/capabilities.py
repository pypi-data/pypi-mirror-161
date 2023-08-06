from typing import Optional

from pydantic import BaseModel, Field


class Capabilities(BaseModel):
    can_edit: Optional[bool] = Field(None, alias="canEdit")
    can_comment: Optional[bool] = Field(None, alias="canComment")
    can_share: Optional[bool] = Field(None, alias="canShare")
    can_copy: Optional[bool] = Field(None, alias="canCopy")
    can_read_revisions: Optional[bool] = Field(None, alias="canReadRevisions")
    can_add_children: Optional[bool] = Field(None, alias="canAddChildren")
    can_delete: Optional[bool] = Field(None, alias="canDelete")
    can_download: Optional[bool] = Field(None, alias="canDownload")
    can_list_children: Optional[bool] = Field(None, alias="canListChildren")
    can_remove_children: Optional[bool] = Field(None, alias="canRemoveChildren")
    can_rename: Optional[bool] = Field(None, alias="canRename")
    can_trash: Optional[bool] = Field(None, alias="canTrash")
    can_untrash: Optional[bool] = Field(None, alias="canUntrash")
    can_change_copy_requires_writer_permission: Optional[bool] = Field(
        None, alias="canChangeCopyRequiresWriterPermission"
    )
    can_delete_children: Optional[bool] = Field(None, alias="canDeleteChildren")
    can_trash_children: Optional[bool] = Field(None, alias="canTrashChildren")
    can_move_children_out_of_drive: Optional[bool] = Field(
        None, alias="canMoveChildrenOutOfDrive"
    )
    can_move_children_within_drive: Optional[bool] = Field(
        None, alias="canMoveChildrenWithinDrive"
    )
    can_move_item_out_of_drive: Optional[bool] = Field(
        None, alias="canMoveItemOutOfDrive"
    )
    can_move_item_within_drive: Optional[bool] = Field(
        None, alias="canMoveItemWithinDrive"
    )
    can_read_drive: Optional[bool] = Field(None, alias="canReadDrive")
    can_modify_content: Optional[bool] = Field(None, alias="canModifyContent")
    can_add_my_drive_parent: Optional[bool] = Field(None, alias="canAddMyDriveParent")
    can_remove_my_drive_parent: Optional[bool] = Field(
        None, alias="canRemoveMyDriveParent"
    )
    can_add_folder_from_another_drive: Optional[bool] = Field(
        None, alias="canAddFolderFromAnotherDrive"
    )
    can_modify_content_restriction: Optional[bool] = Field(
        None, alias="canModifyContentRestriction"
    )
    can_change_security_update_enabled: Optional[bool] = Field(
        None, alias="canChangeSecurityUpdateEnabled"
    )
    can_accept_ownership: Optional[bool] = Field(None, alias="canAcceptOwnership")
