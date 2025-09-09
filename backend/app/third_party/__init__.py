import os
import sys

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tiktok_live_recorder_path = os.path.join(
    base_path, "third_party", "tiktok_live_recorder", "src"
)

sys.path.append(tiktok_live_recorder_path)

try:
    from core.tiktok_api import TikTokAPI
    from core.tiktok_recorder import TikTokRecorder

    __all__ = ["TikTokRecorder", "TikTokAPI"]

except ImportError as e:
    raise ImportError(f"Failed to import TikTokRecorder from third_party: {e}") from e
