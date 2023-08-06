# copyright 2016-2022 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-oaipmh pyramid views for OAI-PMH export

Set hierarchy specification
---------------------------

Sets_ are optional construct for selective harvesting. The scheme used to
define the syntax of sets is usually specific to the community using the
OAI-PMH exchange protocol. This OAI-PMH implementation exposes the following
set hierarchy.

- The first level of hierarchy refers to the entity type to perform the
  selective request on, e.g. for a `ListIdentifiers` verb:

      <baseurl>/oai?verb=ListIdentifiers&set=agent

  would return the identifiers of entities of type Agent found in the repository.

- The second level of hierarchy refers to a filtering criterion on selected
  entity type, usually an attribute with respect to the application schema,
  and is tight to a value of this criterion (attribute) to filter entities on.
  For instance:

      <baseurl>/oai?verb=ListIdentifiers&set=agent:kind:person

  would return the identifiers of entities of type Agent of kind 'person'.

.. _Set:
.. _Sets: http://www.openarchives.org/OAI/openarchivesprotocol.html#Set
"""

from datetime import datetime, timedelta
import re

from isodate import datetime_isoformat
import dateutil.parser
import logging
from lxml import etree
from lxml.builder import E, ElementMaker
import pytz

from pyramid.response import Response
from pyramid.view import view_config

from cubicweb_oaipmh import (
    utcnow,
    OAIError,
    ResumptionToken,
    BadResumptionTokenOAIError,
)


# This is not a full identifier constraint.
# For more details see http://www.openarchives.org/OAI/openarchivesprotocol.html#UniqueIdentifier
IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9:/\-\._]+$", re.IGNORECASE)

# This is intended to differentiate date from datetime.
# This is far from optimal but the other found solutions were uglier:
# https://stackoverflow.com/questions/8434854/parsing-a-date-in-python-without-using-a-default
DATE_NOT_DATETIME = re.compile(r"^\d{1,4}.\d{1,2}.\d{1,4}$")

LOGGER = logging.getLogger("cubicweb_oaipmh")


class UTCParseError(Exception):
    """Raised when the input value could not be parsed"""

    def __init__(self, msg=None):
        super(UTCParseError, self).__init__({"UTCParseError": msg})


def utcparse(timestr):
    """Parse a date/time string as an UTC datetime."""
    try:
        date = dateutil.parser.parse(timestr)
    except ValueError:
        raise UTCParseError()
    granularity = "day" if DATE_NOT_DATETIME.match(timestr) else "time"
    if date.tzinfo is None:
        if "T" in timestr:
            raise UTCParseError("cannot parse a date with time but no timezone")
        else:
            # No time, assume UTC.
            return date.replace(tzinfo=pytz.utc), granularity
    else:
        # Convert to UTC.
        return date.astimezone(pytz.utc), granularity


def filter_none(mapping):
    """Return a dict from `mapping` with None values filtered out."""
    out = {}
    for key, val in mapping.items():
        if val is not None:
            out[key] = val
    return out


def oai_records(rset):
    """Yield OAIRecord items from a result set."""
    for entity in rset.entities():
        record = entity.cw_adapt_to("IOAIPMHRecord")
        if not record:
            continue
        yield OAIRecord(record)


def xml_metadataformat(prefix, mformat):
    """Return the XML representation of a MetadataFormat object."""
    return E.metadataFormat(
        E.metadataPrefix(prefix),
        E.schema(mformat.schema),
        E.metadataNamespace(mformat.namespace),
    )


class IdDoesNotExist(OAIError):
    """The value of the identifier argument is unknown or illegal in this
    repository.
    """

    def __init__(self, identifier):
        msg = "no entity with OAI identifier {0} in repository".format(identifier)
        errors = {"idDoesNotExist": msg}
        super(IdDoesNotExist, self).__init__(errors)


class OAIRequest:
    """Represent an OAI-PMH request."""

    @classmethod
    def from_request(cls, request):
        baseurl = request.route_url("oai")
        return cls(
            baseurl,
            setspec=request.params.get("set"),
            verb=request.params.get("verb"),
            identifier=request.params.get("identifier"),
            from_date=request.params.get("from"),
            until_date=request.params.get("until"),
            resumption_token=request.params.get("resumptionToken"),
            metadata_prefix=request.params.get("metadataPrefix"),
        )

    def __init__(
        self,
        baseurl,
        verb=None,
        setspec=None,
        identifier=None,
        from_date=None,
        until_date=None,
        resumption_token=None,
        metadata_prefix=None,
    ):
        self.baseurl = baseurl
        self.verb = verb
        self.identifier = identifier
        self.errors = {}
        try:
            self.resumption_token = ResumptionToken.parse(resumption_token)
        except BadResumptionTokenOAIError:
            msg = "The value of the resumptionToken argument is invalid or expired."
            self.errors["badResumptionToken"] = msg
            return
        # Parse "from" and "until" dates, which are, by specification
        # expressed in UTC.
        from_date = self.resumption_token.from_date or from_date
        from_granularity = None
        until_granularity = None
        parsed_from_date = None
        parsed_until_date = None
        try:
            if from_date is not None:
                date_part = "from"
                parsed_from_date, from_granularity = utcparse(from_date)
            until_date = self.resumption_token.until_date or until_date
            if until_date is not None:
                date_part = "until"
                parsed_until_date, until_granularity = utcparse(until_date)
        except UTCParseError:
            msg = "'{}' argument must be a UTCdatetime value".format(date_part)
            self.errors["badArgument"] = msg
            return
        if parsed_from_date is not None and parsed_until_date is not None:
            if until_granularity != from_granularity:
                msg = "from and until dates have different granularity"
                self.errors["badArgument"] = msg
            elif parsed_from_date > parsed_until_date:
                msg = (
                    "the from argument must be less than or equal to the until argument"
                )
                self.errors["badArgument"] = msg
        self.granularity = until_granularity
        self.setspec = self.resumption_token.setspec or setspec
        self.from_date = parsed_from_date
        self.until_date = parsed_until_date
        self.orig_from_date = from_date
        self.orig_until_date = until_date
        self.metadata_prefix = self.resumption_token.metadata_prefix or metadata_prefix

    def __repr__(self):
        return etree.tostring(self.to_xml())

    def complete_list_size(self, cnx):
        """
        Return the number total of selected entities
        """
        if self.resumption_token:
            return self.resumption_token.complete_list_size
        dates = {"from_date": self.from_date, "until_date": self.until_date}
        oai = cnx.vreg["components"].select("oai", cnx)
        rset = oai.build_matches_rset(
            self.setspec,
            metadata_prefix=self.metadata_prefix,
            granularity=self.granularity,
            **dates,
        )
        return rset[0][0] if rset else 0

    def rset_from_identifier(self, cnx):
        """Return a ResultSet corresponding to request identifier."""
        oai = cnx.vreg["components"].select("oai", cnx)
        return oai.match_identifier(self.identifier)

    def rset(self, cnx):
        """Return a result set with a resumptionToken information from OAI-PMH
        request by using any provided set specifier, from/until dates and
        previous token.
        """
        dates = {"from_date": self.from_date, "until_date": self.until_date}
        oai = cnx.vreg["components"].select("oai", cnx)
        rset, next_eid = oai.match(
            self.setspec,
            metadata_prefix=self.metadata_prefix,
            from_eid=self.resumption_token.eid,
            granularity=self.granularity,
            **dates,
        )
        if not rset:
            LOGGER.error(
                f"BadResumptionTokenOAIError: found no results for {rset.printable_rql()} "
                f"while expected"
            )

            if self.resumption_token:
                raise BadResumptionTokenOAIError(
                    "The value of the resumptionToken "
                    "argument is invalid or expired."
                )
            raise OAIError(
                {
                    "noRecordsMatch": (
                        "The combination of the values of the "
                        "from, until, and set arguments results "
                        "in an empty list."
                    )
                }
            )
        return rset, next_eid

    def create_resumption_token(self, eid, complete_list_size, cursor):
        """Create a new resumptionToken"""
        return ResumptionToken(
            eid,
            self.setspec,
            self.orig_from_date,
            self.orig_until_date,
            self.metadata_prefix,
            complete_list_size,
            cursor,
        )

    def new_token(self, eid, complete_list_size, max_result_size=0):
        """Return a resumptionToken XML element or None built from request
        parameters and the `eid` of the next entity to return upon
        continuation of the request.

        * return a resumptionToken with completeListSize and cursor and a value
        if there are more result to be fetched;
        * return an empty resumptionToken with completeListSize and cursor
        if this response completes and the request contains a resumptionToken;
        * None otherwise.
        """
        original_cursor = self.resumption_token.cursor if self.resumption_token else 0
        if eid is not None:
            if self.resumption_token:
                # Reuse previous token, just updating "eid" and "cursor" field.
                token = self.resumption_token
                token.eid = eid
                token.cursor = (token.cursor or 0) + max_result_size
            else:
                token = self.create_resumption_token(
                    eid, complete_list_size, max_result_size
                )
            expire = datetime_isoformat(datetime.now(pytz.utc) + timedelta(hours=1))
            return E.resumptionToken(
                token.encode(),
                expirationDate=expire,
                completeListSize=str(complete_list_size),
                cursor=str(original_cursor),
            )
        elif self.resumption_token:
            return E.resumptionToken(
                completeListSize=str(complete_list_size),
                cursor=str(original_cursor),
            )

    def to_xml(self, errors=None):
        if not errors:
            # In cases where the request that generated this response resulted
            # in a badVerb or badArgument error condition, the repository must
            # return the base URL of the protocol request only. Attributes
            # must not be provided in these cases.
            attributes = {
                "verb": self.verb,
                "identifier": self.identifier,
                "set": self.setspec,
            }
            if self.from_date:
                attributes["from"] = datetime_isoformat(self.from_date)
            if self.until_date:
                attributes["until"] = datetime_isoformat(self.until_date)
            if self.metadata_prefix:
                attributes["metadataPrefix"] = self.metadata_prefix
            if self.resumption_token:
                attributes["resumptionToken"] = self.resumption_token.encode()
        else:
            attributes = {}
        attributes = filter_none(attributes)
        return E.request(self.baseurl, **attributes)


class OAIResponse:
    """Represent an OAI-PMH response."""

    def __init__(self, oai_request):
        self.oai_request = oai_request

    @staticmethod
    def _build_errors(errors):
        """Return a list of <error> tag from `errors` dict."""
        return [E.error(msg, code=code) for code, msg in errors.items()]

    def body(self, content=None, errors=None):
        """Return a list of body items of the OAI-PMH response."""

        def check_content(content):
            assert (
                content is not None
            ), "unexpected empty content while no error got reported"

        oai_request = self.oai_request
        if errors:
            return self._build_errors(errors)
        check_content(content)
        try:
            return [E(oai_request.verb, *content)]
        except OAIError as exc:
            return self._build_errors(exc.errors)
        except TypeError:
            # Usually something wrong with `content` generator, try to unpack
            # it to get a meaningful error.
            content = list(content)
            check_content(content)
            return [E(oai_request.verb, *content)]

    def to_xml(self, content=None, errors=()):
        date = E.responseDate(datetime_isoformat(utcnow()))
        request = self.oai_request.to_xml(errors)
        body_elems = self.body(content, errors=errors)
        nsmap = {
            None: "http://www.openarchives.org/OAI/2.0/",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        maker = ElementMaker(nsmap=nsmap)
        attributes = {
            "{%s}schemaLocation"
            % nsmap["xsi"]: " ".join(
                [
                    "http://www.openarchives.org/OAI/2.0/",
                    "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd",
                ]
            )
        }
        return maker("OAI-PMH", date, request, *body_elems, **attributes)


class OAIRecord:
    """Represent an OAI record built from an entity adapted as IOAIPMHRecord."""

    def __init__(self, record):
        self.record = record

    def header(self, prefix):
        """The <header> part of an OAI-PMH record.

        See http://www.openarchives.org/OAI/openarchivesprotocol.html#header
        for a description of elements of a "header".
        """
        if prefix not in self.record.metadata_formats:
            raise OAIError(
                {"noRecordsMatch": 'unsupported metadata prefix "{0}"'.format(prefix)}
            )

        tags = []

        for tag in ("identifier", "datestamp"):
            value = getattr(self.record, tag)
            if value:
                tags.append(E(tag, value))

        set_definition = self.record.set_definition()

        if set_definition is not None:
            for set_spec in set_definition.set_list_for_record(self.record):
                tags.append(E("setSpec", set_spec))

        attrs = {}
        if self.record.deleted:
            attrs["status"] = "deleted"
        return E.header(*tags, **attrs)

    def metadata(self, prefix):
        """The <metadata> part of an OAI-PMH record."""
        if self.record.deleted:
            return None
        metadata = self.record.metadata(prefix)
        if metadata:
            return E.metadata(etree.XML(metadata))
        return None

    def metadata_formats(self):
        for prefix, (fmt, _) in self.record.metadata_formats.items():
            yield xml_metadataformat(prefix, fmt)

    def to_xml(self, prefix):
        """Return the <record> XML element."""
        elems = [self.header(prefix)]
        metadata = self.metadata(prefix)
        if metadata is not None:  # deleted record
            elems.append(metadata)
        return E.record(*elems)


class OAIView:
    """Base class for any OAI view, subclasses should either implement
    `errors` or `verb_content` methods.
    """

    @staticmethod
    def verb_content():
        return

    @staticmethod
    def errors():
        """Return the errors of the OAI-PMH request."""
        return

    def __init__(self, request):
        self.request = request
        self._cw = request.cw_request
        self.oai_request = OAIRequest.from_request(request)

    def __call__(self):
        encoding = self._cw.encoding
        assert encoding == "UTF-8", "unexpected encoding {0}".format(encoding)
        content = ('<?xml version="1.0" encoding="%s"?>\n' % encoding).encode("utf-8")
        oai_response = OAIResponse(self.oai_request)
        # combine errors coming from view selection with those of request
        # processing.
        errors = self.errors() or {}
        verb_content = self.verb_content() if not errors else None
        errors.update(self.oai_request.errors)
        response_elem = oai_response.to_xml(verb_content, errors=errors)
        content += etree.tostring(response_elem, encoding="utf-8")
        return Response(content, content_type="text/xml")


@view_config(route_name="oai")
class OAIErrorView(OAIView):
    """Error view for OAI-PMH request with no or bad "verb" specified.

    `verb` request parameter is necessary in our implementation.
    """

    def errors(self):
        verb = self.request.params.get("verb")
        if verb:
            return {"badVerb": 'illegal verb "{0}"'.format(self.oai_request.verb)}
        else:
            return {"badVerb": "no verb specified"}


@view_config(route_name="oai", verb="Identify")
class OAIIdentifyView(OAIView):
    """View handling verb="Identify" requests."""

    def errors(self):
        if set(self.request.params) - set(["verb", "vid"]):
            return {"badArgument": "Identify accepts no argument"}

    def verb_content(self):
        oai = self._cw.vreg["components"].select("oai", self._cw)
        yield E("repositoryName", self._cw.property_value("ui.site-title"))
        yield E("baseURL", self.request.route_url("oai"))
        yield E("protocolVersion", "2.0")
        try:
            admin_email = self._cw.vreg.config["admin-email"]
        except KeyError:
            pass
        else:
            yield E("adminEmail", admin_email)
        yield E("earliestDatestamp", datetime_isoformat(oai.earliest_datestamp()))
        yield E("deletedRecord", oai.deleted_handling)
        yield E("granularity", "YYYY-MM-DDThh:mm:ssZ")


@view_config(route_name="oai", verb="ListMetadataFormats")
class OAIListMetadatFormatsByIdentifierView(OAIView):
    """View handling verb="ListMetadataFormats" requests."""

    def verb_content(self):
        identifier = self.request.params.get("identifier")
        if identifier:
            rset = self.oai_request.rset_from_identifier(self._cw)
            if not rset:
                raise IdDoesNotExist(self.oai_request.identifier)
            for record in oai_records(rset):
                for fmt in record.metadata_formats():
                    yield fmt
        else:
            oai = self._cw.vreg["components"].select("oai", self._cw)
            for prefix, fmt in oai.metadata_formats():
                yield xml_metadataformat(prefix, fmt)


@view_config(route_name="oai", verb="ListSets")
class OAIListSetsView(OAIView):
    """View handling verb="ListSets" requests."""

    @staticmethod
    def build_set(spec, name=""):
        """Return a "set" element"""
        return E("set", E.setSpec(spec), E.setName(name))

    def verb_content(self):
        oai = self._cw.vreg["components"].select("oai", self._cw)
        for spec, description in oai.setspecs():
            yield self.build_set(spec, name=self._cw._(description))


@view_config(route_name="oai", verb="ListIdentifiers")
class OAIListIdentifiersWithSetView(OAIView):
    """View handling verb="ListIdentifiers" requests with "set" selection."""

    def errors(self):
        if "metadataPrefix" not in self.request.params:
            return {
                "badArgument": (
                    'ListIdentifiers verb requires a "metadataPrefix" ' "restriction"
                )
            }

    def verb_content(self):
        rset, eid = self.oai_request.rset(self._cw)
        for record in oai_records(rset):
            yield record.header(self.oai_request.metadata_prefix)
        complete_list_size = self.oai_request.complete_list_size(self._cw)
        new_token = self.oai_request.new_token(
            eid,
            complete_list_size=complete_list_size,
            max_result_size=self._cw.vreg.config["list-max-size"],
        )
        if new_token is not None:
            yield new_token


@view_config(route_name="oai", verb="ListRecords")
class OAIListRecordsView(OAIView):
    """View handling verb="ListRecords"."""

    def errors(self):
        params = set(self.request.params) & set({"metadataPrefix", "resumptionToken"})
        if not params:
            return {
                "badArgument": (
                    'ListRecords verb requires a "metadataPrefix" ' "restriction"
                )
            }

    def verb_content(self):
        rset, eid = self.oai_request.rset(self._cw)
        for record in oai_records(rset):
            yield record.to_xml(self.oai_request.metadata_prefix)
        complete_list_size = self.oai_request.complete_list_size(self._cw)
        new_token = self.oai_request.new_token(
            eid,
            complete_list_size=complete_list_size,
            max_result_size=self._cw.vreg.config["list-max-size"],
        )
        if new_token is not None:
            yield new_token


@view_config(route_name="oai", verb="GetRecord")
class OAIGetRecordView(OAIView):
    """View handling verb="GetRecord" with proper arguments."""

    def errors(self):
        params = set(self.request.params) & set({"identifier", "metadataPrefix"})
        if not params:
            return {
                "badArgument": (
                    'GetRecord verb requires "identifier" and '
                    '"metadataPrefix" arguments'
                )
            }
        elif params == set({"identifier"}):
            return {
                "badArgument": 'GetRecord verb requires "metadataPrefix" restriction'
            }
        elif params == set({"metadataPrefix"}):
            return {"badArgument": 'GetRecord verb requires "identifier" restriction'}
        identifier = self.request.params.get("identifier")
        if not IDENTIFIER_PATTERN.match(identifier):
            return {"badArgument": ("'identifier' doesn't match required " "syntax.")}

    def verb_content(self):
        rset = self.oai_request.rset_from_identifier(self._cw)
        for record in oai_records(rset):
            if record is not None:
                yield record.to_xml(self.oai_request.metadata_prefix)
                break
        else:
            raise IdDoesNotExist(self.oai_request.identifier)


class VerbPredicate:
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "verb = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        return request.params.get("verb") == self.val


def includeme(config):
    config.add_route("oai", "/oai")
    config.add_view_predicate("verb", VerbPredicate)
    config.scan(__name__)
