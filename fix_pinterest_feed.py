#!/usr/bin/env python3
"""
Fetch the Lightspeed product feed, fill in missing/bad google_product_category
values based on product_type mapping, and write a corrected feed for Pinterest.
Writes: ~/workspace/baby-central-babies/tv-site/pinterest-feed.xml
"""
import re, os, urllib.request

WORKSPACE = os.path.expanduser("~/workspace/baby-central-babies")
TV_SITE = os.path.join(WORKSPACE, "tv-site")

# Map Lightspeed product_type -> Google product category
# Google taxonomy: https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt
CATEGORY_MAP = {
    "strollers": "Baby & Toddler > Baby Transport > Baby Strollers",
    "single stroller collections": "Baby & Toddler > Baby Transport > Baby Strollers",
    "double stroller collections": "Baby & Toddler > Baby Transport > Double Strollers",
    "car seats": "Baby & Toddler > Baby Transport > Baby & Toddler Car Seats",
    "car seat": "Baby & Toddler > Baby Transport > Baby & Toddler Car Seats",
    "cribs": "Baby & Toddler > Nursery Furniture > Baby & Toddler Crib Sets",
    "crib": "Baby & Toddler > Nursery Furniture > Baby & Toddler Crib Sets",
    "furniture": "Baby & Toddler > Nursery Furniture",
    "nursery": "Baby & Toddler > Nursery Furniture",
    "dressers": "Baby & Toddler > Nursery Furniture > Dressers",
    "changers": "Baby & Toddler > Nursery Furniture > Changing Tables",
    "gliders": "Baby & Toddler > Nursery Furniture > Gliders",
    "rockers": "Baby & Toddler > Nursery Furniture > Rockers",
    "high chairs": "Baby & Toddler > Baby & Toddler Feeding Supplies > High Chairs",
    "high chair": "Baby & Toddler > Baby & Toddler Feeding Supplies > High Chairs",
    "feeding & nursing": "Baby & Toddler > Baby & Toddler Feeding Supplies",
    "bottles and nipples": "Baby & Toddler > Baby & Toddler Feeding Supplies > Baby Bottles",
    "bottles": "Baby & Toddler > Baby & Toddler Feeding Supplies > Baby Bottles",
    "nipples": "Baby & Toddler > Baby & Toddler Feeding Supplies > Baby Bottle Nipples",
    "sippy cups": "Baby & Toddler > Baby & Toddler Feeding Supplies > Sippy Cups",
    "bibs & plastic bibs": "Baby & Toddler > Baby & Toddler Feeding Supplies > Baby Bibs",
    "bibs": "Baby & Toddler > Baby & Toddler Feeding Supplies > Baby Bibs",
    "feeding utensils": "Baby & Toddler > Baby & Toddler Feeding Supplies > Baby & Toddler Utensils",
    "toys": "Toys & Games > Toys",
    "developmental": "Toys & Games > Toys > Baby & Toddler Toys",
    "rattles": "Toys & Games > Toys > Baby & Toddler Toys > Rattles",
    "teethers": "Toys & Games > Toys > Baby & Toddler Toys > Teethers",
    "stuffed animals": "Toys & Games > Toys > Stuffed Animals",
    "dolls and accessories": "Toys & Games > Toys > Dolls",
    "activity": "Toys & Games > Toys > Activity Toys",
    "pacifiers": "Baby & Toddler > Baby Care > Pacifiers",
    "diapers": "Baby & Toddler > Diapering",
    "wipes": "Baby & Toddler > Diapering > Baby Wipes",
    "bath": "Baby & Toddler > Baby Care > Baby Bath",
    "health & safety": "Baby & Toddler > Baby Care > Health & Baby Care",
    "gear": "Baby & Toddler > Baby Transport",
    "clothing": "Apparel & Accessories > Clothing > Baby & Toddler Clothing",
    "sleepwear": "Apparel & Accessories > Clothing > Baby & Toddler Clothing > Baby Sleepwear",
    "undershirts-onesies": "Apparel & Accessories > Clothing > Baby & Toddler Clothing > Baby Bodysuits",
    "crib sheets": "Baby & Toddler > Nursery Bedding > Crib Sheets",
    "changing pad sheets": "Baby & Toddler > Nursery Bedding > Changing Pad Covers",
    "bassinet sheets": "Baby & Toddler > Nursery Bedding > Bassinet Sheets",
    "porta crib -play yard sheets": "Baby & Toddler > Nursery Bedding > Playard Sheets",
    "blankets": "Baby & Toddler > Nursery Bedding > Baby Blankets",
    "trikes": "Toys & Games > Toys > Ride-On Toys",
    "bouncers": "Baby & Toddler > Baby Care > Baby Bouncers",
    "swings": "Baby & Toddler > Baby Care > Baby Swings",
    "play yards": "Baby & Toddler > Baby Care > Playards",
    "monitors": "Baby & Toddler > Baby Care > Baby Monitors",
    "gates": "Baby & Toddler > Baby Safety > Baby Gates",
}

DEFAULT_CATEGORY = "Baby & Toddler"

def get_category(product_types):
    """Return the best Google category for a list of product_type strings."""
    for pt in product_types:
        key = pt.strip().lower()
        if key in CATEGORY_MAP:
            return CATEGORY_MAP[key]
        # Try partial match
        for map_key, cat in CATEGORY_MAP.items():
            if map_key in key or key in map_key:
                return cat
    return DEFAULT_CATEGORY

def main():
    # Read from local file (fetched via curl due to large size)
    raw_path = "/tmp/pinterest_raw.xml"
    print(f"Reading {raw_path}...")
    with open(raw_path, encoding="utf-8") as f:
        xml = f.read()
    print(f"Read {len(xml)} chars")

    # Process each <item>
    fixed = 0
    already_ok = 0

    def fix_item(m):
        nonlocal fixed, already_ok
        item = m.group(0)
        # Get all product_type values
        pts = re.findall(r"<g:product_type><!\[CDATA\[(.*?)\]\]></g:product_type>", item)
        # Check existing google_product_category
        existing = re.search(r"<g:google_product_category>(.*?)</g:google_product_category>", item, re.DOTALL)
        if existing and existing.group(1).strip():
            already_ok += 1
            return item
        # Fill it in
        cat = get_category(pts)
        new_tag = f"<g:google_product_category>{cat}</g:google_product_category>"
        if existing:
            item = item.replace(existing.group(0), new_tag)
        else:
            # Insert after the last product_type or after <g:brand>
            anchor = re.search(r"(<g:product_type><!\[CDATA\[.*?\]\]></g:product_type>\s*)+", item)
            if anchor:
                item = item[:anchor.end()] + " " + new_tag + item[anchor.end():]
            else:
                # Fallback: insert before </item>
                item = item.replace("</item>", f" {new_tag}</item>")
        fixed += 1
        return item

    new_xml = re.sub(r"<item>.*?</item>", fix_item, xml, flags=re.DOTALL)

    out = os.path.join(TV_SITE, "pinterest-feed.xml")
    with open(out, "w") as f:
        f.write(new_xml)
    print(f"Fixed {fixed} items, {already_ok} already had categories")
    print(f"Wrote {out} ({len(new_xml)} chars)")

if __name__ == "__main__":
    main()
