"""This module contains helper classes and methods to assist with the
collection of content to be posted to Mastodon."""
# pylint: disable=E1136
import asyncio
import configparser
import hashlib
import logging
import os
import re
import sys
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import TypeVar
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

import asyncpraw.exceptions
import asyncprawcore
import httpx
from asyncpraw.models import Submission
from bs4 import BeautifulSoup
from gfycat.client import GfycatClient
from gfycat.error import GfycatClientError
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
from PIL import Image as PILImage
from rich import print as rprint
from tqdm.asyncio import tqdm

from . import PROGRESS_BAR_FORMAT
from . import USER_AGENT
from .control import Configuration
from .control import Secret
from .control import SubredditConfig

logger = logging.getLogger("Tootbot")

FATAL_TOOTBOT_ERROR = "Tootbot cannot continue, now shutting down"

RH = TypeVar("RH", bound="RedditHelper")
LMH = TypeVar("LMH", bound="LinkedMediaHelper")
MA = TypeVar("MA", bound="MediaAttachment")


async def get_file(img_url: str, file_path: str, progress_label: str) -> Optional[str]:
    """Utility method to save a file located at img_url to a file located at
    filepath.

    Arguments:
        img_url (string): url of imgur image to download
        file_path (string): directory and filename where to save the downloaded image to
        progress_label (string): Message to add to progress bar

    Returns:
        file_path (string): path to downloaded image or None if no image was downloaded
    """
    logger.debug("!!! 🎇🎇 Async Get File %s from %s", file_path, img_url)
    try:
        client = httpx.AsyncClient()
        meta = await client.head(url=img_url)
        size = int(meta.headers["content-length"])
        async with client.stream(method="GET", url=img_url) as response:
            with open(file_path, "wb") as file_out:
                async for chunk in tqdm(
                    iterable=response.aiter_bytes(1),
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"{progress_label:.<60}",
                    ncols=120,
                    bar_format=PROGRESS_BAR_FORMAT,
                    total=size,
                ):
                    file_out.write(chunk)
            return file_path

    except httpx.HTTPError as save_image_error:
        logger.error("Failed to download (%s): %s", img_url, save_image_error)
        return None


def get_secrets() -> Dict[str, Secret]:
    """Helper method to collect all api secrets either from already store
    secrets files or from user input."""

    secrets = {}
    secrets["reddit"] = _get_reddit_secret()
    secrets["gfycat"] = _get_gfycat_secret()
    secrets["imgur"] = _get_imgur_secret()

    return secrets


def _get_reddit_secret() -> Secret:
    """Helper method to collect reddit secret from stored secrets file or from
    user input."""
    reddit_secrets_file = "reddit.secret"
    reddit_config = configparser.ConfigParser()
    if not os.path.exists(reddit_secrets_file):
        rprint("Reddit API keys not found. Please provide Reddit API values.")
        rprint("(See wiki if you need help).")
        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        reddit_agent = "".join(input("[ .. ] Enter Reddit agent: ").split())
        reddit_client_secret = "".join(
            input("[ .. ] Enter Reddit client secret: ").split()
        )
        # Make sure authentication is working
        try:
            # create Reddit api connection and load posts from announcements subreddit
            # to confirm reddit connection works
            reddit_client = asyncpraw.Reddit(
                user_agent="Tootbot",
                client_id=reddit_agent,
                client_secret=reddit_client_secret,
            )
            subreddit = reddit_client.subreddit("announcements")
            for _post in subreddit.hot():
                continue

            # It worked, so save the keys to a file
            reddit_config["Reddit"] = {
                "Agent": reddit_agent,
                "ClientSecret": reddit_client_secret,
            }
            with open(reddit_secrets_file, "w", encoding="utf8") as new_reddit_secrets:
                reddit_config.write(new_reddit_secrets)
        except asyncprawcore.AsyncPrawcoreException as reddit_exception:
            logger.error("Error while logging into Reddit: %s", reddit_exception)
            logger.error(FATAL_TOOTBOT_ERROR)
            sys.exit(1)
    else:
        # Read API keys from secret file
        reddit_config.read(reddit_secrets_file)

    return Secret(
        client_id=reddit_config["Reddit"]["Agent"],
        client_secret=reddit_config["Reddit"]["ClientSecret"],
    )


def _get_gfycat_secret() -> Secret:
    """_get_gfycat_secrets checks if the Gfycat api secrets file exists.

    - If the file exists, this method reads the files and returns the secrets
      in a Secret dataclass.
    - If the file doesn't exist it asks the user over stdin to supply these values
      and then saves them into the gfycat_secrets file

    Arguments:
        logger (logging.Logger): logger to use for general logging messages

    Returns:
        api_secrets (Secret): instance of Secret class containing the api secrets
        to work with gyfycat
    """

    secrets_file = "gfycat.secret"
    if not os.path.exists(secrets_file):
        rprint("Gfycat API keys not found. (See wiki if you need help).")

        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        gfycat_client_id = "".join(input("[ .. ] Enter Gfycat client ID: ").split())
        gfycat_client_secret = "".join(
            input("[ .. ] Enter Gfycat client secret: ").split()
        )
        # Make sure authentication is working
        try:
            gfycat_client = GfycatClient(gfycat_client_id, gfycat_client_secret)

            # If this call doesn't work, it'll throw an ImgurClientError
            gfycat_client.query_gfy("oddyearlyhorsefly")
            # It worked, so save the keys to a file
            gfycat_config = configparser.ConfigParser()
            gfycat_config["Gfycat"] = {
                "ClientID": gfycat_client_id,
                "ClientSecret": gfycat_client_secret,
            }
            with open(secrets_file, "w", encoding="utf8") as file:
                gfycat_config.write(file)
        except GfycatClientError as gfycat_error:
            logger.error("Error while logging into Gfycat: %s", gfycat_error)
            logger.error(FATAL_TOOTBOT_ERROR)
            sys.exit(1)
    else:
        # Read API keys from secret file
        gfycat_config = configparser.ConfigParser()
        gfycat_config.read(secrets_file)

    return Secret(
        client_id=gfycat_config["Gfycat"]["ClientID"],
        client_secret=gfycat_config["Gfycat"]["ClientSecret"],
    )


def _get_imgur_secret() -> Secret:
    """_get_imgur_secrets checks if the Imgur api secrets file exists.

    - If the file exists, this method reads the imgur secrets file and returns the
      secrets a Secret dataclass.
    - If the file doesn't exist it asks the user over stdin to supply these values
      and then saves them into the imgur_secrets file

    Arguments:
        logger (logging.Logger): logger to use for general logging messages

    Returns:
        api_secrets (Secret): instance of Secret class containing the api secrets
        to work with imgut
    """
    secrets_file = "imgur.secret"
    if not os.path.exists(secrets_file):
        rprint("Imgur API keys not found. (See wiki if you need help).")

        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        imgur_client_id = "".join(input("[ .. ] Enter Imgur client ID: ").split())
        imgur_client_secret = "".join(
            input("[ .. ] Enter Imgur client secret: ").split()
        )
        # Make sure authentication is working
        try:
            imgur_client = ImgurClient(imgur_client_id, imgur_client_secret)

            # If this call doesn't work, it'll throw an ImgurClientError
            imgur_client.get_album("dqOyj")
            # It worked, so save the keys to a file
            imgur_config = configparser.ConfigParser()
            imgur_config["Imgur"] = {
                "ClientID": imgur_client_id,
                "ClientSecret": imgur_client_secret,
            }
            with open(secrets_file, "w", encoding="UTF-8") as file:
                imgur_config.write(file)
        except ImgurClientError as imgur_error:
            logger.error("Error while logging into Imgur: %s", imgur_error)
            logger.error(FATAL_TOOTBOT_ERROR)
            sys.exit(1)
    else:
        # Read API keys from secret file
        imgur_config = configparser.ConfigParser()
        imgur_config.read(secrets_file)

    return Secret(
        client_id=imgur_config["Imgur"]["ClientID"],
        client_secret=imgur_config["Imgur"]["ClientSecret"],
    )


class RedditHelper:
    """RedditHelper provides methods to collect data / content from reddit to
    then post on Mastodon."""

    # Check if reddit access details in 'reddit.secret' file has already been set up
    # and load it, otherwise guide user through setting it up.
    def __init__(self: RH, config: Configuration, api_secret: Secret) -> None:
        self.config = config
        self.posts: Dict[str, asyncpraw.models.Submission] = {}
        self.api_secret = api_secret

    async def get_all_reddit_posts(self: RH) -> None:
        """Collects posts from all configured subreddits."""
        tasks = []

        reddit_con = asyncpraw.Reddit(
            user_agent=USER_AGENT,
            client_id=self.api_secret.client_id,
            client_secret=self.api_secret.client_secret,
        )

        for subreddit in self.config.subreddits:
            tasks.append(self.get_reddit_posts(subreddit, reddit_con))
        progress_title = "Processing Subreddits"
        task_results = await tqdm.gather(
            *tasks,
            desc=f"{progress_title:.<60}",
            ncols=120,
            bar_format=PROGRESS_BAR_FORMAT,
            total=len(tasks),
        )

        for result in task_results:
            self.posts.update(result)

        await reddit_con.close()

    async def get_reddit_posts(
        self: RH,
        subreddit: SubredditConfig,
        reddit_con: asyncpraw.Reddit,
    ) -> Dict[str, asyncpraw.models.Submission]:
        """Collects posts considered hot from configured sub/multi-reddits."""
        posts = {}
        logger.debug("Retrieving posts from %s", subreddit.name)
        try:
            subreddit_info = await reddit_con.subreddit(subreddit.name)
            subreddit_posts: Dict[str, asyncpraw.models.Submission] = {}
            async for submission in subreddit_info.hot(
                limit=self.config.reddit.post_limit
            ):
                subreddit_posts[submission.id] = submission
            posts[subreddit.tags] = subreddit_posts
        except asyncprawcore.AsyncPrawcoreException as reddit_error:
            logger.warning(
                "Error when getting reddit posts from r/%s: %s",
                subreddit.name,
                reddit_error,
            )
        return posts

    def winnow_reddit_posts(self: RH) -> None:
        """Filters out reddit posts according to configuration and whether it
        has already been tooted."""
        recorder = self.config.bot.post_recorder
        nsfw_allowed = self.config.reddit.nsfw_allowed
        self_posts_allowed = self.config.reddit.self_posts
        spoilers_allowed = self.config.reddit.spoilers
        stickied_allowed = self.config.reddit.stickied_allowed

        title = "Winnowing chaff "
        for posts in tqdm(
            self.posts.values(),
            desc=f"{title:.<60}",
            total=len(self.posts),
            ncols=120,
            bar_format=PROGRESS_BAR_FORMAT,
        ):
            post_ids = list(posts.keys())
            for post_id in post_ids:

                if posts[post_id].over_18 and not nsfw_allowed:
                    # Skip over NSFW posts if they are disabled in the config file
                    logger.debug("Skipping %s, it is marked as NSFW", post_id)
                    del posts[post_id]
                    continue

                if posts[post_id].is_self and not self_posts_allowed:
                    # Skip over NSFW posts if they are disabled in the config file
                    logger.debug("Skipping %s, it is a self post", post_id)
                    del posts[post_id]
                    continue

                if posts[post_id].spoiler and not spoilers_allowed:
                    # Skip over posts marked as spoilers if they are disabled in
                    # the config file
                    logger.debug("Skipping %s, it is marked as a spoiler", post_id)
                    del posts[post_id]
                    continue

                if posts[post_id].stickied and not stickied_allowed:
                    logger.debug("Skipping %s, it is stickied", post_id)
                    del posts[post_id]
                    continue

                if recorder.duplicate_check(post_id):
                    logger.debug("Skipping %s, it has already been tooted", post_id)
                    del posts[post_id]
                    continue

                if recorder.duplicate_check(posts[post_id].url):
                    logger.debug("Skipping %s, it has already been tooted", post_id)
                    del posts[post_id]
                    continue

    def get_caption(
        self: RH,
        submission: Submission,
        max_len: int,
        add_hash_tags: Optional[str] = None,
        promo_message: Optional[str] = None,
    ) -> str:
        """get_caption returns the text to be posted to mastodon. This is
        determined from the text of the reddit submission, if a promo message
        should be included, and any hashtags.

        Arguments:
            submission (Submission): PRAW Submission object for the reddit post we are
            determining the mastodon toot text for.
            max_len: (int): The maximum length the text for the mastodon toot can be.
            add_hash_tags (str): additional hashtags to be added to global hashtags
            defined in config file. The hashtags must be comma delimited
            promo_message (str): Any promo message that must be added to end of caption.
            Set to None if no promo message to be added
        """
        caption = ""
        # Create string of hashtags
        hashtag_string = ""
        promo_string = ""
        hashtags_for_post = self.config.bot.hash_tags

        # Workout hashtags for post
        if add_hash_tags is not None:
            hashtags_for_subreddit = [x.strip() for x in add_hash_tags.split(",")]
            hashtags_for_post = hashtags_for_subreddit + self.config.bot.hash_tags
        if hashtags_for_post:
            for tag in hashtags_for_post:
                # Add hashtag to string, followed by a space for the next one
                hashtag_string += "#" + tag + " "

        if promo_message:
            promo_string = f" \n \n{self.config.promo.message}"
        caption_max_length = max_len
        caption_max_length -= (
            len(submission.shortlink) - len(hashtag_string) - len(promo_string)
        )

        # Create contents of the Mastodon post
        if len(submission.title) < caption_max_length:
            caption = submission.title + " "
        else:
            caption = submission.title[caption_max_length - 2] + "... "
        caption += hashtag_string + submission.shortlink + promo_string
        return caption


class LinkedMediaHelper:
    """ImgurHelper provides methods to collect data / content from Imgur and
    Gfycat."""

    def __init__(
        self: LMH,
        config: Configuration,
        gfycat_secrets: Secret,
        imgur_secrets: Secret,
    ) -> None:
        self.save_dir = config.media.folder

        try:
            self.imgur_client = ImgurClient(
                client_id=imgur_secrets.client_id,
                client_secret=imgur_secrets.client_secret,
            )
            self.gfycat_client = GfycatClient(
                client_id=gfycat_secrets.client_id,
                client_secret=gfycat_secrets.client_secret,
            )
        except ImgurClientError as imgur_error:
            logger.error("Error on creating ImgurClient: %s", imgur_error)
            logger.error(FATAL_TOOTBOT_ERROR)
            sys.exit(1)
        except GfycatClientError as gfycat_error:
            logger.error("Error on creating GfycatClient: %s", gfycat_error)
            logger.error(FATAL_TOOTBOT_ERROR)
            sys.exit(1)

    async def get_imgur_image(
        self: LMH, img_url: str, max_images: int = 4
    ) -> List[str]:
        """get_imgur_image downloads images from imgur.

        Arguments:
            img_url: url of imgur image to download
            max_images: maximum number of images to download and process, Defaults to 4

        Returns:
            file_paths (string): path to downloaded image or None if no image was
            downloaded
        """

        # Working demo of regex: https://regex101.com/r/G29uGl/2
        regex = r"(?:.*)imgur\.com(?:\/gallery\/|\/a\/|\/)(.*?)(?:\/.*|\.|$)"
        regex_match = re.search(regex, img_url, flags=0)

        if not regex_match:
            logger.error("Could not identify Imgur image/gallery ID at: %s", img_url)
            return []

        # Get the Imgur image/gallery ID
        imgur_id = regex_match.group(1)

        image_urls = self._get_image_urls(img_url, imgur_id)

        # Download and process individual images (up to max_images)
        imgur_paths: List[str] = []
        for image_url in image_urls:
            # If the URL is a GIFV or MP4 link, change it to the GIF version
            file_extension = os.path.splitext(image_url)[-1].lower()
            if file_extension == ".gifv":
                file_extension = ".gif"
                image_url = image_url.replace(".gifv", ".gif")
            elif file_extension == ".mp4":
                file_extension = ".gif"
                image_url = image_url.replace(".mp4", ".gif")

            # Download the image
            file_path = (
                self.save_dir
                + "/"
                + imgur_id
                + "_"
                + str(len(imgur_paths))
                + file_extension
            )
            logger.debug(
                "Downloading Imgur image at URL %s to %s", image_url, file_path
            )
            saved_paths = await get_file(
                img_url=image_url,
                file_path=file_path,
                progress_label="Downloading Imgur image",
            )

            # Imgur will sometimes return a single-frame thumbnail
            # instead of a GIF, so we need to check for this
            if saved_paths and (
                file_extension != ".gif" or self._check_imgur_gif(saved_paths)
            ):
                imgur_paths.append(saved_paths)

            if len(imgur_paths) == max_images:
                break

        return imgur_paths

    def _get_image_urls(self: LMH, img_url: str, imgur_id: str) -> List[str]:
        """_get_image_urls builds a list of urls of all Imgur images identified
        by imgur_id.

        Arguments:
            img_url: URL to IMGUR post
            imgur_id: ID for IMGUR post

        Returns:
            imgur_urls: List of urls to images of Imgur post identified byr imgur_id
        """
        image_urls = []
        try:
            if any(s in img_url for s in ("/a/", "/gallery/")):  # Gallery links
                logger.debug("Imgur link points to gallery: %s", img_url)
                images = self.imgur_client.get_album_images(imgur_id)
                for image in images:
                    image_urls.append(image.link)
            else:  # Single image
                imgur_img = self.imgur_client.get_image(imgur_id)
                image_urls = [imgur_img.link]  # pylint: disable=no-member

        except ImgurClientError as imgur_error:
            logger.error("Could not get information from imgur: %s", imgur_error)
        return image_urls

    def _check_imgur_gif(self: LMH, file_path: str) -> bool:
        """_check_imgur_gif checks if a file downloaded from imgur is indeed a
        gif. If file is not a gif, remove the file.

        Arguments:
            file_path: file name and path to downloaded image

        Returns:
             True if downloaded image is indeed a GIF, otherwise returns False
        """
        img = PILImage.open(file_path)
        mime = PILImage.MIME[img.format]
        img.close()

        if mime != "image/gif":
            logger.warning("Imgur: not a GIF, not posting")
            try:
                os.remove(file_path)
            except OSError as remove_error:
                logger.error("Error while deleting media file: %s", remove_error)
            return False

        return True

    async def get_gfycat_image(self: LMH, img_url: str) -> Optional[str]:
        """get_gfycat_image downloads full resolution images from gfycat.

        Arguments:
            img_url (string): url of gfycat image to download

        Returns:
            file_path (string): path to downloaded image or None if no image was
            downloaded
        """
        gfycat_url = ""
        file_path = self.save_dir + "/"
        try:
            gfycat_name = os.path.basename(urlsplit(img_url).path)
            response = httpx.get(img_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            for tag in soup.find_all("source", src=True):
                src = tag["src"]
                if "giant" in src and "mp4" in src:
                    gfycat_url = src
            file_path += gfycat_name + ".mp4"
        except (
            httpx.HTTPError,
            GfycatClientError,
        ) as gfycat_error:
            logger.error("Error downloading Gfycat link: %s", gfycat_error)
            return None

        if gfycat_url == "":
            logger.debug("Empty Gfycat URL; no attachment to download")
            return None

        logger.debug("Downloading Gfycat at URL %s to %s", gfycat_url, file_path)

        saved_paths = await get_file(
            img_url=gfycat_url,
            file_path=file_path,
            progress_label="Downloading Gfycat image/video",
        )

        return saved_paths

    async def get_reddit_image(self: LMH, img_url: str) -> Optional[str]:
        """get_reddit_image downloads full resolution images from i.reddit or
        reddituploads.com.

        Arguments:
            img_url (string): url of imgur image to download

        Returns:
            file_path (string): path to downloaded image or None if no image was
            downloaded
        """
        file_name = os.path.basename(urlsplit(img_url).path)
        file_extension = os.path.splitext(img_url)[1].lower()
        # Fix for issue with i.reddituploads.com links not having a
        # file extension in the URL
        if not file_extension:
            file_extension += ".jpg"
            file_name += ".jpg"
            img_url += ".jpg"
        # Download the file
        file_path = self.save_dir + "/" + file_name
        logger.debug(
            "Downloading file at URL %s to %s, file type identified as %s",
            img_url,
            file_path,
            file_extension,
        )

        saved_path = await get_file(
            img_url=img_url,
            file_path=file_path,
            progress_label="Downloading reddit image",
        )

        return saved_path

    async def get_reddit_gallery(
        self: LMH,
        reddit_post: Submission,
        max_images: int = 4,
    ) -> List[Optional[str]]:
        """get_reddit_gallery downloads up to max_images images from a reddit
        gallery post and returns a List of file_paths downloaded images.

        Arguments:
            reddit_post (reddit_post):  reddit post / submission object
            max_images (int): [optional] maximum number of images to download.
            Default is 4

        Returns:
            file_paths (List[str]) a list of the paths to downloaded files. If no
            images have been downloaded, and empty list will be returned.
        """
        file_paths: List[Optional[str]] = []
        gallery_items: List[Dict[str, Any]] = reddit_post.gallery_data["items"]
        tasks: List[Any] = []
        for item in gallery_items:
            media_id = item["media_id"]
            meta = reddit_post.media_metadata[media_id]
            logger.debug("Media Metadata: %s", meta)
            if "e" in meta and meta["e"] == "Image":
                source = meta["s"]
                save_path = (
                    self.save_dir + "/" + media_id + "." + meta["m"].split("/")[1]
                )
                logger.debug(
                    "Gallery file_path, source: %s - %s", save_path, source["u"]
                )
                tasks.append(get_file(source["u"], save_path, f"image {len(tasks)+1}"))

                if len(tasks) == max_images:
                    break

        rprint("Donwloading images from reddit gallery")
        file_paths = await asyncio.gather(*tasks)

        return file_paths

    async def get_reddit_video(self: LMH, reddit_post: Submission) -> Optional[str]:
        """get_reddit_video downloads full resolution video from i.reddit or
        reddituploads.

        Arguments:
            reddit_post (reddit_post): reddit post / submission object

        Returns:
            file_path (string): path to downloaded video or None if no image was
            downloaded
        """
        # Get URL for MP4 version of reddit video
        video_url = reddit_post.media["reddit_video"]["fallback_url"]
        file_path: str = self.save_dir + "/" + reddit_post.id + ".mp4"
        logger.debug("Downloading Reddit video at URL %s to %s", video_url, file_path)

        saved_path = await get_file(
            img_url=video_url,
            file_path=file_path,
            progress_label="Downloading video from Reddit",
        )
        return saved_path

    async def get_giphy_image(self: LMH, img_url: str) -> Optional[str]:
        """get_giphy_image downloads full or low resolution image from giphy.

        Arguments:
            img_url (string): url of giphy image to download

        Returns:
            file_path (string): path to downloaded image or None if no image was
            downloaded
        """
        # Working demo of regex: https://regex101.com/r/o8m1kA/2
        regex = (
            r"https?://((?:.*)giphy\.com/media/|giphy.com"
            r"/gifs/|i.giphy.com/)(.*-)?(\w+)(/|\n)"
        )
        match = re.search(regex, img_url, flags=0)
        if not match:
            logger.error("Could not identify Giphy ID in this URL: %s", img_url)
            return None

        # Get the Giphy ID
        giphy_id = match.group(3)
        # Download the MP4 version of the GIF
        giphy_url = "https://media.giphy.com/media/" + giphy_id + "/giphy.mp4"
        file_path = self.save_dir + "/" + giphy_id + "giphy.mp4"

        saved_paths = await get_file(
            img_url=giphy_url,
            file_path=file_path,
            progress_label="Downloading Giphy image/video",
        )

        logger.debug("Downloaded Giphy at URL %s to %s", giphy_url, saved_paths)

        return saved_paths

    async def get_generic_image(self: LMH, img_url: str) -> Optional[str]:
        """get_generic_image downloads image or video from a generic url to a
        media file.

        Arguments:
            img_url (string): url to image or video file

        Returns:
            file_path (string): path to downloaded video or None if no image was
            downloaded
        """
        # First check if URL starts with http:// or https://
        regex = r"^https?://"
        match = re.search(regex, img_url, flags=0)
        if not match:
            logger.debug("Post link is not a full link: %s", img_url)
            return None

        # Check if URL is an image or MP4 file, based on the MIME type
        image_formats = (
            "image/png",
            "image/jpeg",
            "image/gif",
            "image/webp",
            "video/mp4",
        )
        try:
            # img_url has already been checked that it starts with "http://" or
            # "https://" above.
            with urlopen(img_url) as img_site:  # nosec B310
                meta = img_site.info()

        except (URLError, UnicodeEncodeError) as url_error:
            logger.error("Error while opening URL %s", url_error)
            return None

        if meta["content-type"] not in image_formats:
            logger.debug("URL does not point to a valid image file: %s", img_url)
            return None

        # URL appears to be an image, so download it
        file_name = os.path.basename(urlsplit(img_url).path)
        file_path = self.save_dir + "/" + file_name
        logger.debug("Downloading file at URL %s to %s", img_url, file_path)

        saved_path = await get_file(
            img_url=img_url,
            file_path=file_path,
            progress_label="Downloading generic image",
        )

        return saved_path


class MediaAttachment:
    """MediaAttachment contains code to retrieve the appropriate images or
    videos to include in a reddit post to be shared on Mastodon."""

    def __init__(
        self: MA, reddit_post: Submission, image_helper: LinkedMediaHelper
    ) -> None:

        self.media_paths: Dict[str, str] = {}
        self.reddit_post = reddit_post
        self.media_url = self.reddit_post.url
        self.image_helper = image_helper

    async def get_media_files(self: MA) -> None:
        """Downloads media files linked to given reddit_post."""
        logger.debug("URL for post(%s): %s ", self.reddit_post, self.media_url)

        media_paths = await self.get_media()
        for media_path in media_paths:
            logger.debug("Media path for checksum calculation: %s", media_path)
            if media_path:
                sha256 = hashlib.sha256()
                with open(media_path, "rb") as media_file:
                    # Read and update hash string value in blocks of 64K
                    while True:
                        data = media_file.read(2**16)
                        if not data:
                            break
                        sha256.update(data)

                self.media_paths[sha256.hexdigest()] = media_path

    def destroy(self: MA) -> None:
        """Removes any files downloaded and clears out the object
        attributes."""
        try:
            for media_path in self.media_paths.values():
                if media_path is not None:
                    os.remove(media_path)
                    logger.debug("Deleted media file at %s", media_path)
        except OSError as delete_error:
            logger.error("Error while deleting media file: %s", delete_error)

        self.media_paths = {}
        self.media_url = None

    def destroy_one_attachment(self: MA, checksum: str) -> None:
        """Removes file with checksum downloaded.

        Arguments:
            checksum (string): key to media_paths dictionary for file to be removed.
        """
        try:
            media_path = self.media_paths[checksum]
            if media_path is not None:
                os.remove(media_path)
                logger.debug("Deleted media file at %s", media_path)
            self.media_paths.pop(checksum)
        except OSError as delete_error:
            logger.error("Error while deleting media file: %s", delete_error)

    async def get_media(self: MA) -> List[Optional[str]]:
        """Determines which method to call depending on which site the
        media_url is pointing to."""
        if not os.path.exists(self.image_helper.save_dir):
            os.makedirs(self.image_helper.save_dir)
            logger.debug(
                "Media folder not found, created new folder: %s",
                self.image_helper.save_dir,
            )

        file_paths = []
        saved_media_path: Optional[str]
        saved_media_paths: Iterable[Optional[str]]

        # Download and save the linked image
        if any(s in self.media_url for s in ("i.redd.it", "i.reddituploads.com")):
            saved_media_path = await self.image_helper.get_reddit_image(self.media_url)
            file_paths.append(saved_media_path)
        elif "v.redd.it" in self.media_url and not self.reddit_post.media:
            logger.error(
                "Reddit API returned no media for this URL: %s", self.media_url
            )
        elif "v.redd.it" in self.media_url:
            saved_media_path = await self.image_helper.get_reddit_video(
                self.reddit_post
            )
            file_paths.append(saved_media_path)

        elif "imgur.com" in self.media_url:
            saved_media_paths = await self.image_helper.get_imgur_image(self.media_url)
            file_paths.extend(saved_media_paths)

        elif "gfycat.com" in self.media_url:
            saved_media_path = await self.image_helper.get_gfycat_image(self.media_url)
            file_paths.append(saved_media_path)

        elif "giphy.com" in self.media_url:
            saved_media_path = await self.image_helper.get_giphy_image(self.media_url)
            file_paths.append(saved_media_path)

        elif "reddit.com/gallery/" in self.media_url:  # Need to check for gallery post
            if hasattr(self.reddit_post, "is_gallery"):
                logger.debug("%s is a gallery post", self.reddit_post.id)
                save_media_paths = await self.image_helper.get_reddit_gallery(
                    self.reddit_post
                )
                file_paths.extend(save_media_paths)

        else:
            saved_media_path = await self.image_helper.get_generic_image(self.media_url)
            file_paths.append(saved_media_path)

        return file_paths
