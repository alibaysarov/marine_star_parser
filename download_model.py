from pathlib import Path

import argostranslate.package

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

from_code = "en"
to_code = "ru"

argostranslate.package.update_package_index()

available_packages = argostranslate.package.get_available_packages()

package_to_install = next(
    package
    for package in available_packages
    if package.from_code == from_code and package.to_code == to_code
)

downloaded_path = package_to_install.download()

target_path = MODELS_DIR / downloaded_path.name

if downloaded_path != target_path:
    downloaded_path.replace(target_path)

print(f"Model downloaded: {target_path}")
