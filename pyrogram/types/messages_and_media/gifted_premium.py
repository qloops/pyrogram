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

import random

from pyrogram import raw, types, utils

from ..object import Object


class GiftedPremium(Object):
    """Telegram Premium was gifted to the user.

    Parameters:
        gifter (:obj:`~pyrogram.types.User`, *optional*):
            User that gifted Telegram Premium.
            None if the gift was anonymous.

        receiver (:obj:`~pyrogram.types.User`):
            User that received Telegram Premium.

        currency (``str``):
            Currency for the paid amount.

        amount (``int``):
            The paid amount, in the smallest units of the currency.

        cryptocurrency (``str``, *optional*):
            Cryptocurrency used to pay for the gift.

        cryptocurrency_amount (``int``, *optional*):
            The paid amount, in the smallest units of the cryptocurrency.

        month_count (``int``):
            Number of months the Telegram Premium subscription will be active.

        sticker (:obj:`~pyrogram.types.Sticker`):
            A sticker to be shown in the message.

        caption (``str``, *optional*):
            Message added to the gifted Telegram Premium by the sender.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            Entities of the text message.
    """
    def __init__(
        self,
        *,
        gifter: "types.User" = None,
        receiver: "types.User",
        currency: str = None,
        amount: int = None,
        cryptocurrency: str = None,
        cryptocurrency_amount: int = None,
        month_count: int = None,
        sticker: "types.Sticker" = None,
        caption: str = None,
        caption_entities: list["types.MessageEntity"] = None
    ):
        super().__init__()

        self.gifter = gifter
        self.receiver = receiver
        self.currency = currency
        self.amount = amount
        self.cryptocurrency = cryptocurrency
        self.cryptocurrency_amount = cryptocurrency_amount
        self.month_count = month_count
        self.sticker = sticker
        self.caption = caption
        self.caption_entities = caption_entities

    @staticmethod
    async def _parse(
        client,
        action: "raw.types.MessageActionGiftPremium",
        gifter: "raw.base.User" = None,
        receiver: "raw.base.User" = None,
    ) -> "GiftedPremium":
        raw_stickers = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetPremiumGifts(),
                hash=0
            )
        )

        caption, caption_entities = (utils.parse_text_with_entities(client, getattr(action, "message", None), users)).values()

        return GiftedPremium(
            gifter=types.User._parse(client, gifter),
            receiver=types.User._parse(client, receiver),
            currency=action.currency,
            amount=action.amount,
            cryptocurrency=getattr(action, "crypto_currency", None),
            cryptocurrency_amount=getattr(action, "crypto_amount", None),
            month_count=action.months,
            sticker=random.choice(
                types.List(
                    await types.Sticker._parse(
                        client,
                        doc,
                        {
                            type(i): i for i in doc.attributes
                        }
                    ) for doc in raw_stickers.documents
                )
            ),
            caption=caption,
            caption_entities=caption_entities
        )
