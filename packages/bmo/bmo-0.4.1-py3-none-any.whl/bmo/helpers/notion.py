# Notion related functions.

__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import logging
import requests
from datetime import datetime, timezone
import dateutil
import pprint
import json

import typing as T
from pathlib import Path

_pprint = pprint.pprint


def title_from_url(url: str) -> str:
    """Notion title always reflect the URL. Its possible to get the title from
    the URL.

    Notes
    -----
    1. https://dev.to/adamcoster/change-a-url-without-breaking-existing-links-4m0d
    """
    txt = url.split("/")[-1]
    # last 32 chars are UUID
    txt = txt[:-32]
    txt = txt.replace("-", " ")
    return txt


def page_icon(page) -> str:
    if page is None:
        return ""
    if page.get("icon") is not None:
        return page["icon"].get("emoji", "")
    return ""


def pages_to_html(pages):
    html = ["<ul>"]
    for page in pages:
        url = page["url"]
        title = title_from_url(url)
        html.append(f" <li> {page_icon(page)} <a href='{url}'>{title}</a></li>")
    html.append("</ul>")
    return "\n".join(html)


def page_dates(page):
    let = dateutil.parser.parse(page["last_edited_time"])
    ct = dateutil.parser.parse(page["created_time"])
    return let, ct


def events_last_week(page) -> T.List[bool]:
    """Return a tuple for bool.
    (True if edited last week, True if created last week)
    """
    NOW = datetime.now(timezone.utc)
    return [(NOW - x).days <= 7 for x in page_dates(page)]


class Notion:
    """Notion related functions."""

    def __init__(self, token: str):
        self.token = token
        self.backup_dir: T.Optional[str] = None

    def _headers(self):
        assert self.token
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def _url(self, endpoint: str) -> str:
        return f"https://api.notion.com/v1/{endpoint}"

    def post(self, endpoint: str, payload={}):
        response = requests.post(
            self._url(endpoint), headers=self._headers(), json=payload
        )
        assert response.ok, response.text
        return response.json()["results"]

    def get(self, endpoint: str):
        response = requests.get(self._url(endpoint), headers=self._headers())
        assert response.ok, response.text
        return response.json()

    def get_block(self, blockid):
        return self.get(f"blocks/{blockid}")

    def backup(self, outdir: T.Optional[Path]):
        """Backup notion content"""
        assert self.token is not None, "Token can't be None or empty"
        timestamp = datetime.now().isoformat()

        folder = Path.home() / "backups" / Path(f"notion_backup-{timestamp}")
        if outdir is not None:
            folder = Path(outdir)
        folder.mkdir(parents=True)

        logging.info(f"Creating backup into {folder}")
        # replace YOUR_INTEGRATION_TOKEN with your own secret token
        response = self.post("search")
        for block in response:
            with open(f'{folder}/{block["id"]}.json', "w") as file:
                file.write(json.dumps(block))

            child_blocks = self.get(f'blocks/{block["id"]}/children')
            if child_blocks:
                datadir = folder / f'{block["id"]}'
                datadir.mkdir()

                for child in child_blocks:
                    with open(datadir / f'{child["id"]}.json', "w") as file:
                        file.write(json.dumps(child))
        logging.info("backup is complete")

    def weekly_update_db(
        self, dbid: str, title: str, include_updated: bool = True
    ) -> str:
        """Results for a database"""
        payload = dict(page_size=100)
        pages = self.post(f"databases/{dbid}/query", payload=payload)
        NOW = datetime.now(timezone.utc)
        new, updated = [], []
        for page in pages:
            let = dateutil.parser.parse(page["last_edited_time"])
            ct = dateutil.parser.parse(page["created_time"])
            if (datetime.now(timezone.utc) - ct).days < 7:
                new.append(page)
            elif (NOW - let).days < 7:
                if include_updated:
                    updated.append(page)

        html = [f"\n<h1>{title}</h1>"] if (new or updated) else []
        if new:
            html.append("<h2>New</h3>")
            html.append(pages_to_html(new))
        if updated:
            html = [f"\n<h1>{title}</h1>"]
            html.append("<h2>Updated</h3>")
            html.append(pages_to_html(updated))
        return "\n".join(html)

    def posts_from_last_week(self):
        """Show weekly updates."""
        payload = {
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
            "filter": {"property": "object", "value": "page"},
        }
        pages = self.post("search", payload=payload)
        for i, page in enumerate(pages):
            if not events_last_week(page)[0]:
                logging.info("Covered one week")
                break
            print(i, page["url"])
        _pprint(pages[-1])
        # print(html)

    def weekly_update(self):
        """Show weekly updates."""
        # logging.info("Weekly update")
        html = ""
        html += self.weekly_update_db("27fdd796747d4e7da5ab7b895a848e54", "News")
        html += self.weekly_update_db("0d4a63a495f84fd0bd9632c82e0963b8", "The chatter")
        html += self.weekly_update_db(
            "444af744203a42f1999356b32a150d2d", "Getting things done", False
        )
        html += self.weekly_update_db(
            "ecaca4cfe5fb436f83e04a4d1b89fc4d", "Project Docs (everyone hates these!)"
        )
        html += self.weekly_update_db(
            "1778deba18a34a338133078b865e5ece", "What are we reading (really?)", False
        )
        html += self.weekly_update_db(
            "994093f42d194f68811df2cbdc91c27b", "Office Inventory", False
        )
        return html
