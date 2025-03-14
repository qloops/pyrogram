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

from pyrogram import raw, types

from ..object import Object


class KeyboardButton(Object):
    """One button of the reply keyboard.

    For simple text buttons String can be used instead of this object to specify text of the button.
    Optional fields are mutually exclusive.

    Parameters:
        text (``str``):
            Text of the button. If none of the optional fields are used, it will be sent as a message when
            the button is pressed.

        request_contact (``bool``, *optional*):
            If True, the user's phone number will be sent as a contact when the button is pressed.
            Available in private chats only.

        request_location (``bool``, *optional*):
            If True, the user's current location will be sent when the button is pressed.
            Available in private chats only.

        request_poll (:obj:`~pyrogram.types.KeyboardButtonPollType`, *optional*):
            If specified, the user will be asked to create a poll and send it to the bot when the button is pressed.
            Available in private chats only.

        request_users (:obj:`~pyrogram.types.KeyboardButtonRequestUsers`, *optional*):
            If specified, pressing the button will open a list of suitable users.
            Identifiers of selected users will be sent to the bot in a `users_shared` service message.
            Available in private chats only.

        request_chat (:obj:`~pyrogram.types.KeyboardButtonRequestChat`, *optional*):
            If specified, pressing the button will open a list of suitable chats.
            Tapping on a chat will send its identifier to the bot in a `chat_shared` service message.
            Available in private chats only.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            If specified, the described `Web App <https://core.telegram.org/bots/webapps>`_ will be launched when the
            button is pressed.
            The Web App will be able to send a `web_app_data` service message.
            Available in private chats only.
    """
    def __init__(
        self,
        text: str,
        request_contact: bool = None,
        request_location: bool = None,
        request_poll: "types.KeyboardButtonPollType" = None,
        request_users: "types.KeyboardButtonRequestUsers" = None,
        request_chat: "types.KeyboardButtonRequestChat" = None,
        web_app: "types.WebAppInfo" = None,
    ):
        super().__init__()

        self.text = str(text)
        self.request_contact = request_contact
        self.request_location = request_location
        self.request_poll = request_poll
        self.request_users = request_users
        self.request_chat = request_chat
        self.web_app = web_app

    @staticmethod
    def read(b):
        if isinstance(b, raw.types.KeyboardButton):
            return b.text

        if isinstance(b, raw.types.KeyboardButtonRequestPhone):
            return KeyboardButton(
                text=b.text,
                request_contact=True
            )

        if isinstance(b, raw.types.KeyboardButtonRequestGeoLocation):
            return KeyboardButton(
                text=b.text,
                request_location=True
            )

        if isinstance(b, raw.types.KeyboardButtonRequestPoll):
            return KeyboardButton(
                text=b.text,
                request_poll=types.KeyboardButtonPollType(is_quiz=b.quiz)
            )

        if isinstance(b, raw.types.KeyboardButtonRequestPeer):
            if isinstance(b.peer_type, (raw.types.RequestPeerTypeBroadcast, raw.types.RequestPeerTypeChat)):
                user_privileges = getattr(b.peer_type, "user_admin_rights", None)
                bot_privileges = getattr(b.peer_type, "bot_admin_rights", None)

                return KeyboardButton(
                    text=b.text,
                    request_chat=types.KeyboardButtonRequestChat(
                        button_id=b.button_id,
                        chat_is_channel=isinstance(b.peer_type, raw.types.RequestPeerTypeBroadcast),
                        chat_is_created=getattr(b.peer_type, "creator", None),
                        bot_is_member=getattr(b.peer_type, "bot_participant", None),
                        chat_has_username=getattr(b.peer_type, "has_username", None),
                        chat_is_forum=getattr(b.peer_type, "forum", None),
                        user_administrator_rights=types.ChatPrivileges._parse(user_privileges),
                        bot_administrator_rights=types.ChatPrivileges._parse(bot_privileges)
                    )
                )

            if isinstance(b.peer_type, raw.types.RequestPeerTypeUser):
                return KeyboardButton(
                    text=b.text,
                    request_users=types.KeyboardButtonRequestUsers(
                        button_id=b.button_id,
                        user_is_bot=getattr(b.peer_type, "bot", None),
                        user_is_premium=getattr(b.peer_type, "premium", None),
                        max_quantity=getattr(b, "max_quantity", None)
                    )
                )

        if isinstance(b, raw.types.KeyboardButtonSimpleWebView):
            return KeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(
                    url=b.url
                )
            )

    def write(self):
        if self.request_contact:
            return raw.types.KeyboardButtonRequestPhone(text=self.text)
        elif self.request_location:
            return raw.types.KeyboardButtonRequestGeoLocation(text=self.text)
        elif self.request_poll:
            return raw.types.KeyboardButtonRequestPoll(
                text=self.text,
                quiz=self.request_poll.is_quiz
            )
        elif self.request_chat:
            user_privileges = self.request_chat.user_administrator_rights
            bot_privileges = self.request_chat.bot_administrator_rights

            user_admin_rights = raw.types.ChatAdminRights(
                change_info=user_privileges.can_change_info,
                post_messages=user_privileges.can_post_messages,
                post_stories=user_privileges.can_post_stories,
                edit_messages=user_privileges.can_edit_messages,
                edit_stories=user_privileges.can_post_stories,
                delete_messages=user_privileges.can_delete_messages,
                delete_stories=user_privileges.can_delete_stories,
                ban_users=user_privileges.can_restrict_members,
                invite_users=user_privileges.can_invite_users,
                pin_messages=user_privileges.can_pin_messages,
                add_admins=user_privileges.can_promote_members,
                anonymous=user_privileges.is_anonymous,
                manage_call=user_privileges.can_manage_video_chats,
                other=user_privileges.can_manage_chat
            ) if user_privileges else None

            bot_admin_rights = raw.types.ChatAdminRights(
                change_info=bot_privileges.can_change_info,
                post_messages=bot_privileges.can_post_messages,
                post_stories=bot_privileges.can_post_stories,
                edit_messages=bot_privileges.can_edit_messages,
                edit_stories=bot_privileges.can_post_stories,
                delete_messages=bot_privileges.can_delete_messages,
                delete_stories=bot_privileges.can_delete_stories,
                ban_users=bot_privileges.can_restrict_members,
                invite_users=bot_privileges.can_invite_users,
                pin_messages=bot_privileges.can_pin_messages,
                add_admins=bot_privileges.can_promote_members,
                anonymous=bot_privileges.is_anonymous,
                manage_call=bot_privileges.can_manage_video_chats,
                other=bot_privileges.can_manage_chat
            ) if bot_privileges else None

            if self.request_chat.chat_is_channel:
                peer_type = raw.types.RequestPeerTypeBroadcast(
                    creator=self.request_chat.chat_is_created,
                    has_username=self.request_chat.chat_has_username,
                    user_admin_rights=user_admin_rights,
                    bot_admin_rights=bot_admin_rights
                )
            else:
                peer_type = raw.types.RequestPeerTypeChat(
                    creator=self.request_chat.chat_is_created,
                    bot_participant=self.request_chat.bot_is_member,
                    has_username=self.request_chat.chat_has_username,
                    forum=self.request_chat.chat_is_forum,
                    user_admin_rights=user_admin_rights,
                    bot_admin_rights=bot_admin_rights
                )

            return raw.types.KeyboardButtonRequestPeer(
                text=self.text,
                button_id=self.request_chat.button_id,
                peer_type=peer_type,
                max_quantity=1
            )
        elif self.request_users:
            return raw.types.KeyboardButtonRequestPeer(
                text=self.text,
                button_id=self.request_users.button_id,
                peer_type=raw.types.RequestPeerTypeUser(
                    bot=self.request_users.user_is_bot,
                    premium=self.request_users.user_is_premium
                ),
                max_quantity=self.request_users.max_quantity
            )
        elif self.web_app:
            return raw.types.KeyboardButtonSimpleWebView(text=self.text, url=self.web_app.url)
        else:
            return raw.types.KeyboardButton(text=self.text)
