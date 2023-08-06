#
# Copyright 2021-2022 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from typing import Optional, TYPE_CHECKING

import trafaret as t

from datarobot._compat import String
from datarobot.models.api_object import APIObject

if TYPE_CHECKING:
    from mypy_extensions import TypedDict

    class SharingAccessPayload(TypedDict, total=False):
        username: str
        role: str
        can_share: bool
        can_use_data: bool


class SharingAccess(APIObject):
    """Represents metadata about whom a entity (e.g. a data store) has been shared with

    .. versionadded:: v2.14

    Currently :py:class:`DataStores <datarobot.DataStore>`,
    :py:class:`DataSources <datarobot.DataSource>`,
    :py:class:`Datasets <datarobot.models.Dataset>`,
    :py:class:`Projects <datarobot.models.Project>` (new in version v2.15) and
    :py:class:`CalendarFiles <datarobot.CalendarFile>` (new in version 2.15) can be shared.

    This class can represent either access that has already been granted, or be used to grant access
    to additional users.

    Attributes
    ----------
    username : str
        a particular user
    role : str or None
        if a string, represents a particular level of access and should be one of
        ``datarobot.enums.SHARING_ROLE``.  For more information on the specific access levels, see
        the :ref:`sharing <sharing>` documentation.  If None, can be passed to a `share`
        function to revoke access for a specific user.
    can_share : bool or None
        if a bool, indicates whether this user is permitted to further share.  When False, the
        user has access to the entity, but can only revoke their own access but not modify any
        user's access role.  When True, the user can share with any other user at a access role up
        to their own.  May be None if the SharingAccess was not retrieved from the DataRobot server
        but intended to be passed into a `share` function; this will be equivalent to passing True.
    can_use_data : bool or None
        if a bool, indicates whether this user should be able to view, download and process data
        (use to create projects, predictions, etc). For OWNER can_use_data is always True. If role
        is empty canUseData is ignored.
    user_id : str or None
        the id of the user
    """

    _converter = t.Dict(
        {
            t.Key("username"): String,
            t.Key("role"): String,
            t.Key("can_share", default=None): t.Or(t.Bool, t.Null),
            t.Key("can_use_data", default=None): t.Or(t.Bool, t.Null),
            t.Key("user_id", default=None): t.Or(String, t.Null),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        username: str,
        role: str,
        can_share: Optional[bool] = None,
        can_use_data: Optional[bool] = None,
        user_id: Optional[str] = None,
    ) -> None:
        self.username = username
        self.role = role
        self.can_share = can_share
        self.can_use_data = can_use_data
        self.user_id = user_id

    def __repr__(self) -> str:
        return (
            "{cls}(username: {username}, role: {role}, "
            "can_share: {can_share}, can_use_data: {can_use_data}, user_id: {user_id})"
        ).format(
            cls=self.__class__.__name__,
            username=self.username,
            role=self.role,
            can_share=self.can_share,
            can_use_data=self.can_use_data,
            user_id=self.user_id,
        )

    def collect_payload(self) -> "SharingAccessPayload":
        """Set up the dict that should be sent to the server in order to share this

        Returns
        -------
        payload : dict
        """
        payload: "SharingAccessPayload" = {"username": self.username, "role": self.role}
        if self.can_share is not None:
            payload["can_share"] = self.can_share
        if self.can_use_data is not None:
            payload["can_use_data"] = self.can_use_data
        return payload
