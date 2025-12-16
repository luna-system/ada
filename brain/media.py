"""
ListenBrainz integration for fetching and formatting user's current/recent media.
"""
import os
import time
import requests
import datetime
from typing import Optional, Dict, Any

# Cache for ListenBrainz data (to avoid hammering the API)
_LISTENBRAINZ_CACHE = {"ts": 0.0, "data": None}

def fetch_listenbrainz(user: Optional[str], token: Optional[str]) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetch current playing or recent listen from ListenBrainz.
    
    Returns: (data_dict, error_message)
    - If successful: data_dict contains {source, status, artist, track, release, listened_at}
    - If error: error_message is non-None string
    """
    if not user:
        return None, "LISTENBRAINZ_USER not configured"
    
    now = time.time()
    cached = _LISTENBRAINZ_CACHE.get("data")
    # 5-second cache to avoid repeated API calls
    if cached and (now - _LISTENBRAINZ_CACHE.get("ts", 0) < 5):
        return cached, None

    headers = {"User-Agent": "ada-v1/brain"}
    if token:
        headers["Authorization"] = f"Token {token}"

    def normalize(meta, status, listened_at=None):
        if not meta:
            return None
        return {
            "source": "listenbrainz",
            "status": status,
            "artist": (meta or {}).get("artist_name"),
            "track": (meta or {}).get("track_name"),
            "release": (meta or {}).get("release_name"),
            "listened_at": listened_at,
        }

    base = "https://api.listenbrainz.org/1/user/" + user
    
    # Try /playing-now first (requires token for accurate "now playing" data)
    if token:
        try:
            r = requests.get(base + "/playing-now", headers=headers, timeout=5)
            if r.status_code == 200:
                payload = r.json() or {}
                pn = (payload.get("playing_now") or {})
                if pn:
                    meta = pn.get("track_metadata")
                    if meta:
                        info = normalize(meta, status="playing", listened_at=pn.get("listened_at"))
                        _LISTENBRAINZ_CACHE.update({"ts": now, "data": info})
                        return info, None
        except Exception:
            pass  # Fall through to /listens
    
    # Fall back to recent listens (works without token, but lags behind current playback)
    try:
        r = requests.get(base + "/listens", headers=headers, params={"count": 1}, timeout=5)
        if r.status_code == 200:
            payload = r.json() or {}
            listens = (payload.get("payload") or {}).get("listens") or []
            if listens:
                first = listens[0]
                meta = (first.get("track_metadata") or {})
                listened_at = (first.get("listened_at") or first.get("played_at"))
                
                # Check if the track is recent enough to be considered "now playing"
                # Consider it "playing" if listened within the last 5 minutes
                status = "recent"
                if listened_at:
                    try:
                        track_age = now - int(listened_at)
                        if track_age < 300:  # 5 minutes
                            status = "playing"
                    except (ValueError, TypeError):
                        pass
                
                info = normalize(meta, status=status, listened_at=listened_at)
                _LISTENBRAINZ_CACHE.update({"ts": now, "data": info})
                return info, None
    except Exception as e:
        return None, str(e)

    # Return idle state if no data found
    info = {"source": "listenbrainz", "status": "idle"}
    _LISTENBRAINZ_CACHE.update({"ts": now, "data": info})
    return info, None


def format_media_for_prompt(media_info: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Format ListenBrainz media info as natural language for the LLM prompt.
    Returns None if media_info is empty or incomplete.
    """
    if not media_info or not isinstance(media_info, dict):
        return None
    
    status = media_info.get("status")
    if status == "playing":
        artist = media_info.get("artist", "Unknown Artist")
        track = media_info.get("track", "Unknown Track")
        return f"luna has chosen to share that she is currently listening to the song {track} by artist {artist}."
    elif status == "recent":
        artist = media_info.get("artist", "Unknown Artist")
        track = media_info.get("track", "Unknown Track")
        listened_at = media_info.get("listened_at")
        time_str = ""
        if listened_at:
            try:
                from datetime import datetime as dt
                ldt = dt.fromisoformat(listened_at.replace("Z", "+00:00"))
                now_dt = dt.now(ldt.tzinfo)
                delta = now_dt - ldt
                days = delta.days
                hours = delta.seconds // 3600
                if days > 0:
                    time_str = f"{days} day{'s' if days != 1 else ''} ago"
                elif hours > 0:
                    time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                else:
                    time_str = "a few minutes ago"
            except Exception:
                time_str = "recently"
        else:
            time_str = "recently"
        return f"luna has chosen to share that the last song she listened to was {track} by artist {artist} {time_str}."
    
    return None
