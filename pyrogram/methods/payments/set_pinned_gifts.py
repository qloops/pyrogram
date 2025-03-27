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


from typing import List

import pyrogram
from pyrogram import raw


class SetPinnedGifts:
    async def set_pinned_gifts(
        self: "pyrogram.Client",
        received_gift_ids: List[int],
    ) -> bool:
        """Change the list of pinned gifts on the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            received_gift_ids (List of ``int``):
                New list of pinned gifts.
                All gifts must be upgraded and saved on the profile page first.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Send gift
                await app.set_pinned_gifts(received_gift_ids=[123, 456])
        """
        # TODO: Add channels support for this and other methods
        await self.invoke(
            raw.functions.payments.ToggleStarGiftsPinnedToTop(
                peer=raw.types.InputPeerSelf(),
                stargift=[
                    raw.types.InputSavedStarGiftUser(
                        msg_id=mid
                    ) for mid in received_gift_ids
                ]
            )
        )

        return True
