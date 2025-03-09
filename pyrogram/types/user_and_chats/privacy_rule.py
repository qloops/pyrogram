#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from typing import List, Optional

from pyrogram import raw, types
from ..object import Object


class PrivacyRule(Object):
    """A privacy rule.

    Parameters:
        allow_all (``bool``, *optional*):
            Allow all users.

        allow_bots (``bool``, *optional*):
            Allow only bots.

        allow_chats (``bool``, *optional*):
            Allow only participants of certain chats.

        allow_close_friends (``bool``, *optional*):
            Allow only close friends.

        allow_contacts (``bool``, *optional*):
            Allow contacts only.

        allow_premium (``bool``, *optional*):
            Allow only users with a Premium subscription.
            Currently only usable for :obj:`~pyrogram.enums.PrivacyKey.CHAT_INVITE`.

        allow_users (``bool``, *optional*):
            Allow only participants of certain users.

        users (List of :obj:`~pyrogram.types.User`, *optional*):
            List of users.

        chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
            List of chats.
    """

    def __init__(
        self, *,
        allow_all: Optional[bool] = None,
        allow_bots: Optional[bool] = None,
        allow_chats: Optional[bool] = None,
        allow_close_friends: Optional[bool] = None,
        allow_contacts: Optional[bool] = None,
        allow_premium: Optional[bool] = None,
        allow_users: Optional[bool] = None,
        users: Optional[List["types.User"]] = None,
        chats: Optional[List["types.Chat"]] = None
    ):
        super().__init__(None)

        self.allow_all = allow_all
        self.allow_bots = allow_bots
        self.allow_chats = allow_chats
        self.allow_close_friends = allow_close_friends
        self.allow_contacts = allow_contacts
        self.allow_premium = allow_premium
        self.allow_users = allow_users
        self.users = users
        self.chats = chats

    @staticmethod
    def _parse(client, rule: "raw.base.PrivacyRule", users: dict, chats: dict) -> "PrivacyRule":
        allow_all = None
        allow_bots = None
        allow_chats = None
        allow_close_friends = None
        allow_contacts = None
        allow_premium = None
        allow_users = None

        parsed_users = None
        parsed_chats = None

        if isinstance(
            rule,
            (
                raw.types.PrivacyValueAllowUsers,
                raw.types.PrivacyValueDisallowUsers
            )
        ):
            parsed_users = types.List(types.User._parse(client, users.get(i)) for i in rule.users) or None

        if isinstance(
            rule,
            (
                raw.types.PrivacyValueAllowChatParticipants,
                raw.types.PrivacyValueDisallowChatParticipants
            )
        ):
            parsed_chats = types.List(types.Chat._parse_chat(client, chats.get(i)) for i in rule.chats) or None

        if isinstance(rule, raw.types.PrivacyValueAllowAll):
            allow_all = True
        elif isinstance(rule, raw.types.PrivacyValueDisallowAll):
            allow_all = False

        if isinstance(rule, raw.types.PrivacyValueAllowBots):
            allow_bots = True
        elif isinstance(rule, raw.types.PrivacyValueDisallowBots):
            allow_bots = False

        if isinstance(rule, raw.types.PrivacyValueAllowCloseFriends):
            allow_close_friends = True

        if isinstance(rule, raw.types.PrivacyValueAllowContacts):
            allow_contacts = True
        elif isinstance(rule, raw.types.PrivacyValueDisallowContacts):
            allow_contacts = False

        if isinstance(rule, raw.types.PrivacyValueAllowPremium):
            allow_premium = True

        if isinstance(rule, raw.types.PrivacyValueAllowUsers):
            allow_users = True
        elif isinstance(rule, raw.types.PrivacyValueDisallowUsers):
            allow_users = False

        return PrivacyRule(
            allow_all=allow_all,
            allow_bots=allow_bots,
            allow_chats=allow_chats,
            allow_close_friends=allow_close_friends,
            allow_contacts=allow_contacts,
            allow_premium=allow_premium,
            allow_users=allow_users,
            users=parsed_users,
            chats=parsed_chats
        )
