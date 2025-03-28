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

from datetime import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class AllowedGiftsSettings(Object):
    """Accepts gift types.

    Parameters:
        limited_gifts (``bool``, *optional*):
            True, if limited gifts are allowed.

        unlimited_gifts (``bool``, *optional*):
            True, if unlimited gifts are allowed.

        unique_gifts (``bool``, *optional*):
            True, if unique gifts are allowed.

        premium_subscription (``bool``, *optional*):
            True, if premium subscription gifts are allowed.
    """

    def __init__(
        self,
        *,
        limited_gifts: Optional[bool] = None,
        unlimited_gifts: Optional[bool] = None,
        unique_gifts: Optional[bool] = None,
        premium_subscription: Optional[bool] = None,
    ):
        super().__init__()

        self.limited_gifts = limited_gifts
        self.unlimited_gifts = unlimited_gifts
        self.unique_gifts = unique_gifts
        self.premium_subscription = premium_subscription

    @staticmethod
    def _parse(disallowed_gifts: "raw.types.DisallowedGiftsSettings") -> Optional["AllowedGiftsSettings"]:
        if not disallowed_gifts:
            return None

        return AllowedGiftsSettings(
            limited_gifts=not disallowed_gifts.disallow_limited_stargifts,
            unlimited_gifts=not disallowed_gifts.disallow_unlimited_stargifts,
            unique_gifts=not disallowed_gifts.disallow_unique_stargifts,
            premium_subscription=not disallowed_gifts.disallow_premium_gifts,
        )

    def write(self) -> "raw.types.DisallowedGiftsSettings":
        return raw.types.DisallowedGiftsSettings(
            disallow_unlimited_stargifts=not self.unlimited_gifts,
            disallow_limited_stargifts=not self.limited_gifts,
            disallow_unique_stargifts=not self.unique_gifts,
            disallow_premium_gifts=not self.premium_subscription,
        )
