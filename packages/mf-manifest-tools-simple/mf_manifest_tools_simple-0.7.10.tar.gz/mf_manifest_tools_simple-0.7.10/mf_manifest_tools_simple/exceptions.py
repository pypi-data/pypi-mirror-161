from typing import List

__all__ = ["NotMFManifest", "ManifestNotValid", "ValidationError"]


class NotMFManifest(Exception):
    def __repr__(self):
        return "Not a MF manifest file"


class ManifestNotValid(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __repr__(self):
        return self._msg


class ValidationError(Exception):
    def __init__(self, msgs: List[str]):
        self.msgs = msgs

    def __repr__(self):
        return "\n".join(self.msgs)
