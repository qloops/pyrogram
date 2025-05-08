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
from typing import Union

import pyrogram
from pyrogram import errors, raw, types, utils


class TransferGift:
    async def transfer_gift(
        self: "pyrogram.Client",
        owned_gift_id: str,
        new_owner_chat_id: Union[int, str],
        # stars_count: int = None,
        business_connection_id: str = None
    ) -> "types.Message":
        """Transfers an owned unique gift to another user.

        .. note::

            Requires the `can_transfer_and_upgrade_gifts` business bot right.
            Additionally requires the `can_transfer_stars` business bot right if the upgrade is paid.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            owned_gift_id (``str``):
                Unique identifier of the regular gift that should be transferred.
                For a user gift, you can use the message ID (int) of the gift message.
                For a channel gift, you can use the packed format `chatID_savedID` (str).
                For a upgraded gift, you can use the gift link.

            new_owner_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat you want to transfer the star gift to.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.
                For bots only.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Example:
            .. code-block:: python

                # Transfer gift to another user
                await app.transfer_gift(owned_gift_id="123", new_owner_chat_id=123)
        """
        owned_gift_id = str(owned_gift_id)

        saved_gift_match = re.match(r"^(\d+)_(\d+)$", owned_gift_id)
        slug_match = self.UPGRADED_GIFT_RE.match(owned_gift_id)

        if saved_gift_match:
            stargift = raw.types.InputSavedStarGiftChat(
                peer=await self.resolve_peer(saved_gift_match.group(1)),
                saved_id=int(saved_gift_match.group(2))
            )
        elif slug_match:
            stargift = raw.types.InputSavedStarGiftSlug(
                slug=slug_match.group(1)
            )
        else:
            stargift = raw.types.InputSavedStarGiftUser(
                msg_id=int(owned_gift_id)
            )

        peer = await self.resolve_peer(new_owner_chat_id)

        try:
            r = await self.invoke(
                raw.functions.payments.TransferStarGift(
                    stargift=stargift,
                    to_id=peer
                ),
                business_connection_id=business_connection_id
            )
        except errors.PaymentRequired:
            invoice = raw.types.InputInvoiceStarGiftTransfer(
                stargift=stargift,
                to_id=peer
            )

            r = await self.invoke(
                raw.functions.payments.SendStarsForm(
                    form_id=(await self.invoke(
                        raw.functions.payments.GetPaymentForm(
                            invoice=invoice
                        ),
                        business_connection_id=business_connection_id
                    )).form_id,
                    invoice=invoice
                ),
                business_connection_id=business_connection_id
            )

        return (
            await utils.parse_messages(
                client=self,
                messages=r.updates if isinstance(r, raw.types.payments.PaymentResult) else r,
                business_connection_id=business_connection_id
            )
        )[0]
