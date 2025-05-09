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

from typing import Dict, List

import pyrogram
from pyrogram import raw, types

from ..object import Object


class GiftsForResale(Object):
    """Describes gifts available for resale.

    Parameters:
        total_count (``int``):
            Total number of gifts found.

        gifts (List of :obj:`~pyrogram.types.Gift`):
            List of gifts available for resale.

        models (List of :obj:`~pyrogram.types.GiftAttribute`):
            Available models. For :meth:`~pyrogram.Client.search_gifts_for_resale` requests without offset and attributes only.

        symbols (List of :obj:`~pyrogram.types.GiftAttribute`):
            Available symbols. For :meth:`~pyrogram.Client.search_gifts_for_resale` requests without offset and attributes only.

        backdrops (List of :obj:`~pyrogram.types.GiftAttribute`):
            Available backdrops. For :meth:`~pyrogram.Client.search_gifts_for_resale` requests without offset and attributes only.
    """

    def __init__(
        self,
        *,
        total_count: int,
        gifts: List["types.Gift"],
        models: List["types.GiftAttribute"],
        symbols: List["types.GiftAttribute"],
        backdrops: List["types.GiftAttribute"]
    ):
        super().__init__()

        self.total_count = total_count
        self.gifts = gifts
        self.models = models
        self.symbols = symbols
        self.backdrops = backdrops

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        resale_gifts: "raw.base.payments.ResaleStarGifts",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {}
    ):
        models = types.List()
        symbols = types.List()
        backdrops = types.List()

        if resale_gifts.attributes:
            for attribute in resale_gifts.attributes:
                if isinstance(attribute, raw.types.StarGiftAttributeModel):
                    models.append(types.GiftAttribute._parse(client, attribute, users, chats))
                elif isinstance(attribute, raw.types.StarGiftAttributePattern):
                    symbols.append(types.GiftAttribute._parse(client, attribute, users, chats))
                elif isinstance(attribute, raw.types.StarGiftAttributeBackdrop):
                    backdrops.append(types.GiftAttribute._parse(client, attribute, users, chats))

        return GiftsForResale(
            total_count=resale_gifts.count,
            gifts=types.List(types.Gift._parse(client, gift, users, chats) for gift in resale_gifts.gifts),
            models=models or None,
            symbols=symbols or None,
            backdrops=backdrops or None
        )
