from typing import Dict, Any


class S3SignedUrl:
    def __init__(self, url: str, fields: Dict[Any, str]):
        self.url = url
        self.fields = fields
