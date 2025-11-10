from dataclasses import dataclass


@dataclass
class ImageEntity:
    image_id: str
    uploader_id: str
    filename: str
    mime_type: str
    size_bytes: int
    width: int
    height: int
    checksum: str
    status: str
