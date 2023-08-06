"""This module is a collection of classes and methods to perform the actual
posting of content to Mastodon."""
# pylint: disable=too-few-public-methods
# With two private methods it is still nice to have these in their own module
import logging
import os
import sys
from typing import Any
from typing import Dict
from typing import List
from typing import TypeVar

import magic
from mastodon import Mastodon
from mastodon import MastodonError
from rich import print as rprint
from tqdm.asyncio import tqdm

from . import PROGRESS_BAR_FORMAT
from .collect import LinkedMediaHelper
from .collect import MediaAttachment
from .collect import RedditHelper
from .control import Configuration

logger = logging.getLogger("Tootbot")

MP = TypeVar("MP", bound="MastodonPublisher")


class MastodonPublisher:
    """Ease the publishing of content to Mastodon."""

    MAX_LEN_TOOT = 500
    SECRETS_FILE = "mastodon.secret"

    def __init__(
        self: MP,
        config: Configuration,
        secrets_file: str = "mastodon.secret",
    ) -> None:
        self.bot = config.bot
        self.media_only = config.media.media_only
        self.nsfw_marked = config.reddit.nsfw_marked
        self.mastodon_config = config.mastodon_config
        self.num_non_promo_posts = 0
        self.promo = config.promo

        api_base_url = "https://" + self.mastodon_config.domain

        # Log into Mastodon if enabled in settings
        try:
            self.mastodon = Mastodon(
                access_token=secrets_file, api_base_url=api_base_url
            )
            # Make sure authentication is working
            userinfo = self.mastodon.account_verify_credentials()
            mastodon_username = userinfo["username"]
            logger.debug(
                "Successfully authenticated on %s as @%s",
                self.mastodon_config.domain,
                mastodon_username,
            )
        except MastodonError as mastodon_error:
            logger.error("Error while logging into Mastodon: %s", mastodon_error)
            logger.error("Tootbot cannot continue, now shutting down")
            sys.exit(1)

    @staticmethod
    def get_secrets(mastodon_domain: str) -> None:
        """Checks that Mastodon API secrets are available. If not collects
        neccesarry info from user input the create and store APi secrets for
        Mastodon API secrets.

        Arguments:
            mastodon_domain: domain name for Mastodon instance used for tooting. This
            is read from config.ini file, where it must be configured
            logger: Logger to use for error and warning messages.
        """
        api_base_url = "https://" + mastodon_domain

        # Log into Mastodon if enabled in settings
        if not os.path.exists(MastodonPublisher.SECRETS_FILE):
            # If the secret file doesn't exist,
            # it means the setup process hasn't happened yet
            rprint("Mastodon API keys not found. (See wiki for help).")
            user_name = input("[ .. ] Enter email address for Mastodon account: ")
            password = input("[ .. ] Enter password for Mastodon account: ")
            rprint("Generating login key for Mastodon...")
            try:
                Mastodon.create_app(
                    "Tootbot",
                    website="https://codeberg.org/MarvinsMastodonTools/tootbot",
                    api_base_url=api_base_url,
                    to_file=MastodonPublisher.SECRETS_FILE,
                )
                mastodon = Mastodon(
                    client_id=MastodonPublisher.SECRETS_FILE,
                    api_base_url=api_base_url,
                )
                mastodon.log_in(
                    user_name, password, to_file=MastodonPublisher.SECRETS_FILE
                )
                # Make sure authentication is working
                userinfo = mastodon.account_verify_credentials()
                mastodon_username = userinfo["username"]
                rprint(
                    f"Successfully authenticated on "
                    f"{mastodon_domain} as @{mastodon_username}"
                )
                rprint(
                    f"Mastodon login information now stored in "
                    f"{MastodonPublisher.SECRETS_FILE} file"
                )
            except MastodonError as mastodon_error:
                logger.error("Error while logging into Mastodon: %s", mastodon_error)
                logger.error("Tootbot cannot continue, now shutting down")
                sys.exit(1)

    async def make_post(
        self: MP,
        posts: Dict[Any, Any],
        reddit_helper: RedditHelper,
        media_helper: LinkedMediaHelper,
    ) -> None:
        """Makes a post on mastodon from a selection of reddit submissions.

        Arguments:
            posts: A dictionary of subreddit specific hashtags and PRAW Submission
                   objects
            reddit_helper: Helper class to work with Reddit
            media_helper: Helper class to retrieve media linked to from a reddit
            Submission.
        """
        break_to_mainloop = False
        for additional_hashtags, source_posts in posts.items():
            if break_to_mainloop:
                break

            for post in source_posts:

                # Find out if we have any attachments to include with toot.
                logger.debug(
                    "Getting attachments for post %s",
                    source_posts[post].id,
                )
                attachments = MediaAttachment(source_posts[post], media_helper)
                await attachments.get_media_files()
                self._remove_posted_earlier(attachments)

                # Make sure the post contains media,
                # if MEDIA_POSTS_ONLY in config is set to True
                if self.media_only and len(attachments.media_paths) == 0:
                    self.bot.logger.warning(
                        "Skipping %s, non-media posts disabled or "
                        "media file not found",
                        source_posts[post].id,
                    )
                    # Log the post anyway
                    self.bot.post_recorder.log_post(reddit_id=source_posts[post].id)
                    continue

                try:
                    # Generate promo message if needed
                    promo_message = None
                    if self.num_non_promo_posts >= self.promo.every > 0:
                        promo_message = self.promo.message
                        self.num_non_promo_posts = -1

                    # Generate post caption
                    caption = reddit_helper.get_caption(
                        source_posts[post],
                        MastodonPublisher.MAX_LEN_TOOT,
                        add_hash_tags=additional_hashtags,
                        promo_message=promo_message,
                    )

                    # Upload media files if available
                    media_ids = self._post_attachments(attachments)

                    # Determine if spoiler is necessary
                    spoiler = None
                    if source_posts[post].over_18 and self.nsfw_marked:
                        spoiler = "NSFW"

                    # Post to Mastodon
                    toot = self.mastodon.status_post(
                        status=caption,
                        media_ids=media_ids,
                        sensitive=self.mastodon_config.media_always_sensitive,
                        spoiler_text=spoiler,
                    )
                    rprint(f'Posted to Mastodon at {toot["url"]}: "{caption}"')

                    # Log the toot
                    self.bot.post_recorder.log_post(
                        reddit_id=source_posts[post].id,
                        shared_url=source_posts[post].url,
                    )

                    self.num_non_promo_posts += 1
                    self.mastodon_config.number_of_errors = 0

                except MastodonError as mastodon_error:
                    logger.error("Error while posting toot: %s", mastodon_error)
                    # Log the post anyway, so we don't get into a loop of the
                    # same error
                    self.bot.post_recorder.log_post(reddit_id=source_posts[post].id)
                    self.mastodon_config.number_of_errors += 1

                # Clean up media file
                attachments.destroy()

                # Return control to main loop
                break_to_mainloop = True
                break

    def _post_attachments(
        self: MP, attachments: MediaAttachment
    ) -> List[Dict[str, str]]:
        """_post_attachments post any media in attachments.media_paths list.

        Arguments:
            attachments: object with a list of paths to media to be posted on Mastodon

        Returns:
            media_ids: List of dicts returned by mastodon.media_post
        """
        media_ids: List[Dict[str, str]] = []
        if len(attachments.media_paths) == 0:
            return media_ids

        title = "Uploading attachments"
        for checksum, media_path in tqdm(
            attachments.media_paths.items(),
            desc=f"{title:.<60}",
            total=len(attachments.media_paths),
            unit="attachment",
            ncols=120,
            bar_format=PROGRESS_BAR_FORMAT,
        ):
            try:
                mime_type = magic.from_file(media_path, mime=True)
                logger.debug(
                    "Media %s (%s) with checksum: %s",
                    media_path,
                    mime_type,
                    checksum,
                )
                media = self.mastodon.media_post(media_path, mime_type)
                # Log the media upload
                self.bot.post_recorder.log_post(check_sum=checksum)
                media_ids.append(media)
            except (MastodonError, TypeError) as mastodon_error:
                logger.debug(
                    "Error when uploading media %s (%s): %s",
                    media_path,
                    mime_type,
                    mastodon_error,
                )

        return media_ids

    def _remove_posted_earlier(self: MP, attachments: MediaAttachment) -> None:
        """_remove_posted_earlier checks che checksum of all proposed
        attachments and removes any from the list that have already been posted
        earlier.

        Arguments:
            attachments: object with list of paths to media files proposed to be
            posted on Mastodon
        """
        # Build a list of checksums for files that have already been posted earlier
        checksums = []
        for checksum in attachments.media_paths:
            logger.debug(
                "Media attachment (path, checksum): %s, %s",
                attachments.media_paths[checksum],
                checksum,
            )
            if attachments.media_paths[checksum] is None:
                checksums.append(checksum)
            # Check for duplicate of attachment sha256
            elif self.bot.post_recorder.duplicate_check(checksum):
                logger.debug("Media with checksum %s has already been posted", checksum)
                checksums.append(checksum)
        # Remove all empty or previously posted images
        for checksum in checksums:
            attachments.destroy_one_attachment(checksum)
