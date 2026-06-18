import pandas as pd
import glob
import os
import csv

# ── Auto-detect input ────────────────────────────────────────────────────────
buyer_files = glob.glob("*Buyer.csv")
if not buyer_files:
    raise FileNotFoundError("No '- Buyer.csv' file found in the current directory.")

file_path = buyer_files[0]
print(f"📋 Processing: {file_path}")

# Derive output name: strip " - Buyer" suffix from stem
base_name = os.path.splitext(os.path.basename(file_path))[0]
if base_name.endswith(" - Buyer"):
    base_name = base_name[: -len(" - Buyer")]
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
output_file_path = os.path.join(downloads_folder, f"Python - {base_name} - Category.csv")

# ── Read input ───────────────────────────────────────────────────────────────
df = pd.read_csv(file_path)
if "ITEM_NAME" not in df.columns:
    raise ValueError("Expected an 'ITEM_NAME' column in the CSV.")

items_raw = df["ITEM_NAME"].dropna().tolist()

# ── Clean item names ─────────────────────────────────────────────────────────
double_space_items = []
items = []
for item in items_raw:
    cleaned = item.strip()
    if "  " in cleaned:
        double_space_items.append(cleaned)
        while "  " in cleaned:
            cleaned = cleaned.replace("  ", " ")
    items.append(cleaned)

print(f"\n📦 Items to process ({len(items)}):")
for item in items:
    print(f"   {item}")

# ── Sport prompt ─────────────────────────────────────────────────────────────
valid_sports = {
    "BASEBALL": {"name": "BASEBALL", "id": 274},
    "BASKETBALL": {"name": "BASKETBALL", "id": 272},
    "FOOTBALL": {"name": "FOOTBALL", "id": 273},
    "HOCKEY": {"name": "HOCKEY", "id": 303},
    "SOFTBALL": {"name": "SOFTBALL", "id": 275},
    "SOCCER": {"name": "SOCCER", "id": 348},
}

print()
sport_input = input(
    "Does this assortment belong to a sport?\n"
    "(Baseball / Basketball / Football / Hockey / Softball / Soccer — or leave blank to skip): "
).strip().upper()

assortment_sport = None
if sport_input:
    if sport_input in valid_sports:
        assortment_sport = valid_sports[sport_input]
        print(f"✅ All items will be assigned to {assortment_sport['name']} ARIZONA (ID {assortment_sport['id']})")
    else:
        print(f"⚠️  '{sport_input}' not recognized — skipping sport assignment")

# ── Category data ────────────────────────────────────────────────────────────
brands = {
    "BLUE 84":          {"name": "BLUE 84",          "id": 0,   "men": 121, "women": 81},
    "CERTO":            {"name": "CERTO",             "id": 296, "men": 0,   "women": 0},
    "CHAMPION":         {"name": "CHAMPION",          "id": 291, "men": 120, "women": 154},
    "COLOSSEUM":        {"name": "COLOSSEUM",         "id": 302, "men": 171, "women": 172},
    "DUCK COMPANY":     {"name": "DUCK COMPANY",      "id": 285, "men": 0,   "women": 0},
    "ESTABLISHED & CO": {"name": "ESTABLISHED & CO",  "id": 295, "men": 0,   "women": 0},
    "GAMEDAY SOCIAL":   {"name": "GAMEDAY SOCIAL",    "id": 293, "men": 0,   "women": 0},
    "GEAR FOR SPORTS":  {"name": "GEAR FOR SPORTS",   "id": 0,   "men": 123, "women": 0},
    "HYPE AND VICE":    {"name": "HYPE AND VICE",     "id": 0,   "men": 0,   "women": 183},
    "HYPE & VICE":      {"name": "HYPE & VICE",       "id": 0,   "men": 0,   "women": 183},
    "LEAGUE":           {"name": "LEAGUE",            "id": 0,   "men": 83,  "women": 0},
    "LULULEMON":        {"name": "LULULEMON",         "id": 319, "men": 320, "women": 321},
    "NIKE":             {"name": "NIKE",              "id": 298, "men": 46,  "women": 79},
    "OURAY":            {"name": "OURAY",             "id": 299, "men": 48,  "women": 82},
    "REYN SPOONER":     {"name": "REYN SPOONER",      "id": 286, "men": 0,   "women": 0},
    "USCAPE":           {"name": "USCAPE",            "id": 292, "men": 0,   "women": 0},
    "WRANGLER":         {"name": "WRANGLER",          "id": 294, "men": 0,   "women": 0},
    "ZEPHYR":           {"name": "ZEPHYR",            "id": 0,   "men": 47,  "women": 80},
    "ZOOZATZ":          {"name": "ZOOZATZ",           "id": 297, "men": 0,   "women": 209},
}

arizona_sports = {
    "BASEBALL":    {"name": "BASEBALL",    "id": 274},
    "BASKETBALL":  {"name": "BASKETBALL",  "id": 272},
    "FOOTBALL":    {"name": "FOOTBALL",    "id": 273},
    "HOCKEY":      {"name": "HOCKEY",      "id": 303},
    "SOFTBALL":    {"name": "SOFTBALL",    "id": 275},
    "SOCCER":      {"name": "SOCCER",      "id": 348},
}

bottoms     = ("SHORTS", "PANT", "SKIRT", "SKORT", "JOGGER", "JOGGERS", "SWEATPANT", "SWEATPANTS")
outerwears  = ("JACKET", "COAT", "BOMBER", "WINDBREAKER")
polos       = ("POLO", "COLLAR")
sweatshirts = ("HOOD", "CREW", "SWEATSHIRT", "SWEATER", "CARDIGAN", "HOODIE",
               "1/2 ZIP", "1/2ZIP", "FULL ZIP", "FULLZIP", "1/4 ZIP", "1/4ZIP",
               "PULLOVER", "PULL OVER")
hats        = ("HAT", "ADJUSTABLE HAT", "BEANIE", "FITTED HAT", "TRUCKER HAT",
               "TRCKR HAT", "SNAPBACK", "SNAP BACK", " CAP")
loungewear  = ("PAJAMA", "PAJAMAS")
tops        = ("TEE", "T-SHIRT", "TSHIRT", "TANK", "VNECK", "V-NECK")

# ── Categorize ───────────────────────────────────────────────────────────────
assortment_sorted = []
unmatched_items = []

for item in items:
    matched_brand = False
    matched_product_type = False

    # Age groups
    categorized_kid = False
    if "YOUTH" in item:
        assortment_sorted.append(["ALL KIDS", "225", item])
        assortment_sorted.append(["YOUTH", "70", item])
        categorized_kid = True
    elif "TODDLER" in item:
        assortment_sorted.append(["ALL KIDS", "225", item])
        assortment_sorted.append(["TODDLER", "69", item])
        categorized_kid = True
    elif "INFANT" in item:
        assortment_sorted.append(["ALL KIDS", "225", item])
        assortment_sorted.append(["INFANT", "69", item])
        categorized_kid = True

    # Gender
    categorized_gender = ""
    if "WOMEN" in item and not categorized_kid:
        categorized_gender = "women"
    elif not categorized_kid:
        categorized_gender = "men"

    # Product type detection
    is_bottom     = any(k in item for k in bottoms)
    is_outerwear  = any(k in item for k in outerwears)
    is_polo       = any(k in item for k in polos)
    is_sweatshirt = any(k in item for k in sweatshirts)
    is_hat        = any(k in item for k in hats)
    is_loungewear = any(k in item for k in loungewear)
    is_top        = any(k in item for k in tops)
    has_product_type = any([is_bottom, is_outerwear, is_polo, is_sweatshirt, is_hat, is_loungewear, is_top])

    # NEW ARRIVALS (every item)
    assortment_sorted.append(["NEW ARRIVALS", "330", item])

    # MENS
    if categorized_gender == "men" and not categorized_kid:
        assortment_sorted.append(["MENS NEW ARRIVALS", "3", item])
        if is_bottom:
            assortment_sorted.append(["MENS BOTTOMS", "22", item])
            matched_product_type = True
        elif is_outerwear:
            assortment_sorted.append(["MENS OUTWEAR", "21", item])
            matched_product_type = True
        elif is_polo:
            assortment_sorted.append(["MENS POLOS", "18", item])
            matched_product_type = True
        elif is_sweatshirt:
            assortment_sorted.append(["MENS SWEATSHIRTS", "20", item])
            matched_product_type = True
        elif is_hat:
            assortment_sorted.append(["MENS HATS", "119", item])
            matched_product_type = True
        elif is_loungewear:
            assortment_sorted.append(["MENS LOUNGEWEAR", "265", item])
            matched_product_type = True
        elif is_top:
            assortment_sorted.append(["MENS TOP", "19", item])
            matched_product_type = True
        else:
            assortment_sorted.append(["MENS TOP", "19", item])

    # WOMENS
    if categorized_gender == "women" and not categorized_kid:
        assortment_sorted.append(["WOMENS NEW ARRIVALS", "6", item])
        if is_bottom:
            assortment_sorted.append(["WOMENS BOTTOMS", "55", item])
            matched_product_type = True
        elif is_outerwear:
            assortment_sorted.append(["WOMENS OUTWEAR", "54", item])
            matched_product_type = True
        elif is_polo:
            assortment_sorted.append(["WOMENS POLOS", "51", item])
            matched_product_type = True
        elif is_sweatshirt:
            assortment_sorted.append(["WOMENS SWEATSHIRTS", "53", item])
            matched_product_type = True
        elif is_hat:
            assortment_sorted.append(["WOMENS HATS", "143", item])
            matched_product_type = True
        elif is_loungewear:
            assortment_sorted.append(["WOMENS LOUNGEWEAR", "266", item])
            matched_product_type = True
        elif is_top:
            assortment_sorted.append(["WOMENS TOP", "52", item])
            matched_product_type = True
        else:
            assortment_sorted.append(["WOMENS TOP", "52", item])

    # BRANDS
    for brand in brands.values():
        if brand["name"] in item:
            matched_brand = True
            if brand["id"]:
                assortment_sorted.append([brand["name"], str(brand["id"]), item])
            if categorized_gender == "men" and brand["men"]:
                assortment_sorted.append([brand["name"] + " MEN", str(brand["men"]), item])
            if categorized_gender == "women" and brand["women"]:
                assortment_sorted.append([brand["name"] + " WOMEN", str(brand["women"]), item])

    # ARIZONA SPORTS — keyword-based
    for sport in arizona_sports.values():
        if sport["name"] in item:
            assortment_sorted.append([sport["name"] + " ARIZONA", str(sport["id"]), item])

    # ARIZONA SPORTS — assortment-level override
    if assortment_sport:
        assortment_sorted.append(
            [assortment_sport["name"] + " ARIZONA", str(assortment_sport["id"]), item]
        )

    # Track unmatched
    if not matched_brand or not matched_product_type:
        if not matched_brand and not matched_product_type:
            reason = "No brand or product type match"
        elif not matched_brand:
            reason = "No brand match"
        else:
            reason = "No product type match"
        unmatched_items.append((item, reason))

# ── Deduplicate ──────────────────────────────────────────────────────────────
seen = set()
deduped = []
for row in assortment_sorted:
    key = tuple(row)
    if key not in seen:
        seen.add(key)
        deduped.append(row)

removed_dupes = len(assortment_sorted) - len(deduped)
deduped.sort(key=lambda x: x[0])

# ── Write output ─────────────────────────────────────────────────────────────
with open(output_file_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["CATEGORY_NAME", "CATEGORY_ID", "ITEM_NAME"])
    for row in deduped:
        writer.writerow(row)

    if unmatched_items:
        writer.writerow([])
        writer.writerow(["# Items Not Found:"])
        writer.writerow(["# ITEM_NAME", "# REASON"])
        for item, reason in unmatched_items:
            writer.writerow([f"# {item}", f"# {reason}"])

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n🎉 Done!")
print(f"   ✅ {len(items)} items processed")
print(f"   🗑️  {removed_dupes} duplicate rows removed")
if double_space_items:
    print(f"   ⚠️  {len(double_space_items)} items had double spaces (corrected)")
if unmatched_items:
    print(f"   ❓ {len(unmatched_items)} items flagged in Items Not Found:")
    for item, reason in unmatched_items:
        print(f"      - {item} ({reason})")
print(f"\n📁 Saved to: {output_file_path}")
