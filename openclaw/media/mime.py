"""MIME type detection and media kind classification.

Matches TypeScript src/media/mime.ts and src/media/constants.ts
"""

from __future__ import annotations

from typing import Optional, Literal

MediaKind = Literal["image", "video", "audio", "document"]


def media_kind_from_mime(content_type: Optional[str]) -> Optional[MediaKind]:
    """Determine media kind from MIME type.

    Args:
        content_type: MIME type string

    Returns:
        Media kind or None if unknown
    """
    if not content_type:
        return None

    content_type_lower = content_type.lower().split(";")[0].strip()

    if content_type_lower.startswith("image/"):
        return "image"
    elif content_type_lower.startswith("video/"):
        return "video"
    elif content_type_lower.startswith("audio/"):
        return "audio"
    else:
        return "document"


def is_gif_media(content_type: Optional[str], file_name: Optional[str]) -> bool:
    """Check if media is a GIF animation.

    Args:
        content_type: MIME type
        file_name: File name

    Returns:
        True if GIF
    """
    if content_type:
        content_type_lower = content_type.lower()
        if "image/gif" in content_type_lower:
            return True

    if file_name:
        file_name_lower = file_name.lower()
        if file_name_lower.endswith(".gif"):
            return True

    return False


def is_heic_mime(content_type: Optional[str]) -> bool:
    """Check if MIME type is HEIC/HEIF.
    
    Args:
        content_type: MIME type
        
    Returns:
        True if HEIC/HEIF
    """
    if not content_type:
        return False
    
    content_type_lower = content_type.lower()
    return "image/heic" in content_type_lower or "image/heif" in content_type_lower


def is_heic_file(file_name: Optional[str]) -> bool:
    """Check if filename indicates HEIC/HEIF format.
    
    Args:
        file_name: File name
        
    Returns:
        True if HEIC/HEIF
    """
    if not file_name:
        return False
    
    file_name_lower = file_name.lower()
    return file_name_lower.endswith(".heic") or file_name_lower.endswith(".heif")


__all__ = [
    "MediaKind",
    "media_kind_from_mime",
    "is_gif_media",
    "is_heic_mime",
    "is_heic_file",
]
