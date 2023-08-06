"""This module contains helper classes and methods to assist with determining
if a reddit post should be published on Mastodon."""
import configparser
import logging
import sqlite3
import sys
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional
from typing import TypeVar

from rich.logging import RichHandler

from . import POST_RECORDER_SQLITE_DB

PR = TypeVar("PR", bound="PostRecorder")
Config = TypeVar("Config", bound="Configuration")


class PostRecorder:
    """Implements logging of reddit posts published to Mastodon and also
    checking against the log of published content to determine if a post would
    be a duplicate."""

    def __init__(self: PR, cache_file: str, logger: logging.Logger) -> None:
        self.cache_file = cache_file
        self.logger = logger
        self.db_connection = sqlite3.connect(POST_RECORDER_SQLITE_DB)

        # Make sure DB tables exist
        db_cursor = self.db_connection.cursor()
        db_cursor.execute(
            "CREATE TABLE IF NOT EXISTS post (id TEXT PRIMARY KEY) WITHOUT ROWID"
        )
        db_cursor.execute(
            "CREATE TABLE IF NOT EXISTS share "
            "(url TEXT PRIMARY KEY) "
            "WITHOUT ROWID"
        )
        db_cursor.execute(
            "CREATE TABLE IF NOT EXISTS hash "
            "(checksum TEXT PRIMARY KEY) "
            "WITHOUT ROWID"
        )
        self.db_connection.commit()

    def duplicate_check(self: PR, identifier: str) -> bool:
        """Checks if identifier can be found in log file of content posted to
        Mastodon.

        Arguments:
            identifier (string):
                Any identifier we want to make sure has not already been posted.
                This can be id of reddit post, url of media attachment file to be
                posted, or checksum of media attachment file.

        Returns:
            boolean:
                False if "identifier" is not in log of content already posted to
                Mastodon
                True if "identifier" has been found in log of content.
        """
        db_cursor = self.db_connection.cursor()

        # check for reddit_id
        result = db_cursor.execute(
            "SELECT * FROM post where id=:id", {"id": identifier}
        )
        if result.fetchone():
            return True

        # check for Shared URL
        result = db_cursor.execute(
            "SELECT * FROM share where url=:url", {"url": identifier}
        )
        if result.fetchone():
            return True

        # check for attachment hash
        result = db_cursor.execute(
            "SELECT * FROM hash where checksum=:checksum", {"checksum": identifier}
        )
        if result.fetchone():
            return True

        return False

    def log_post(
        self: PR,
        reddit_id: Optional[str] = None,
        shared_url: Optional[str] = None,
        check_sum: Optional[str] = None,
    ) -> None:
        """Logs details about reddit posts that have been published.

        Arguments:
            reddit_id (string):
                Id of post on reddit that was published to Mastodon
            shared_url (string):
                URL of media attachment that was shared on Mastodon
            check_sum (string):
                Checksum of media attachment that was shared on Mastodon.
                This enables checking for duplicate media even if file has been renamed.
        """
        db_cursor = self.db_connection.cursor()
        if reddit_id:
            db_cursor.execute("INSERT INTO post VALUES (?)", (reddit_id,))
        if shared_url:
            db_cursor.execute("INSERT INTO share VALUES (?)", (shared_url,))
        if check_sum:
            db_cursor.execute("INSERT INTO hash VALUES (?)", (check_sum,))
        self.db_connection.commit()


@dataclass
class Secret:
    """Dataclass for API login secrets."""

    client_id: Optional[str]
    client_secret: str


@dataclass
class BotConfig:
    """Dataclass holding configuration values for general behaviour of
    tootbot."""

    cache_file: str
    post_recorder: PostRecorder
    delay_between_posts: int
    run_once_only: bool
    hash_tags: List[str]
    log_level: str
    logger: logging.Logger


@dataclass
class RedditReaderConfig:
    """Dataclass holding configuration values related to Reddit."""

    post_limit: int
    nsfw_allowed: bool
    nsfw_marked: bool
    spoilers: bool
    self_posts: bool
    stickied_allowed: bool


@dataclass
class PromoConfig:
    """Dataclass holding configuration values related to Promotional message
    settings."""

    every: int
    message: str


@dataclass
class HealthCheckConfig:
    """Dataclass holding configuration values around Healthchecks
    monitoring."""

    enabled: bool
    base_url: str
    uuid: str


@dataclass
class MediaConfig:
    """Dataclass holding configuration values around attached media."""

    folder: str
    media_only: bool


@dataclass
class MastodonConfig:
    """Dataclass holding configuration values for Mastodon settings.

    This also stores the number of times the mastodon API has returned
    an error to allow throttling of posting toots in a controlled manner
    """

    domain: str
    media_always_sensitive: bool
    throttling_enabled: bool
    throttling_max_delay: int
    number_of_errors: int


@dataclass
class SubredditConfig:
    """Dataclass to hold configuration settings about the subreddits to be
    monitored."""

    name: str
    tags: str


@dataclass
class Configuration:
    """Dataclass to hold all settings for tootbot."""

    bot: BotConfig
    subreddits: List[SubredditConfig]
    promo: PromoConfig
    health: HealthCheckConfig
    media: MediaConfig
    mastodon_config: MastodonConfig
    reddit: RedditReaderConfig

    def __init__(self: Config) -> None:

        # Make sure config file exists
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
        except configparser.Error as config_error:
            print("[ERROR] Error while reading config file: %s", config_error)
            sys.exit(1)

        # Set-up logging
        log_level = "INFO"
        if config["BotSettings"]["LogLevel"]:
            log_level = config["BotSettings"]["LogLevel"]
        logging.basicConfig(
            level=log_level,
            format="%(name)s[%(process)d] %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            handlers=[RichHandler()],
        )
        logger = logging.getLogger("Tootbot")

        # Bot settings
        bot_settings = config["BotSettings"]
        hash_tags = []
        if config["BotSettings"]["Hashtags"]:
            # Parse list of hashtags
            hash_tags_string = config["BotSettings"]["Hashtags"]
            hash_tags = [x.strip() for x in hash_tags_string.split(",")]
        self.bot = BotConfig(
            cache_file=bot_settings["CacheFile"],
            post_recorder=PostRecorder(bot_settings["CacheFile"], logger),
            delay_between_posts=int(bot_settings["DelayBetweenPosts"]),
            run_once_only=str_to_bool(bot_settings["RunOnceOnly"]),
            hash_tags=hash_tags,
            log_level=bot_settings["LogLevel"],
            logger=logger,
        )

        # Settings related to reddit reader
        self.reddit = RedditReaderConfig(
            post_limit=int(bot_settings["PostLimit"]),
            nsfw_allowed=str_to_bool(bot_settings["NSFWPostsAllowed"]),
            nsfw_marked=str_to_bool(bot_settings["NSFWPostsMarked"]),
            spoilers=str_to_bool(bot_settings["SpoilersAllowed"]),
            self_posts=str_to_bool(bot_settings["SelfPostsAllowed"]),
            stickied_allowed=str_to_bool(bot_settings["StickiedPostsAllowed"]),
        )

        # Settings related to promotional messages
        promo_settings = config["PromoSettings"]
        self.promo = PromoConfig(
            every=int(promo_settings["PromoEvery"]),
            message=promo_settings["PromoMessage"],
        )

        # HealthChecks related settings
        healthchecks_settings = config["HealthChecks"]
        health_enabled = False
        if len(healthchecks_settings["BaseUrl"]) > 0:
            health_enabled = True
        self.health = HealthCheckConfig(
            enabled=health_enabled,
            base_url=healthchecks_settings["BaseUrl"],
            uuid=healthchecks_settings["UUID"],
        )

        # Settings related to media attachments
        media_settings = config["MediaSettings"]
        self.media = MediaConfig(
            folder=media_settings["MediaFolder"],
            media_only=str_to_bool(media_settings["MediaPostsOnly"]),
        )

        # Mastodon info
        mastodon_settings = config["Mastodon"]
        self.mastodon_config = MastodonConfig(
            domain=mastodon_settings["InstanceDomain"],
            media_always_sensitive=str_to_bool(mastodon_settings["SensitiveMedia"]),
            throttling_enabled=str_to_bool(mastodon_settings["ThrottlingEnabled"]),
            throttling_max_delay=int(mastodon_settings["ThrottlingMaxDelay"]),
            number_of_errors=0,
        )

        self.subreddits = []
        for subreddit, hashtags in config.items("Subreddits"):
            self.subreddits.append(SubredditConfig(subreddit, hashtags))

        logger.debug("After loading of config: %s", self)


def str_to_bool(value: Any) -> bool:
    """Helper function to convert a string into a boolean value.

    returns: bool
    """
    if not value:
        return False
    return str(value).lower() in ("y", "yes", "t", "true", "on", "1")
