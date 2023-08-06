from abc import ABC
from typing import List

from fa_common.db.models import DocumentDBTimeStampedModel


class AuditEventBase(DocumentDBTimeStampedModel, ABC):
    """
    Base Model to use for the Audit Event received from
    `_call_home()` in fa_common.licence.utils.

    Requires abstractmethod(s) from DocumentDBTimeStampedModel
    to be implemented (e.g. get_db_collection()).

    Use it as follows:

    .. code-block:: python

        class AuditEvent(AuditEventBase):
            @classmethod
            def get_db_collection(cls) -> str:
                return f"{dm_settings.COLLECTION_PREFIX}auditevents"


        event = AuditEvent()
        event.save()
    """

    product: str = ""
    product_version: str = ""
    licensee: str = ""
    expiry: str = ""
    audit_url: str = ""
    features: List[str] = []
    container_id: str = ""
    username: str = ""
    node: str = ""
    python_version: str = ""
    platform: str = ""
    distro: str = ""
