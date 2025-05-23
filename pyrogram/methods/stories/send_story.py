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

import os
from typing import BinaryIO, Callable, List, Union

import pyrogram
from pyrogram import StopTransmission, enums, raw, types, utils
from pyrogram.errors import FilePartMissing


class SendStory:
    async def send_story(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        media: Union[str, BinaryIO],
        caption: str = None,
        period: int = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: Union[str, BinaryIO] = None,
        supports_streaming: bool = True,
        file_name: str = None,
        privacy: "enums.StoriesPrivacyRules" = None,
        allowed_users: List[Union[int, str]] = None,
        disallowed_users: List[Union[int, str]] = None,
        pinned: bool = None,
        protect_content: bool = None,
        parse_mode: "enums.ParseMode" = None,
        caption_entities: List["types.MessageEntity"] = None,
        progress: Callable = None,
        progress_args: tuple = (),
        media_areas: List["types.MediaArea"] = None
    ) -> "types.Story":
        """Post new story.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            media (``str`` | ``BinaryIO``):
                Video or photo to send.
                Pass a file_id as string to send a animation that exists on the Telegram servers,
                pass a file path as string to upload a new animation that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            caption (``str``, *optional*):
                Story caption, 0-1024 characters.

            period (``int``, *optional*):
                Period after which the story is moved to archive (and to the profile if pinned is set), in seconds.
                Must be one of ``6 * 3600``, ``12 * 3600``, ``86400``, or ``2 * 86400`` for Telegram Premium users,
                and 86400 otherwise.

            duration (``int``, *optional*):
                Duration of sent video in seconds.

            width (``int``, *optional*):
                Video width.

            height (``int``, *optional*):
                Video height.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the video sent.
                The thumbnail should be in JPEG format and less than 200 KB in size.
                A thumbnail's width and height should not exceed 320 pixels.
                Thumbnails can't be reused and can be only uploaded as a new file.

            supports_streaming (``bool``, *optional*):
                True, if the uploaded video is suitable for streaming.
                Defaults to True.

            file_name (``str``, *optional*):
                File name of the story sent.

            privacy (:obj:`~pyrogram.enums.StoriesPrivacyRules`, *optional*):
                Story privacy.
                Defaults to :obj:`~pyrogram.enums.StoriesPrivacyRules.PUBLIC`

            allowed_users (List of ``int``, *optional*):
                List of user_id or chat_id of chat users who are allowed to view stories.
                Note: chat_id available only with :obj:`~pyrogram.enums.StoriesPrivacyRules.SELECTED_USERS`.
                Works with :obj:`~pyrogram.enums.StoriesPrivacyRules.CLOSE_FRIENDS`
                and :obj:`~pyrogram.enums.StoriesPrivacyRules.SELECTED_USERS` only

            disallowed_users (List of ``int``, *optional*):
                List of user_id whos disallow to view the stories.
                Note: Works with :obj:`~pyrogram.enums.StoriesPrivacyRules.PUBLIC`
                and :obj:`~pyrogram.enums.StoriesPrivacyRules.CONTACTS` only

            pinned (``bool``, *optional*):
                If True, the story will be pinned.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent story from forwarding and saving.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

            media_areas (List of :obj:`~pyrogram.types.MediaArea`, *optional*):
                List of media areas to add to the story.

        Returns:
            :obj:`~pyrogram.types.Story` a single story is returned.

        Example:
            .. code-block:: python

                # Post story to your profile
                await app.send_story("me", "story.png", caption='My new story!')

                # Post story to channel
                await app.send_story(123456, "story.png", caption='My new story!')

        Raises:
            ValueError: In case of invalid arguments.
        """
        # TODO: media_areas

        message, entities = (await utils.parse_text_entities(self, caption, parse_mode, caption_entities)).values()

        try:
            if isinstance(media, str):
                if os.path.isfile(media):
                    thumb = await self.save_file(thumb)
                    file = await self.save_file(media, progress=progress, progress_args=progress_args)
                    mime_type = self.guess_mime_type(file.name)
                    if mime_type == "video/mp4":
                        media = raw.types.InputMediaUploadedDocument(
                            mime_type=mime_type,
                            file=file,
                            thumb=thumb,
                            attributes=[
                                raw.types.DocumentAttributeVideo(
                                    duration=duration,
                                    w=width,
                                    h=height,
                                ),
                                raw.types.DocumentAttributeFilename(file_name=file_name or os.path.basename(media))
                            ]
                        )
                    else:
                        media = raw.types.InputMediaUploadedPhoto(
                            file=file,
                        )
                else:
                    media = utils.get_input_media_from_file_id(media)
            else:
                thumb = await self.save_file(thumb)
                file = await self.save_file(media, progress=progress, progress_args=progress_args)
                mime_type = self.guess_mime_type(file.name)
                if mime_type == "video/mp4":
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=mime_type,
                        file=file,
                        thumb=thumb,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                supports_streaming=supports_streaming or None,
                                duration=duration,
                                w=width,
                                h=height,
                            ),
                            raw.types.DocumentAttributeFilename(file_name=file_name or media.name)
                        ]
                    )
                else:
                    media = raw.types.InputMediaUploadedPhoto(
                        file=file,
                    )

            privacy_rules = []

            if privacy == enums.StoriesPrivacyRules.PUBLIC:
                privacy_rules.append(raw.types.InputPrivacyValueAllowAll())
                if disallowed_users:
                    users = [await self.resolve_peer(user_id) for user_id in disallowed_users]
                    privacy_rules.append(raw.types.InputPrivacyValueDisallowUsers(users=users))
            elif privacy == enums.StoriesPrivacyRules.CONTACTS:
                privacy_rules.append(raw.types.InputPrivacyValueAllowContacts())
                if disallowed_users:
                    users = [await self.resolve_peer(user_id) for user_id in disallowed_users]
                    privacy_rules.append(raw.types.InputPrivacyValueDisallowUsers(users=users))
            elif privacy == enums.StoriesPrivacyRules.CLOSE_FRIENDS:
                privacy_rules.append(raw.types.InputPrivacyValueAllowCloseFriends())
                if allowed_users:
                    users = [await self.resolve_peer(user_id) for user_id in allowed_users]
                    privacy_rules.append(raw.types.InputPrivacyValueAllowUsers(users=users))
                else:
                    privacy_rules.append(raw.types.InputPrivacyValueAllowUsers(users=[raw.types.InputPeerEmpty()]))
            elif privacy == enums.StoriesPrivacyRules.SELECTED_USERS:
                _allowed_users = []
                _allowed_chats = []

                if allowed_users:
                    for user in allowed_users:
                        peer = await self.resolve_peer(user)
                        if isinstance(peer, raw.types.InputPeerUser):
                            _allowed_users.append(peer)
                        elif isinstance(peer, (raw.types.InputPeerChat, raw.types.InputPeerChannel)):
                            _allowed_chats.append(peer)
                else:
                    privacy_rules.append(raw.types.InputPrivacyValueAllowUsers(users=[raw.types.InputPeerEmpty()]))

                if _allowed_users:
                    privacy_rules.append(raw.types.InputPrivacyValueAllowUsers(users=_allowed_users))
                if _allowed_chats:
                    privacy_rules.append(raw.types.InputPrivacyValueAllowChatParticipants(chats=_allowed_chats))
            else:
                privacy_rules.append(raw.types.InputPrivacyValueAllowAll())

            while True:
                try:
                    r = await self.invoke(
                        raw.functions.stories.SendStory(
                            peer=await self.resolve_peer(chat_id),
                            media=media,
                            privacy_rules=privacy_rules,
                            random_id=self.rnd_id(),
                            pinned=pinned,
                            noforwards=protect_content,
                            media_areas=[await area.write(self) for area in (media_areas or [])] or None,
                            caption=message,
                            entities=entities,
                            period=period,
                        )
                    )
                except FilePartMissing as e:
                    await self.save_file(media, file_id=file.id, file_part=e.value)
                else:
                    for i in r.updates:
                        if isinstance(i, raw.types.UpdateStory):
                            return await types.Story._parse(
                                self,
                                i.story,
                                i.peer,
                                {i.id: i for i in r.users},
                                {i.id: i for i in r.chats}
                            )
        except StopTransmission:
            return None
