"""Helper script with all Regexes."""
from __future__ import annotations

import re

from .enums import MessageTypes

# pylint: disable=invalid-name

# sample OH: SR0001L0001    006969XX    [ID00000000]
# sample other OH: SR0001L0001    006969XX    \x00\x00\x00\x00
oh_regex = r"""
^S
(?:R)(?P<receiver>(?<=R)(?:\d{4}))
(?:L)(?P<line>(?<=L)(?:\d{4}))
\s+(?P<account>\w{6})XX\s+
(\[(?P<id>\w+)\])?
(\x00+)?$
"""
OH_MATCHER = re.compile(oh_regex, re.X)

main_regex = r"""
(?P<crc>[A-Fa-f0-9]{4})
(?P<length>[A-Fa-f0-9]{4})\"
(?P<encrypted_flag>[*])?
(?P<message_type>SIA-DCS|ADM-CID|NULL)\"
(?P<sequence>[0-9]{4})
(?P<receiver>R[A-Fa-f0-9]{1,6})?
(?P<line>L[A-Fa-f0-9]{1,6})
[#]?(?P<account>[A-Fa-f0-9]{3,16})?
[\[]
(?P<rest>.*)
"""
MAIN_MATCHER = re.compile(main_regex, re.X)

# Content matcher, with shared pre and post expressions.
xdata_ts_regex = r"""
[\]]
(?:\[(?:(?<=\[)(?P<xdata>.*)(?=\]))\])?
(?:_(?<=_)(?P<timestamp>[0-9:,-]*)?)?$
"""

sia_content_regex = (
    r"""
[#]?(?P<account>[A-Fa-f0-9]{3,16})?
[|]?
[N]?
(?:ti)?(?:(?<=ti)(?P<ti>\d{2}:\d{2}))?\/?
(?:id)?(?:(?<=id)(?P<id>\d*))?\/?
(?:ri)?(?:(?<=ri)(?P<ri>\d*))?\/?
(?P<code>[a-zA-Z]{2})?
(?P<message>.[^\[\]]*)?
"""
    + xdata_ts_regex
)

adm_content_regex = (
    r"""
[#]?(?P<account>[A-F0-9]{3,16})?
[|]?
(?P<event_qualifier>\d{1})
(?P<event_type>\d{3})
\s
(?P<partition>\d{2})
\s
(?P<ri>\d{3})
"""
    + xdata_ts_regex
)

encr_content_regex = r"""
(?:[^\|\[\]]*)[|]?
"""

SIA_CONTENT_MATCHER = re.compile(sia_content_regex, re.X)
ADM_CONTENT_MATCHER = re.compile(adm_content_regex, re.X)
ENCR_SIA_CONTENT_MATCHER = re.compile(encr_content_regex + sia_content_regex, re.X)
ENCR_ADM_CONTENT_MATCHER = re.compile(encr_content_regex + adm_content_regex, re.X)


def _get_matcher(
    message_type: MessageTypes | str, encrypted: bool = False
) -> re.Pattern:
    """Extract the content using the different regexes."""
    if message_type == MessageTypes.ADMCID:
        return ENCR_ADM_CONTENT_MATCHER if encrypted else ADM_CONTENT_MATCHER
    return ENCR_SIA_CONTENT_MATCHER if encrypted else SIA_CONTENT_MATCHER
