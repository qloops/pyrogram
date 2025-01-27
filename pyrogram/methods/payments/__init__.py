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

from .apply_gift_code import ApplyGiftCode
from .check_gift_code import CheckGiftCode
from .convert_gift import ConvertGift
from .get_payment_form import GetPaymentForm
from .get_stars_balance import GetStarsBalance
from .get_upgraded_gift import GetUpgradedGift
from .get_available_gifts import GetAvailableGifts
from .get_chat_gifts_count import GetChatGiftsCount
from .get_chat_gifts import GetChatGifts
from .hide_gift import HideGift
from .send_payment_form import SendPaymentForm
from .send_gift import SendGift
from .show_gift import ShowGift
from .transfer_gift import TransferGift
from .upgrade_gift import UpgradeGift

class Payments(
    ApplyGiftCode,
    CheckGiftCode,
    ConvertGift,
    GetPaymentForm,
    GetStarsBalance,
    GetUpgradedGift,
    GetAvailableGifts,
    GetChatGiftsCount,
    GetChatGifts,
    HideGift,
    SendPaymentForm,
    SendGift,
    ShowGift,
    TransferGift,
    UpgradeGift
):
    pass
