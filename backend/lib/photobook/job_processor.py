import tempfile
from pathlib import Path
from typing import Any

from backend.lib.asset_manager.base import AssetManager, AssetStorageKey
from backend.lib.types.asset import Asset
from backend.lib.utils.common import none_throws
from backend.lib.vertex_ai.gemini import Gemini


class JobProcessor:
    def __init__(
        self, job_id: str, job_data: dict[str, Any], asset_manager: AssetManager
    ) -> None:
        self.job_id = job_id
        self.job_data = job_data
        self.image_keys: list[AssetStorageKey] = job_data.get("image_keys", [])
        self.instruction: str = job_data.get("instruction", "")
        self.asset_manager = asset_manager
        self.gemini = Gemini()

    async def process(self) -> dict[str, Any]:
        if not self.image_keys:
            raise ValueError("No image_keys found in job_data")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Download
            tmp_path = Path(tmpdir)
            download_results = await self.asset_manager.download_files_batched(
                [(key, tmp_path / Path(key).name) for key in self.image_keys]
            )
            downloaded_paths = [
                none_throws(asset.cached_local_path)
                for asset in download_results.values()
                if isinstance(asset, Asset)
            ]
            if not downloaded_paths:
                raise RuntimeError("All image downloads failed")

            # Sign URLs
            signed_urls_res = await self.asset_manager.generate_signed_urls_batched(
                self.image_keys,
            )
            signed_urls_sanitized = [
                signed_urls_res.get(key, None) for key in self.image_keys
            ]
            signed_urls_sanitized = [
                k if isinstance(k, str) else "" for k in signed_urls_sanitized
            ]

            img_id_signed_urls_map = {
                Path(key).name: signed_url
                for (key, signed_url) in zip(self.image_keys, signed_urls_sanitized)
            }

            # Run gemini
            try:
                gemini_output = await self.gemini.run_image_understanding_job(
                    self.instruction, downloaded_paths
                )
            except Exception as e:
                gemini_output = f"Gemini generation failed: {e}"

        return {
            "job_id": self.job_id,
            "processed_keys": self.image_keys,
            "signed_urls": signed_urls_sanitized,
            "img_id_signed_urls_map": img_id_signed_urls_map,
            "successful_files": [str(p) for p in downloaded_paths],
            "gemini_result": gemini_output,
        }
