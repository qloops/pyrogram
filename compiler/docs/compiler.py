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

import ast
import os
import re
import shutil
from dataclasses import dataclass
from typing import Literal

HOME = "compiler/docs"
DESTINATION = "docs/source/telegram"
PYROGRAM_API_DEST = "docs/source/api"

FUNCTIONS_PATH = "pyrogram/raw/functions"
TYPES_PATH = "pyrogram/raw/types"
BASE_PATH = "pyrogram/raw/base"

FUNCTIONS_BASE = "functions"
TYPES_BASE = "types"
BASE_BASE = "base"


def snek(s: str):
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _extract_union_name(node: ast.AST) -> str | None:
    """Extract the name of a variable that is assigned a Union type.

    :param node: The AST node to extract the variable name from.
    :return: The variable name if it is assigned a Union type, otherwise None.

    >>> import ast
    >>> parsed_ast = ast.parse("User = Union[raw.types.UserEmpty]")
    >>> _extract_union_name(parsed_ast.body[0])
    'User'
    """

    # Check if the assigned value is a Union type
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
        if isinstance(node.value.value, ast.Name) and node.value.value.id == "Union":
            # Extract variable name
            if isinstance(node.targets[0], ast.Name):
                return node.targets[0].id  # Variable name


def _extract_class_name(node: ast.AST) -> str | None:
    """Extract the name of a class.

    :param node: The AST node to extract the class name from.
    :return: The class name if it is a class, otherwise None.

    >>> import ast
    >>> parsed_ast = ast.parse("class User: pass")
    >>> _extract_class_name(parsed_ast.body[0])
    'User'
    """

    if isinstance(node, ast.ClassDef):
        return node.name  # Class name


NodeType = Literal["class", "union"]


@dataclass
class NodeInfo:
    name: str
    type: NodeType


def parse_node_info(node: ast.AST) -> NodeInfo | None:
    """Parse an AST node and extract the class or variable name."""
    class_name = _extract_class_name(node)
    if class_name:
        return NodeInfo(name=class_name, type="class")

    union_name = _extract_union_name(node)
    if union_name:
        return NodeInfo(name=union_name, type="union")

    return None


def generate(source_path, base):
    all_entities = {}

    def build(path, level=0):
        last = path.split("/")[-1]

        for i in os.listdir(path):
            try:
                if not i.startswith("__"):
                    build("/".join([path, i]), level=level + 1)
            except NotADirectoryError:
                with open(path + "/" + i, encoding="utf-8") as f:
                    p = ast.parse(f.read())

                for node in ast.walk(p):
                    node_info = parse_node_info(node)
                    if node_info:
                        break
                else:
                    continue

                full_path = os.path.basename(path) + "/" + snek(node_info.name).replace("_", "-") + ".rst"

                if level:
                    full_path = base + "/" + full_path

                namespace = path.split("/")[-1]
                if namespace in ["base", "types", "functions"]:
                    namespace = ""

                full_name = f"{(namespace + '.') if namespace else ''}{node_info.name}"

                os.makedirs(os.path.dirname(DESTINATION + "/" + full_path), exist_ok=True)

                with open(DESTINATION + "/" + full_path, "w", encoding="utf-8") as f:
                    title_markup = "=" * len(full_name)
                    full_class_path = "pyrogram.raw.{}".format(
                        ".".join(full_path.split("/")[:-1]) + "." + node_info.name
                    )

                    if node_info.type == "class":
                        directive_type = "autoclass"
                        directive_suffix = "()"
                        directive_option = "members"
                    elif node_info.type == "union":
                        directive_type = "autodata"
                        directive_suffix = ""
                        directive_option = "annotation"
                    else:
                        raise ValueError(f"Unknown node type: `{node_info.type}`")

                    f.write(
                        page_template.format(
                            title=full_name,
                            title_markup=title_markup,
                            directive_type=directive_type,
                            full_class_path=full_class_path,
                            directive_suffix=directive_suffix,
                            directive_option=directive_option,
                        )
                    )

                if last not in all_entities:
                    all_entities[last] = []

                all_entities[last].append(node_info.name)

    build(source_path)

    for k, v in sorted(all_entities.items()):
        v = sorted(v)
        entities = []

        for i in v:
            entities.append(f'{i} <{snek(i).replace("_", "-")}>')

        if k != base:
            inner_path = base + "/" + k + "/index" + ".rst"
            module = "pyrogram.raw.{}.{}".format(base, k)
        else:
            for i in sorted(list(all_entities), reverse=True):
                if i != base:
                    entities.insert(0, "{0}/index".format(i))

            inner_path = base + "/index" + ".rst"
            module = "pyrogram.raw.{}".format(base)

        with open(DESTINATION + "/" + inner_path, "w", encoding="utf-8") as f:
            if k == base:
                f.write(":tocdepth: 1\n\n")
                k = "Raw " + k

            f.write(
                toctree.format(
                    title=k.title(),
                    title_markup="=" * len(k),
                    module=module,
                    entities="\n    ".join(entities)
                )
            )

            f.write("\n")


def pyrogram_api():
    def get_title_list(s: str) -> list:
        return [i.strip() for i in [j.strip() for j in s.split("\n") if j] if i]

    # Methods

    categories = dict(
        utilities="""
        Utilities
            start
            stop
            run
            restart
            add_handler
            remove_handler
            stop_transmission
            export_session_string
            set_parse_mode
        """,
        messages="""
        Messages
            send_message
            forward_media_group
            forward_messages
            copy_message
            copy_media_group
            send_photo
            send_audio
            send_document
            send_sticker
            send_video
            send_animation
            send_voice
            send_video_note
            send_media_group
            send_location
            send_venue
            send_contact
            send_cached_media
            send_reaction
            edit_message_text
            edit_message_caption
            edit_message_media
            edit_message_reply_markup
            edit_inline_text
            edit_inline_caption
            edit_inline_media
            edit_inline_reply_markup
            send_chat_action
            delete_messages
            get_available_effects
            get_messages
            get_scheduled_messages
            get_stickers
            get_media_group
            get_chat_history
            get_chat_history_count
            read_chat_history
            send_poll
            view_messages
            vote_poll
            stop_poll
            retract_vote
            send_dice
            search_messages
            search_messages_count
            search_posts
            search_posts_count
            search_global
            search_global_count
            download_media
            stream_media
            get_discussion_message
            get_discussion_replies
            get_discussion_replies_count
            get_custom_emoji_stickers
            send_web_page
            start_bot
            update_color
            delete_chat_history
            send_paid_media
            send_paid_reaction
            add_to_gifs
        """,
        chats="""
        Chats
            join_chat
            leave_chat
            ban_chat_member
            unban_chat_member
            restrict_chat_member
            promote_chat_member
            set_administrator_title
            set_chat_photo
            delete_chat_photo
            set_chat_title
            set_chat_description
            set_chat_permissions
            pin_chat_message
            unpin_chat_message
            pin_forum_topic
            unpin_forum_topic
            unpin_all_chat_messages
            get_chat
            get_chat_member
            get_chat_members
            get_chat_members_count
            get_dialogs
            get_dialogs_count
            set_chat_username
            archive_chats
            unarchive_chats
            add_chat_members
            create_channel
            create_group
            create_supergroup
            delete_channel
            delete_supergroup
            delete_user_history
            set_slow_mode
            mark_chat_unread
            get_chat_event_log
            get_chat_online_count
            get_send_as_chats
            set_send_as_chat
            set_chat_protected_content
            close_forum_topic
            create_forum_topic
            delete_forum_topic
            edit_forum_topic
            get_forum_topics
            get_forum_topics_by_id
            update_color
            update_chat_notifications
            toggle_forum_topics
            delete_folder
            export_folder_link
            get_folders
            update_folder
            get_similar_channels
            join_folder
            leave_folder
            toggle_join_to_send
            toggle_folder_tags
            set_chat_ttl
            get_personal_channels
            get_chat_settings
            transfer_chat_ownership
        """,
        users="""
        Users
            get_me
            get_users
            get_chat_photos
            get_chat_photos_count
            set_profile_photo
            set_personal_channel
            delete_profile_photos
            set_username
            update_profile
            block_user
            unblock_user
            get_common_chats
            get_default_emoji_statuses
            set_emoji_status
            update_status
            check_username
            update_birthday
        """,
        invite_links="""
        Invite Links
            get_chat_invite_link
            export_chat_invite_link
            create_chat_invite_link
            edit_chat_invite_link
            revoke_chat_invite_link
            delete_chat_invite_link
            get_chat_invite_link_joiners
            get_chat_invite_link_joiners_count
            get_chat_admin_invite_links
            get_chat_admin_invite_links_count
            get_chat_admins_with_invite_links
            get_chat_join_requests
            delete_chat_admin_invite_links
            approve_chat_join_request
            approve_all_chat_join_requests
            decline_chat_join_request
            decline_all_chat_join_requests
        """,
        contacts="""
        Contacts
            add_contact
            delete_contacts
            import_contacts
            get_contacts
            get_contacts_count
            search_contacts
        """,
        payments="""
        Payments
            apply_gift_code
            check_gift_code
            convert_gift
            get_payment_form
            get_available_gifts
            get_upgraded_gift
            get_chat_gifts_count
            get_chat_gifts
            hide_gift
            send_payment_form
            send_gift
            show_gift
            transfer_gift
            upgrade_gift
            get_stars_balance
        """,
        phone="""
        Phone
            get_call_members
        """,
        password="""
        Password
            enable_cloud_password
            change_cloud_password
            remove_cloud_password
        """,
        bots="""
        Bots
            get_inline_bot_results
            send_inline_bot_result
            send_invoice
            answer_callback_query
            answer_inline_query
            request_callback_answer
            send_game
            set_game_score
            get_game_high_scores
            set_bot_commands
            get_bot_commands
            delete_bot_commands
            set_bot_default_privileges
            get_bot_default_privileges
            set_chat_menu_button
            get_chat_menu_button
            answer_web_app_query
            answer_pre_checkout_query
            answer_shipping_query
            create_invoice_link
            refund_star_payment
            set_bot_info_description
            get_bot_info_description
            set_bot_info_short_description
            get_bot_info_short_description
            set_bot_name
            get_bot_name
            get_owned_bots
        """,
        business="""
        Business
            get_business_connection
        """,
        authorization="""
        Authorization
            connect
            disconnect
            initialize
            terminate
            send_code
            resend_code
            sign_in
            sign_in_bot
            sign_up
            get_password_hint
            check_password
            send_recovery_code
            recover_password
            accept_terms_of_service
            log_out
            get_active_sessions
            reset_session
            reset_sessions
        """,
        advanced="""
        Advanced
            invoke
            resolve_peer
            save_file
        """,
        stories="""
        Stories
            can_post_stories
            copy_story
            delete_stories
            edit_story_caption
            edit_story_media
            edit_story_privacy
            forward_story
            get_all_stories
            get_chat_stories
            get_pinned_stories
            get_archived_stories
            get_stories
            hide_chat_stories
            show_chat_stories
            view_stories
            pin_chat_stories
            unpin_chat_stories
            read_chat_stories
            send_story
            enable_stealth_mode
            get_story_views
        """,
        premium="""
        Premium
            apply_boost
            get_boosts
            get_boosts_status
        """,
        account="""
        Account
            get_account_ttl
            set_account_ttl
            set_privacy
            get_privacy
            set_global_privacy_settings
            get_global_privacy_settings
        """
    )

    root = PYROGRAM_API_DEST + "/methods"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/methods.rst") as f:
        template = f.read()

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *methods = get_title_list(v)
            fmt_keys.update({k: "\n    ".join("{0} <{0}>".format(m) for m in methods)})

            for method in methods:
                with open(root + "/{}.rst".format(method), "w") as f2:
                    title = "{}()".format(method)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. automethod:: pyrogram.Client.{}()".format(method))

            functions = ["idle", "compose"]

            for func in functions:
                with open(root + "/{}.rst".format(func), "w") as f2:
                    title = "{}()".format(func)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. autofunction:: pyrogram.{}()".format(func))

        f.write(template.format(**fmt_keys))

    # Types

    categories = dict(
        users_chats="""
        Users & Chats
            Birthday
            BusinessConnection
            BusinessIntro
            BusinessRecipients
            BusinessWeeklyOpen
            BusinessWorkingHours
            User
            Username
            Chat
            ChatPhoto
            ChatMember
            ChatPermissions
            ChatPrivileges
            ChatInviteLink
            ChatAdminWithInviteLinks
            ChatEvent
            ChatEventFilter
            ChatMemberUpdated
            ChatJoinRequest
            ChatJoiner
            Dialog
            Restriction
            EmojiStatus
            Folder
            GroupCallMember
            ChatColor
            FoundContacts
            PrivacyRule
            StoriesStealthMode
            BotVerification
            ChatSettings
            GlobalPrivacySettings
        """,
        messages_media="""
        Messages & Media
            BusinessMessage
            Message
            MessageEntity
            Photo
            Thumbnail
            StrippedThumbnail
            Audio
            AvailableEffect
            Document
            ForumTopic
            ForumTopicClosed
            ForumTopicCreated
            ForumTopicEdited
            ForumTopicReopened
            Animation
            Video
            Voice
            VideoNote
            Contact
            Location
            MediaArea
            Venue
            Sticker
            Game
            WebPage
            Poll
            PollOption
            Dice
            Reaction
            RefundedPayment
            Gift
            VideoChatScheduled
            VideoChatStarted
            VideoChatEnded
            VideoChatMembersInvited
            PhoneCallStarted
            PhoneCallEnded
            WebAppData
            MessageReactions
            ChatReactions
            Story
            MyBoost
            BoostsStatus
            Giveaway
            GiveawayCreated
            GiveawayCompleted
            GiveawayWinners
            Invoice
            GiftCode
            CheckedGiftCode
            SuccessfulPayment
            PaidMediaInfo
            PaidMediaPreview
            PaymentForm
            ChatBoost
            ContactRegistered
            ScreenshotTaken
            WriteAccessAllowed
            GiftAttribute
            StoryView
        """,
        bot_keyboards="""
        Bot keyboards
            ReplyKeyboardMarkup
            KeyboardButton
            ReplyKeyboardRemove
            InlineKeyboardMarkup
            InlineKeyboardButton
            LoginUrl
            ForceReply
            CallbackQuery
            GameHighScore
            CallbackGame
            WebAppInfo
            MenuButton
            MenuButtonCommands
            MenuButtonWebApp
            MenuButtonDefault
            SentWebAppMessage
            RequestChannelInfo
            RequestChatInfo
            RequestUserInfo
            RequestPollInfo
            OrderInfo
            PreCheckoutQuery
            ShippingAddress
            ShippingQuery
            MessageReactionUpdated
            MessageReactionCountUpdated
            ChatBoostUpdated
            ShippingOption
            PurchasedPaidMedia
        """,
        bot_commands="""
        Bot commands
            BotCommand
            BotCommandScope
            BotCommandScopeDefault
            BotCommandScopeAllPrivateChats
            BotCommandScopeAllGroupChats
            BotCommandScopeAllChatAdministrators
            BotCommandScopeChat
            BotCommandScopeChatAdministrators
            BotCommandScopeChatMember
        """,
        input_media="""
        Input Media
            InputMedia
            InputMediaPhoto
            InputMediaVideo
            InputMediaAudio
            InputMediaAnimation
            InputMediaDocument
            InputPhoneContact
        """,
        inline_mode="""
        Inline Mode
            InlineQuery
            InlineQueryResult
            InlineQueryResultCachedAudio
            InlineQueryResultCachedDocument
            InlineQueryResultCachedAnimation
            InlineQueryResultCachedPhoto
            InlineQueryResultCachedSticker
            InlineQueryResultCachedVideo
            InlineQueryResultCachedVoice
            InlineQueryResultArticle
            InlineQueryResultAudio
            InlineQueryResultContact
            InlineQueryResultDocument
            InlineQueryResultAnimation
            InlineQueryResultLocation
            InlineQueryResultPhoto
            InlineQueryResultVenue
            InlineQueryResultVideo
            InlineQueryResultVoice
            ChosenInlineResult
        """,
        input_message_content="""
        InputMessageContent
            InputMessageContent
            InputTextMessageContent
        """,
        authorization="""
        Authorization
            ActiveSession
            ActiveSessions
            SentCode
            TermsOfService
        """,
        input_privacy_rule="""
        InputPrivacyRule
            InputPrivacyRule
            InputPrivacyRuleAllowAll
            InputPrivacyRuleAllowBots
            InputPrivacyRuleAllowChats
            InputPrivacyRuleAllowCloseFriends
            InputPrivacyRuleAllowContacts
            InputPrivacyRuleAllowPremium
            InputPrivacyRuleAllowUsers
            InputPrivacyRuleDisallowAll
            InputPrivacyRuleDisallowBots
            InputPrivacyRuleDisallowChats
            InputPrivacyRuleDisallowContacts
            InputPrivacyRuleDisallowUsers
        """
    )

    root = PYROGRAM_API_DEST + "/types"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/types.rst") as f:
        template = f.read()

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *types = get_title_list(v)

            fmt_keys.update({k: "\n    ".join(types)})

            # noinspection PyShadowingBuiltins
            for type in types:
                with open(root + "/{}.rst".format(type), "w") as f2:
                    title = "{}".format(type)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. autoclass:: pyrogram.types.{}()\n".format(type))

        f.write(template.format(**fmt_keys))

    # Bound Methods

    categories = dict(
        message="""
        Message
            Message.click
            Message.delete
            Message.download
            Message.forward
            Message.copy
            Message.copy_media_group
            Message.pin
            Message.unpin
            Message.edit
            Message.edit_text
            Message.edit_caption
            Message.edit_media
            Message.edit_reply_markup
            Message.reply
            Message.reply_text
            Message.reply_animation
            Message.reply_audio
            Message.reply_cached_media
            Message.reply_chat_action
            Message.reply_contact
            Message.reply_document
            Message.reply_game
            Message.reply_inline_bot_result
            Message.reply_location
            Message.reply_media_group
            Message.reply_photo
            Message.reply_poll
            Message.reply_sticker
            Message.reply_venue
            Message.reply_video
            Message.reply_video_note
            Message.reply_voice
            Message.reply_web_page
            Message.get_media_group
            Message.react
            Message.read
            Message.view
            Message.pay
        """,
        chat="""
        Chat
            Chat.archive
            Chat.unarchive
            Chat.set_title
            Chat.set_description
            Chat.set_photo
            Chat.set_ttl
            Chat.ban_member
            Chat.unban_member
            Chat.restrict_member
            Chat.promote_member
            Chat.join
            Chat.leave
            Chat.export_invite_link
            Chat.get_member
            Chat.get_members
            Chat.add_members
            Chat.mark_unread
            Chat.set_protected_content
            Chat.unpin_all_messages
            Chat.mute
            Chat.unmute
        """,
        user="""
        User
            User.archive
            User.unarchive
            User.block
            User.unblock
            User.get_common_chats
        """,
        callback_query="""
        Callback Query
            CallbackQuery.answer
            CallbackQuery.edit_message_text
            CallbackQuery.edit_message_caption
            CallbackQuery.edit_message_media
            CallbackQuery.edit_message_reply_markup
        """,
        inline_query="""
        InlineQuery
            InlineQuery.answer
        """,
        pre_checkout_query="""
        PreCheckoutQuery
            PreCheckoutQuery.answer
        """,
        shipping_query="""
        ShippingQuery
            ShippingQuery.answer
        """,
        chat_join_request="""
        ChatJoinRequest
            ChatJoinRequest.approve
            ChatJoinRequest.decline
        """,
        story="""
        Story
            Story.reply
            Story.reply_text
            Story.reply_animation
            Story.reply_audio
            Story.reply_cached_media
            Story.reply_media_group
            Story.reply_photo
            Story.reply_sticker
            Story.reply_video
            Story.reply_video_note
            Story.reply_voice
            Story.copy
            Story.delete
            Story.edit_media
            Story.edit_caption
            Story.edit_privacy
            Story.react
            Story.forward
            Story.download
            Story.read
            Story.view
        """,
        folder="""
        Folder
            Folder.delete
            Folder.update
            Folder.include_chat
            Folder.exclude_chat
            Folder.update_color
            Folder.pin_chat
            Folder.remove_chat
            Folder.export_link
        """,
        active_session="""
        ActiveSession
            ActiveSession.reset
        """,
        gift="""
        Gift
            Gift.show
            Gift.hide
            Gift.convert
            Gift.upgrade
            Gift.transfer
            Gift.wear
        """,
        animation="""
        Animation
            Animation.add_to_gifs
        """
    )

    root = PYROGRAM_API_DEST + "/bound-methods"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/bound-methods.rst") as f:
        template = f.read()

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *bound_methods = get_title_list(v)

            fmt_keys.update({"{}_hlist".format(k): "\n    ".join("- :meth:`~{}`".format(bm) for bm in bound_methods)})

            fmt_keys.update(
                {"{}_toctree".format(k): "\n    ".join("{} <{}>".format(bm.split(".")[1], bm) for bm in bound_methods)})

            # noinspection PyShadowingBuiltins
            for bm in bound_methods:
                with open(root + "/{}.rst".format(bm), "w") as f2:
                    title = "{}()".format(bm)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. automethod:: pyrogram.types.{}()".format(bm))

        f.write(template.format(**fmt_keys))


    # Enumerations

    categories = dict(
        enums="""
        Enumerations
            BusinessSchedule
            ChatAction
            ChatEventAction
            ChatJoinType
            ChatMemberStatus
            ChatMembersFilter
            ChatType
            ClientPlatform
            FolderColor
            MessageEntityType
            MessageMediaType
            MessageServiceType
            MessagesFilter
            NextCodeType
            ParseMode
            PhoneCallDiscardReason
            PollType
            PrivacyKey
            ProfileColor
            ReplyColor
            SentCodeType
            StoriesPrivacyRules
            UserStatus
            GiftAttributeType
            MediaAreaType
            PrivacyRuleType
        """,
    )

    root = PYROGRAM_API_DEST + "/enums"

    shutil.rmtree(root, ignore_errors=True)
    os.mkdir(root)

    with open(HOME + "/template/enums.rst") as f:
        template = f.read()

    with open(root + "/cleanup.html", "w") as f:
        f.write("""<script>
  document
    .querySelectorAll("em.property")
    .forEach((elem, i) => i !== 0 ? elem.remove() : true)

  document
    .querySelectorAll("a.headerlink")
    .forEach((elem, i) => [0, 1].includes(i) ? true : elem.remove())
</script>""")

    with open(root + "/index.rst", "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *enums = get_title_list(v)

            fmt_keys.update({"{}_hlist".format(k): "\n    ".join("{}".format(enum) for enum in enums)})

            fmt_keys.update(
                {"{}_toctree".format(k): "\n    ".join("{}".format(enum) for enum in enums)})

            # noinspection PyShadowingBuiltins
            for enum in enums:
                with open(root + "/{}.rst".format(enum), "w") as f2:
                    title = "{}".format(enum)

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(".. autoclass:: pyrogram.enums.{}()".format(enum))
                    f2.write("\n    :members:\n")

                    f2.write("\n.. raw:: html\n    :file: ./cleanup.html\n")

        f.write(template.format(**fmt_keys))


def start():
    global page_template
    global toctree

    shutil.rmtree(DESTINATION, ignore_errors=True)

    with open(HOME + "/template/page.txt", encoding="utf-8") as f:
        page_template = f.read()

    with open(HOME + "/template/toctree.txt", encoding="utf-8") as f:
        toctree = f.read()

    generate(TYPES_PATH, TYPES_BASE)
    generate(FUNCTIONS_PATH, FUNCTIONS_BASE)
    generate(BASE_PATH, BASE_BASE)
    pyrogram_api()


if "__main__" == __name__:
    FUNCTIONS_PATH = "../../pyrogram/raw/functions"
    TYPES_PATH = "../../pyrogram/raw/types"
    BASE_PATH = "../../pyrogram/raw/base"
    HOME = "."
    DESTINATION = "../../docs/source/telegram"
    PYROGRAM_API_DEST = "../../docs/source/api"

    start()
