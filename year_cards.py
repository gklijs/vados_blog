"""Rebuilds each year page's post cards, the section's "Latest" link, and
the home page's latest posts.

vados lists a page's children only as title tiles, so a year page
(root/<section>/<year>/page.json) shows its posts as `leftNotifications`
cards with date and summary instead. Run this after adding or changing a
post; it rewrites those cards from the posts' own page.json files, ordered by
`order` (lowest first, so give the newest post the lowest number), and points
the section page's "Latest:" link at the newest post of the newest year.

The home page gets cards for the newest HOME_POSTS posts of HOME_SECTIONS,
ahead of its other cards (the project cards, which link elsewhere and are
left as they are).

Usage: python3 year_cards.py
"""

import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "root")
HOME_SECTIONS = ["tech"]
HOME_POSTS = 4


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


def card(section, year, slug, p):
    return {
        "content": f'<p class="post-date">{p["subTitle"]}</p><p>{p["summary"]}</p>',
        "title": p["title"],
        "image": p.get("image"),
        "url": f"/{section}/{year}/{slug}",
        "color": "White",
    }


def set_cards(page, cards):
    # vados sizes card images for half the page width, so cards with images
    # alternate between the two columns; text-only cards stay in the left one
    # and use the full width.
    if any(c["image"] for c in cards):
        page["leftNotifications"] = cards[0::2]
        page["rightNotifications"] = cards[1::2]
    else:
        page["leftNotifications"] = cards
        page["rightNotifications"] = []


def years_of(section_dir):
    return sorted((y for y in os.listdir(section_dir) if y.isdigit()), reverse=True)


def external(cards):
    return [c for c in cards if not (c.get("url") or "").startswith("/")]


for section in sorted(os.listdir(ROOT)):
    section_dir = os.path.join(ROOT, section)
    if not os.path.isdir(section_dir):
        continue
    years = years_of(section_dir)
    for year in years:
        year_page_path = os.path.join(section_dir, year, "page.json")
        posts = posts_of(os.path.join(section_dir, year))
        year_page = load(year_page_path)
        set_cards(year_page, [card(section, year, slug, p) for slug, p in posts])
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

latest = [
    card(section, year, slug, p)
    for section in HOME_SECTIONS
    for year in years_of(os.path.join(ROOT, section))
    for slug, p in posts_of(os.path.join(ROOT, section, year))
][:HOME_POSTS]
home_path = os.path.join(ROOT, "page.json")
home = load(home_path)



# The other cards keep their own column, after the posts.
home["leftNotifications"] = latest[0::2] + external(home["leftNotifications"])
home["rightNotifications"] = latest[1::2] + external(home["rightNotifications"])
save(home_path, home)
print(f"/: {len(latest)} latest post(s)")
