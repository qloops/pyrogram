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

import logging
import os
import re
from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.file_id import FileType

log = logging.getLogger(__name__)


class SendMediaGroup:
    # TODO: Add progress parameter
    async def send_media_group(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        media: List[Union[
            "types.InputMediaPhoto",
            "types.InputMediaVideo",
            "types.InputMediaAudio",
            "types.InputMediaDocument"
        ]],
        disable_notification: bool = None,
        message_thread_id: int = None,
        effect_id: int = None,
        reply_parameters: "types.ReplyParameters" = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        show_caption_above_media: bool = None,
        business_connection_id: str = None,
        allow_paid_broadcast: bool = None,
        paid_message_star_count: int = None,

        reply_to_message_id: int = None,
        reply_to_chat_id: Union[int, str] = None,
        reply_to_story_id: int = None,
        quote_text: str = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        quote_entities: List["types.MessageEntity"] = None,
        quote_offset: int = None,
    ) -> List["types.Message"]:
        """Send a group of photos or videos as an album.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            media (List of :obj:`~pyrogram.types.InputMediaPhoto`, :obj:`~pyrogram.types.InputMediaVideo`, :obj:`~pyrogram.types.InputMediaAudio` and :obj:`~pyrogram.types.InputMediaDocument`):
                A list describing photos and videos to be sent, must include 2–10 items.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of the sent messages is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto, InputMediaVideo

                await app.send_media_group(
                    "me",
                    [
                        InputMediaPhoto("photo1.jpg"),
                        InputMediaPhoto("photo2.jpg", caption="photo caption"),
                        InputMediaVideo("video.mp4", caption="video caption")
                    ]
                )
        """
        if any(
            (
                reply_to_message_id is not None,
                reply_to_chat_id is not None,
                reply_to_story_id is not None,
                quote_text is not None,
                parse_mode is not None,
                quote_entities is not None,
                quote_offset is not None,
            )
        ):
            if reply_to_message_id is not None:
                log.warning(
                    "`reply_to_message_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if reply_to_chat_id is not None:
                log.warning(
                    "`reply_to_chat_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if reply_to_story_id is not None:
                log.warning(
                    "`reply_to_story_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_text is not None:
                log.warning(
                    "`quote_text` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if parse_mode is not None:
                log.warning(
                    "`parse_mode` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_entities is not None:
                log.warning(
                    "`quote_entities` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_offset is not None:
                log.warning(
                    "`quote_offset` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id,
                chat_id=reply_to_chat_id,
                story_id=reply_to_story_id,
                quote=quote_text,
                quote_parse_mode=parse_mode,
                quote_entities=quote_entities,
                quote_position=quote_offset
            )

        multi_media = []

        for i in media:
            if isinstance(i, types.InputMediaPhoto):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedPhoto(
                                    file=await self.save_file(i.media),
                                    spoiler=i.has_spoiler
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaPhoto(
                            id=raw.types.InputPhoto(
                                id=media.photo.id,
                                access_hash=media.photo.access_hash,
                                file_reference=media.photo.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaPhotoExternal(
                                    url=i.media,
                                    spoiler=i.has_spoiler
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaPhoto(
                            id=raw.types.InputPhoto(
                                id=media.photo.id,
                                access_hash=media.photo.access_hash,
                                file_reference=media.photo.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.PHOTO, has_spoiler=i.has_spoiler)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedPhoto(
                                file=await self.save_file(i.media),
                                spoiler=i.has_spoiler
                            ),
                            business_connection_id=business_connection_id
                        )
                    )

                    media = raw.types.InputMediaPhoto(
                        id=raw.types.InputPhoto(
                            id=media.photo.id,
                            access_hash=media.photo.access_hash,
                            file_reference=media.photo.file_reference
                        ),
                        spoiler=i.has_spoiler
                    )
            elif isinstance(i, types.InputMediaVideo):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedDocument(
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    spoiler=i.has_spoiler,
                                    mime_type=self.guess_mime_type(i.media) or "video/mp4",
                                    nosound_video=True,
                                    attributes=[
                                        raw.types.DocumentAttributeVideo(
                                            supports_streaming=i.supports_streaming or None,
                                            duration=i.duration,
                                            w=i.width,
                                            h=i.height
                                        ),
                                        raw.types.DocumentAttributeFilename(file_name=i.file_name or os.path.basename(i.media))
                                    ]
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media,
                                    spoiler=i.has_spoiler
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.VIDEO, has_spoiler=i.has_spoiler)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedDocument(
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                spoiler=i.has_spoiler,
                                mime_type=self.guess_mime_type(getattr(i.media, "name", "video.mp4")) or "video/mp4",
                                nosound_video=True,
                                attributes=[
                                    raw.types.DocumentAttributeVideo(
                                        supports_streaming=i.supports_streaming or None,
                                        duration=i.duration,
                                        w=i.width,
                                        h=i.height
                                    ),
                                    raw.types.DocumentAttributeFilename(file_name=i.file_name or getattr(i.media, "name", "video.mp4"))
                                ]
                            ),
                            business_connection_id=business_connection_id
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        ),
                        spoiler=i.has_spoiler
                    )
            elif isinstance(i, types.InputMediaAudio):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedDocument(
                                    mime_type=self.guess_mime_type(i.media) or "audio/mpeg",
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    attributes=[
                                        raw.types.DocumentAttributeAudio(
                                            duration=i.duration,
                                            performer=i.performer,
                                            title=i.title
                                        ),
                                        raw.types.DocumentAttributeFilename(file_name=i.file_name or os.path.basename(i.media))
                                    ]
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.AUDIO)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedDocument(
                                mime_type=self.guess_mime_type(getattr(i.media, "name", "audio.mp3")) or "audio/mpeg",
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                attributes=[
                                    raw.types.DocumentAttributeAudio(
                                        duration=i.duration,
                                        performer=i.performer,
                                        title=i.title
                                    ),
                                    raw.types.DocumentAttributeFilename(file_name=i.file_name or getattr(i.media, "name", "audio.mp3"))
                                ]
                            ),
                            business_connection_id=business_connection_id
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        )
                    )
            elif isinstance(i, types.InputMediaDocument):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaUploadedDocument(
                                    mime_type=self.guess_mime_type(i.media) or "application/zip",
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    attributes=[
                                        raw.types.DocumentAttributeFilename(file_name=i.file_name or os.path.basename(i.media))
                                    ]
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media
                                ),
                                business_connection_id=business_connection_id
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference
                            )
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.DOCUMENT)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=await self.resolve_peer(chat_id),
                            media=raw.types.InputMediaUploadedDocument(
                                mime_type=self.guess_mime_type(
                                    getattr(i.media, "name", "file.zip")
                                ) or "application/zip",
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                attributes=[
                                    raw.types.DocumentAttributeFilename(file_name=i.file_name or getattr(i.media, "name", "file.zip"))
                                ]
                            ),
                            business_connection_id=business_connection_id
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        )
                    )
            else:
                raise ValueError(f"{i.__class__.__name__} is not a supported type for send_media_group")

            multi_media.append(
                raw.types.InputSingleMedia(
                    media=media,
                    random_id=self.rnd_id(),
                    **await utils.parse_text_entities(self, i.caption, i.parse_mode, i.caption_entities)
                )
            )

        peer = await self.resolve_peer(chat_id)
        r = await self.invoke(
            raw.functions.messages.SendMultiMedia(
                peer=peer,
                multi_media=multi_media,
                silent=disable_notification or None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id
                ),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                invert_media=show_caption_above_media,
                allow_paid_floodskip=allow_paid_broadcast,
                allow_paid_stars=paid_message_star_count,
                effect=effect_id,
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id
        )

        conn_id = None

        for u in r.updates:
            if getattr(u, "connection_id", None):
                conn_id = u.connection_id
                break


        return await utils.parse_messages(
            self,
            raw.types.messages.Messages(
                messages=[m.message for m in filter(
                    lambda u: isinstance(u, (raw.types.UpdateNewMessage,
                                             raw.types.UpdateNewChannelMessage,
                                             raw.types.UpdateNewScheduledMessage,
                                             raw.types.UpdateBotNewBusinessMessage)),
                    r.updates
                )],
                users=r.users,
                chats=r.chats
            ),
            business_connection_id=conn_id
        )
