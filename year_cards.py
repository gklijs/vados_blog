"""Rebuilds each year page's post cards, and the section's "Latest" link.

vados lists a page's children only as title tiles, so a year page
(root/<section>/<year>/page.json) shows its posts as `leftNotifications`
cards with date and summary instead. Run this after adding or changing a
post; it rewrites those cards from the posts' own page.json files, ordered by
`order` (lowest first, so give the newest post the lowest number), and points
the section page's "Latest:" link at the newest post of the newest year.

Usage: python3 year_cards.py
"""

import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "root")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def posts_of(year_dir):
    posts = []
    for slug in os.listdir(year_dir):
        page = os.path.join(year_dir, slug, "page.json")
        if os.path.isfile(page):
            posts.append((slug, load(page)))
    posts.sort(key=lambda p: (p[1].get("order") is None, p[1].get("order") or 0, p[1]["title"]))
    return posts


for section in sorted(os.listdir(ROOT)):
    section_dir = os.path.join(ROOT, section)
    if not os.path.isdir(section_dir):
        continue
    years = sorted((y for y in os.listdir(section_dir) if y.isdigit()), reverse=True)
    for year in years:
        year_page_path = os.path.join(section_dir, year, "page.json")
        posts = posts_of(os.path.join(section_dir, year))
        year_page = load(year_page_path)
        cards = [
            {
                "content": f'<p class="post-date">{p["subTitle"]}</p><p>{p["summary"]}</p>',
                "title": p["title"],
                "image": p.get("image"),
                "url": f"/{section}/{year}/{slug}",
                "color": "White",
            }
            for slug, p in posts
        ]
        # vados sizes card images for half the page width, so cards with
        # images alternate between the two columns; text-only cards stay in
        # the left one and use the full width.
        if any(card["image"] for card in cards):
            year_page["leftNotifications"] = cards[0::2]
            year_page["rightNotifications"] = cards[1::2]
        else:
            year_page["leftNotifications"] = cards
            year_page["rightNotifications"] = []
        save(year_page_path, year_page)
        print(f"/{section}/{year}: {len(posts)} post(s)")
    if years:
        newest = posts_of(os.path.join(section_dir, years[0]))
        section_page_path = os.path.join(section_dir, "page.json")
        if newest and os.path.isfile(section_page_path):
            slug, p = newest[0]
            section_page = load(section_page_path)
            link = f'<strong>Latest:</strong> <a href="/{section}/{years[0]}/{slug}">{p["title"]}</a>'
            section_page["content"] = re.sub(r"<strong>Latest:</strong> <a [^>]*>[^<]*</a>", link, section_page["content"])
            save(section_page_path, section_page)
            print(f"/{section} latest: {p['title']}")
