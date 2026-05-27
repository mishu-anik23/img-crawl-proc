import os
import io
import time
import random
import requests
from PIL import Image, ImageOps
from ddgs import DDGS  # ✅ Updated import


# -------------------------------------------------------------------
# ✅ SETTINGS
# -------------------------------------------------------------------
BRANDS = [
    "AASHIRVAAD", "AHMED", "ANJAPPAR", "BRITANNIA", "DABUR",
    "HALDIRAM", "HEER", "LAZIZA", "MAGGI", "MDH", "NIDO", "PARACHUTE",
    "PARLE", "PG TIPS", "SCHANI", "TATA"
]

SAVE_DIR = "brand-logo"
RESIZE_TO = (350, 350)
PADDING = 10

os.makedirs(SAVE_DIR, exist_ok=True)


# -------------------------------------------------------------------
# ✅ DOWNLOAD IMAGE
# -------------------------------------------------------------------
def download_image(url):
    headers = {
        "User-Agent": random_user_agent(),
        "Referer": "https://duckduckgo.com/",
    }
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content)).convert("RGBA")
    except Exception:
        return None
    return None


# -------------------------------------------------------------------
# ✅ RANDOM USER-AGENT TO AVOID BLOCKING
# -------------------------------------------------------------------
def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)",
        "Mozilla/5.0 (Android 11; Mobile; rv:89.0)"
    ]
    return random.choice(agents)


# -------------------------------------------------------------------
# ✅ SEARCH, DOWNLOAD, RESIZE, SAVE
# -------------------------------------------------------------------
def process_brand_logo(brand):
    print(f"\n🔍 Searching logo for: {brand}")

    ddgs = DDGS()

    # ✅ Retry logic for rate limit errors
    for attempt in range(5):
        try:
            results = ddgs.images(
                keywords=f"{brand} brand logo",
                max_results=10
            )
            break
        except Exception as e:
            print(f"⚠️ Rate-limit or network issue. Retrying... ({attempt+1}/5)")
            time.sleep(random.uniform(3, 7))
    else:
        print(f"❌ Failed to fetch images for {brand} due to rate-limits.")
        return

    if not results:
        print(f"❌ No result for {brand}")
        return

    for item in results:
        img_url = item.get("image")
        if not img_url:
            continue

        print(f"⬇️ Trying: {img_url}")

        img = download_image(img_url)
        if img is None:
            print("⚠️ Download failed.")
            continue

        try:
            img.thumbnail(RESIZE_TO, Image.LANCZOS)

            img_with_pad = ImageOps.expand(img, border=PADDING, fill="white")

            final_img = Image.new("RGBA", RESIZE_TO, "white")
            final_img.paste(
                img_with_pad,
                (
                    (RESIZE_TO[0] - img_with_pad.width) // 2,
                    (RESIZE_TO[1] - img_with_pad.height) // 2
                )
            )

            save_path = os.path.join(SAVE_DIR, f"{brand}.png")
            final_img.save(save_path)

            print(f"✅ Saved: {save_path}")
            return

        except Exception as e:
            print(f"⚠️ Error processing image: {e}")

    print(f"❌ Could not process any logo for {brand}")


# -------------------------------------------------------------------
# ✅ MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    for brand in BRANDS:
        process_brand_logo(brand)

    print("\n✅✅ DONE!")
