"""HuggingFace trending models widget using HuggingFace API."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..core.base_widget import BaseWidget
from ..core.http_cache import get_http_client


class HuggingfaceModelsWidget(BaseWidget):
    """Displays trending models from HuggingFace.

    Optional params:
        - limit: Number of models to show (default: 10)
    """

    def get_required_params(self) -> list[str]:
        return []

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch trending models from HuggingFace."""
        self.validate_params()

        limit = self.merged_params.get("limit", 10)
        client = get_http_client()

        try:
            # Fetch trending models from HuggingFace API
            url = "https://huggingface.co/api/trending"
            params = {
                "limit": limit,
                "type": "model"
            }

            headers = {
                "User-Agent": "fathom-deck/1.0.0"
            }
            response = client.get(url, params=params, headers=headers, response_type="json")

            # Extract models from response
            models = []
            for item in response.get("recentlyTrending", []):
                model = item.get("repoData", {})

                # Format parameters (e.g., "7B", "13B")
                num_params = model.get("numParameters")
                if num_params:
                    # numParameters is a number
                    if isinstance(num_params, (int, float)):
                        if num_params >= 1e9:
                            num_params = f"{num_params / 1e9:.1f}B"
                        elif num_params >= 1e6:
                            num_params = f"{num_params / 1e6:.1f}M"
                        else:
                            num_params = f"{num_params:,}"

                # Get author info from authorData
                author_data = model.get("authorData", {})
                avatar_url = author_data.get("avatarUrl", "")
                author_fullname = author_data.get("fullname", "")

                # Construct thumbnail URL (same pattern as papers)
                model_id = model["id"]
                thumbnail_url = f"https://cdn-thumbnails.huggingface.co/social-thumbnails/models/{model_id}.png"

                models.append({
                    "id": model_id,
                    "author": model.get("author", model_id.split("/")[0]),
                    "author_fullname": author_fullname,
                    "name": model_id.split("/")[-1],
                    "url": f"https://huggingface.co/{model_id}",
                    "thumbnail": thumbnail_url,
                    "avatar": avatar_url,
                    "downloads": model.get("downloads", 0),
                    "likes": model.get("likes", 0),
                    "pipeline_tag": model.get("pipeline_tag"),
                    "num_parameters": num_params,
                    "last_modified": model.get("lastModified"),
                })

            data = {
                "models": models,
                "limit": limit,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            print(f"✅ Fetched {len(models)} trending HuggingFace models")
            return data

        except Exception as e:
            print(f"❌ Failed to fetch HuggingFace trending models: {e}")
            raise

    def render(self, processed_data: Dict[str, Any]) -> str:
        """Render HuggingFace models widget HTML."""
        models = processed_data["models"]
        limit = processed_data["limit"]
        timestamp_iso = processed_data["fetched_at"]

        return self.render_template(
            "widgets/huggingface_models.html",
            size=self.size,
            models=models,
            limit=limit,
            timestamp_iso=timestamp_iso
        )
