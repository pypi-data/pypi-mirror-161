"""cubicweb-oaipmh application package

OAI-PMH server for CubicWeb
"""
import base64
from datetime import datetime
from collections import namedtuple

from isodate import datetime_isoformat
import pytz

from logilab.common.deprecation import callable_deprecated


@callable_deprecated("[oaipmh 0.2] use isodate.datetime_isoformat")
def isodate(date=None):
    if date is None:
        date = utcnow()
    return datetime_isoformat(date)


def utcnow():
    return datetime.now(tz=pytz.utc)


# Model for metadata format of records in the OAI-PMH repository.
MetadataFormat = namedtuple("MetadataFormat", ["schema", "namespace"])


class OAIError(Exception):
    """Error in OAI-PMH request."""

    def __init__(self, errors):
        super(OAIError, self).__init__()
        self.errors = errors


class NoRecordsMatch(OAIError):
    """The combination of the values of the from, until, set and
    metadataPrefix arguments results in an empty list.
    """

    def __init__(self, msg):
        super(NoRecordsMatch, self).__init__({"noRecordsMatch": msg})


class BadResumptionTokenOAIError(OAIError):
    """Token is invalid or failed to decode"""

    def __init__(self, msg):
        super(BadResumptionTokenOAIError, self).__init__({"badResumptionToken": msg})


class ResumptionToken:
    """A resumption token represents the state information needed to continue
    a request which lead to an incomplete (paginated) response.
    """

    __slots__ = (
        "eid",
        "setspec",
        "from_date",
        "until_date",
        "metadata_prefix",
        "complete_list_size",
        "cursor",
    )
    _delimiter = "~"

    def __init__(
        self,
        eid,
        setspec=None,
        from_date=None,
        until_date=None,
        metadata_prefix=None,
        complete_list_size=None,
        cursor=None,
    ):
        self.eid = int(eid) if eid is not None else None
        self.setspec = setspec
        self.from_date = from_date
        self.until_date = until_date
        self.metadata_prefix = metadata_prefix
        self.complete_list_size = (
            int(complete_list_size) if complete_list_size is not None else None
        )
        self.cursor = int(cursor) if cursor is not None else None

    def __repr__(self):
        return "<ResumptionToken {}>".format(
            " ".join("{}={}".format(n, getattr(self, n)) for n in self.__slots__)
        )

    def __eq__(self, other):
        if not isinstance(other, ResumptionToken):
            return False
        return all(
            getattr(self, name) == getattr(other, name) for name in self.__slots__
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.eid is not None

    __nonzero__ = __bool__

    @classmethod
    def parse(cls, token=None):
        """Return a ResumptionToken parsed from `token` string."""
        if token is None:
            return cls(None)
        btoken = token
        if isinstance(token, str):
            btoken = token.encode("ascii")
        try:
            attrs = (
                base64.urlsafe_b64decode(btoken).decode("utf-8").split(cls._delimiter)
            )
        except (TypeError, UnicodeError):
            raise BadResumptionTokenOAIError(
                "The value of the resumptionToken argument failed to " "decode"
            )

        parsed = dict((k, v or None) for k, v in zip(cls.__slots__, attrs))
        return cls(**parsed)

    def encode(self):
        """Return string encoding state of the resumption token."""
        if self.eid is None:
            return None

        def encoded_fields():
            for name in self.__slots__:
                value = getattr(self, name)
                if not value:
                    yield ""
                elif isinstance(value, bytes):
                    yield value.decode("utf-8")
                else:
                    yield str(value)

        state = self._delimiter.join(encoded_fields())
        return base64.urlsafe_b64encode(state.encode("utf-8")).decode("ascii")


def includeme(config):
    config.include(".views")
