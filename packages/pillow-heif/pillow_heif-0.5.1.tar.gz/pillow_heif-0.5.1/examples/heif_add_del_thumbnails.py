import os
from pathlib import Path

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/heif_other/nokia/alpha.heic")
    heif_file = pillow_heif.open_heif(image_path)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    pillow_heif.add_thumbnails(heif_file, [256, 372])
    heif_file.save(result_path, quality=35)

    # Next code will remove thumbnails
    heif_file = pillow_heif.open_heif(result_path)
    del heif_file.thumbnails[0]  # remove first thumbnail
    del heif_file.thumbnails[0]  # remove second thumbnail
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}_no_thumbs.heic")
    heif_file.save(result_path, quality=35)
