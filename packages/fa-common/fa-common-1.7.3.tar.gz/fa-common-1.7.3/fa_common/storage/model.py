from typing import Optional

from fa_common import CamelModel, sizeof_fmt


# Shared properties
class File(CamelModel):
    size: Optional[str]  # e.g. '3 KB'
    size_bytes: Optional[int]
    url: Optional[str] = None  # download url
    gs_uri: Optional[str] = None  # GSC Uri
    id: Optional[str]  # id can be path or database id
    dir: bool = False
    path: Optional[str]  # path to current item (e.g. /folder1/someFile.txt)
    # optional (but we are using id as name if name is not present) (e.g. someFile.txt)
    name: str
    content_type: Optional[str]

    def set_size(self, bytes: int):
        self.size = sizeof_fmt(bytes)
        self.size_bytes = bytes
