import json
import os
import platform
import urllib.request
import zipfile

from yt2navidrome.config import DENO_INSTALL_DIR
from yt2navidrome.utils.logging import get_logger


class DenoInstaller:
    logger = get_logger(__name__)

    @classmethod
    def detect_os_arch(cls) -> tuple[str, str]:
        """Detect the current OS and architecture"""
        os_name = platform.system().lower()
        arch = platform.machine().lower()
        if arch in ("x86_64", "amd64"):
            arch = "x86_64"
        elif arch in ("aarch64", "arm64"):
            arch = "aarch64"
        else:
            arch = arch  # fallback, may need more mapping
        return os_name, arch

    @classmethod
    def get_deno_asset_name(cls, os_name: str, arch: str) -> str | None:
        """Return the correct Deno asset name for the platform."""

        if os_name.lower() == "windows":
            if arch.lower() != "x86_64":
                cls.logger.error(f"Unsupported arch for Windows: {arch}")
                return None

            return "deno-x86_64-pc-windows-msvc.zip"

        elif os_name.lower() == "linux":
            if arch.lower() not in ["x86_64", "aarch64"]:
                cls.logger.error(f"Unsupported arch for Linux: {arch}")
                return None

            return f"deno-{arch}-unknown-linux-gnu.zip"

        elif os_name.lower() == "darwin":
            if arch.lower() not in ["x86_64", "aarch64"]:
                cls.logger.error(f"Unsupported arch for MacOS: {arch}")
                return None

            return f"deno-{arch}-apple-darwin.zip"

        cls.logger.error(f"Unsupported OS for deno: {os_name}")
        return None

    @classmethod
    def download_latest(cls) -> str | None:
        """Download latest deno release from Github"""
        os_name, arch = cls.detect_os_arch()
        asset_name = cls.get_deno_asset_name(os_name, arch)

        if not asset_name:
            cls.logger.error(f"No deno version matching os={os_name} and arch={arch} found.")
            return None

        api_url = "https://api.github.com/repos/denoland/deno/releases/latest"

        try:
            with urllib.request.urlopen(api_url) as resp:  # noqa: S310
                data = json.load(resp)

            for asset in data["assets"]:
                if asset_name in asset["name"]:
                    url = asset["browser_download_url"]

                    cls.logger.debug(f"Downloading Deno from {url}")
                    local_filename: str = asset["name"]
                    urllib.request.urlretrieve(url, local_filename)  # noqa: S310
                    cls.logger.debug(f"Downloaded {local_filename}")

                    return local_filename

            cls.logger.error(f"No matching Deno release found for {os_name} {arch}")
        except Exception:
            cls.logger.exception("Error downloading Deno")

        return None

    @classmethod
    def install(cls, zip_path: str) -> bool:
        """Extract the Deno binary from the zip and place it in DENO_INSTALL_DIR."""
        os.makedirs(DENO_INSTALL_DIR, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    if member == "deno.exe" or member == "deno":
                        zip_ref.extract(member, DENO_INSTALL_DIR)
                        deno_path = os.path.join(DENO_INSTALL_DIR, member)
                        if not deno_path.endswith(".exe"):
                            os.chmod(deno_path, 0o755)  # noqa: S103

                        cls.logger.debug(f"Deno installed at {deno_path}")
                        return True

            cls.logger.error("Deno binary not found in the archive.")
        except Exception:
            cls.logger.exception("Error extracting Deno")

        return False

    @classmethod
    def ensure_deno_installed(cls) -> bool:
        """Download and install Deno if not already present."""
        os_name, _ = cls.detect_os_arch()
        deno_bin = "deno.exe" if os_name == "windows" else "deno"

        deno_path = os.path.join(DENO_INSTALL_DIR, deno_bin)
        if os.path.exists(deno_path):
            cls.logger.debug(f"Deno already installed at {deno_path}")
            return True

        else:
            zip_path = cls.download_latest()
            if zip_path:
                success = cls.install(zip_path)
                return success

        return False
