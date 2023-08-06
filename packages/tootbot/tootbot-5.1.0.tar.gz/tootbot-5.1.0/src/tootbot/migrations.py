"""This module contains methods to help migrate from earlier versions of
tootbot."""
import csv
import sqlite3

from tqdm import tqdm

from . import POST_RECORDER_CSV_FILE
from . import POST_RECORDER_SQLITE_DB
from . import PROGRESS_BAR_FORMAT

CSV_ID_FIELD = 0
CSV_SHARED_URL_FIELD = 3
CSV_CHECKSUM_FIELD = 4


def move_2_sqlite() -> None:
    """This method migrates posting history values recorded in earlier versions
    (4.0.0 and earlier) to a SQLite database we use now."""
    post_ids = set()
    shared_urls = set()
    checksums = set()

    with open(POST_RECORDER_CSV_FILE, encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        title = (
            f"Reading '{POST_RECORDER_CSV_FILE}' file "
            f"and adding ids to '{POST_RECORDER_SQLITE_DB}' DB"
        )

        for row in tqdm(
            csv_reader,
            desc=f"{title:.<60}",
            ncols=120,
            bar_format=PROGRESS_BAR_FORMAT,
        ):
            # Skip first row containing column headers
            if row[CSV_ID_FIELD] == "Reddit post ID":
                continue

            post_ids.add(row[CSV_ID_FIELD])

            if row[CSV_SHARED_URL_FIELD].startswith("http"):
                shared_urls.add(row[CSV_SHARED_URL_FIELD])

            if row[CSV_CHECKSUM_FIELD]:
                checksums.add(row[CSV_CHECKSUM_FIELD])

    ids_to_insert = []
    for item in post_ids:
        ids_to_insert.append((item,))

    urls_to_insert = []
    for item in shared_urls:
        urls_to_insert.append((item,))

    hashes_to_insert = []
    for item in checksums:
        hashes_to_insert.append((item,))

    db_connection = sqlite3.connect(POST_RECORDER_SQLITE_DB)

    # Make sure DB tables exist
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS post (id TEXT PRIMARY KEY) WITHOUT ROWID"
    )
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS share (url TEXT PRIMARY KEY) WITHOUT ROWID"
    )
    db_cursor.execute(
        "CREATE TABLE IF NOT EXISTS hash "
        "(checksum TEXT PRIMARY KEY) "
        "WITHOUT ROWID"
    )
    db_connection.commit()

    db_cursor.executemany("INSERT OR IGNORE INTO post VALUES (?)", ids_to_insert)
    db_cursor.executemany("INSERT OR IGNORE INTO share VALUES (?)", urls_to_insert)
    db_cursor.executemany("INSERT OR IGNORE INTO hash VALUES (?)", hashes_to_insert)
    db_connection.commit()

    db_connection.close()
