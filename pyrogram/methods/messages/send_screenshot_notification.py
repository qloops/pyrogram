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

from typing import Union

import pyrogram
from pyrogram import types, raw

class SendScreenshotNotification:
    async def send_screenshot_notification(
        self: "pyrogram.Client",
        chat_id: Union[int, str]
    ) -> "types.Message":
        """Notify the other user in a private chat that a screenshot of the chat was taken.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent service message is returned.
        """

        r = await self.invoke(
            raw.functions.messages.SendScreenshotNotification(
                peer=await self.resolve_peer(chat_id),
                reply_to=raw.types.InputReplyToMessage(reply_to_msg_id=0),
                random_id=self.rnd_id()
            )
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateNewMessage,
                            raw.types.UpdateNewChannelMessage,
                            raw.types.UpdateNewScheduledMessage,
                            raw.types.UpdateBotNewBusinessMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats},
                    is_scheduled=isinstance(i, raw.types.UpdateNewScheduledMessage),
                    business_connection_id=getattr(i, "connection_id", None)
                )
