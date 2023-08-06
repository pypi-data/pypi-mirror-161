from enum import auto
from enum import Enum
from typing import List
from typing import Optional
from typing import Union

import attr


@attr.s
class Attachment:
    content_type = attr.ib(type=str)
    id = attr.ib(type=str)
    size = attr.ib(type=int)
    stored_filename = attr.ib(type=str)


@attr.s
class Address:
    uuid = attr.ib(type=str)
    number = attr.ib(type=Optional[str], default=None)


@attr.s
class Reaction:
    emoji = attr.ib(type=str)
    target_author = attr.ib(type=Union[str, Address, dict])
    target_sent_timestamp = attr.ib(type=int)
    remove = attr.ib(type=bool, default=False)


@attr.s
class Payment:
    note = attr.ib(type=str)
    receipt = attr.ib(type=str)


@attr.s
class Message:
    username = attr.ib(type=str)
    source = attr.ib(type=Union[str, dict])
    text = attr.ib(type=str)
    source_device = attr.ib(type=int, default=0)
    timestamp = attr.ib(type=int, default=None)
    expiration_secs = attr.ib(type=int, default=0)
    is_receipt = attr.ib(type=bool, default=False)
    attachments = attr.ib(type=list, default=[])
    quote = attr.ib(type=str, default=None)
    group = attr.ib(type=dict, default={})
    group_v2 = attr.ib(type=dict, default={})
    reaction = attr.ib(type=Optional[Reaction], default=None)
    payment = attr.ib(type=Optional[Payment], default=None)


@attr.s
class MemberDetail:
    uuid = attr.ib(type=str)
    role = attr.ib(type=str)
    joined_revision = attr.ib(type=int)


@attr.s
class AccessControl:
    link = attr.ib(type=str)
    attributes = attr.ib(type=str)
    members = attr.ib(type=str)


@attr.s
class Group:
    id = attr.ib(type=str)
    revision = attr.ib(type=int)
    timer = attr.ib(type=int)
    title = attr.ib(type=str, default=None)
    description = attr.ib(type=str, default=None)
    members = attr.ib(type=List[Address], default=[])
    pending_members = attr.ib(type=List[Address], default=[])
    requesting_members = attr.ib(type=List[Address], default=[])
    access_control = attr.ib(type=AccessControl, default=None)
    invite_link = attr.ib(type=str, default=None)
    member_detail = attr.ib(type=List[MemberDetail], default=[])
    pending_member_detail = attr.ib(type=List[MemberDetail], default=[])
    announcements = attr.ib(type=str, default=None)
    avatar = attr.ib(type=str, default=None)


class TrustLevel(Enum):
    UNTRUSTED = auto()
    TRUSTED_UNVERIFIED = auto()
    TRUSTED_VERIFIED = auto()


def _map_trust_level(label: str) -> TrustLevel:
    return TrustLevel[label]


@attr.s
class Identity:
    added = attr.ib(type=int)
    safety_number = attr.ib(type=str)
    qr_code_data = attr.ib(type=str)
    trust_level = attr.ib(type=TrustLevel, converter=_map_trust_level)
