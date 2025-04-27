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

import re

import pyrogram
from pyrogram import raw


class ShowGift:
    async def show_gift(
        self: "pyrogram.Client",
        owned_gift_id: str
    ) -> bool:
        """Display gift on the current user's or the channel's profile page.

        .. note::

            Requires `can_post_messages` administrator right in the channel chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owned_gift_id (``str``):
                Identifier of the gift.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Show gift in user profile
                await app.show_gift(owned_gift_id="123")

                # Show gift in channel (owned_gift_id packed in format chatID_savedID)
                await app.show_gift(owned_gift_id="123_456")
        """
        match = re.search(r"(\d+)_(\d+)", str(owned_gift_id))

        if match:
            stargift = raw.types.InputSavedStarGiftChat(
                peer=await self.resolve_peer(match.group(1)),
                saved_id=int(match.group(2))
            )
        else:
            stargift = raw.types.InputSavedStarGiftUser(
                msg_id=int(owned_gift_id)
            )

        r = await self.invoke(
            raw.functions.payments.SaveStarGift(
                stargift=stargift,
                unsave=False
            )
        )

        return r
