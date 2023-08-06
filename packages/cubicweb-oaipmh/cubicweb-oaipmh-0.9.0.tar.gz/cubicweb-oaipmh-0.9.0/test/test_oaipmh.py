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
"""cubicweb-oaipmh tests"""
from __future__ import print_function

from contextlib import contextmanager
from datetime import date, timedelta
from functools import wraps
import time
import unittest2

from isodate import datetime_isoformat
from dateutil.parser import parse as parse_date
from lxml import etree
import pytz

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.pyramid.test import PyramidCWTest

from cubicweb_oaipmh import utcnow, MetadataFormat, ResumptionToken
from cubicweb_oaipmh.entities import NoRecordsMatch
from cubicweb_oaipmh.views import OAIError, OAIRequest


def b(i):
    return str(i).encode()


def agent(cnx, name=None, kind="person", **kwargs):
    return cnx.create_entity(
        "Agent", name=name, kind=cnx.create_entity("AgentKind", name=kind), **kwargs
    )


def xmlview_snippet(cnx, eid):
    """Return a snippet of xmlitem view for entity with `eid`."""
    entity = cnx.entity_from_eid(eid)
    return (
        '<%s eid="%s" cwuri="%s"' % (entity.cw_etype, entity.eid, entity.cwuri)
    ).encode("utf-8")


@contextmanager
def temporary_list_max_size(config, value):
    optname = "list-max-size"
    old_value = config["list-max-size"]
    config.global_set_option(optname, value)
    try:
        yield
    finally:
        config.global_set_option(optname, old_value)


class ResumptionTokenTC(unittest2.TestCase):
    def test_none(self):
        token = ResumptionToken.parse(None)
        self.assertIsNone(token.eid)
        self.assertFalse(token)
        self.assertIsNone(token.encode())
        self.assertIsNone(token.cursor)

    def test_unicode(self):
        """Make sure we can parse unicode string."""
        token = ResumptionToken(1, metadata_prefix="oai_dc")
        utoken = token.encode()
        assert ResumptionToken.parse(utoken) == token

    def test_roundtrip(self):
        attrs = ("eid", "setspec", "from_date", "until_date", "metadata_prefix")
        for tokeninfo in [
            (1,),  # All none.
            (6, "pif", "2016-07-31T22:00:00Z", "2016-09-14T13:39:03Z", "oai_dc"),
            (8, "paf", None, "2016-09-14T13:39:03Z", "myfmt"),
        ]:
            params = dict(zip(attrs, tokeninfo))
            token = ResumptionToken(**params)
            encoded = token.encode()
            parsed = ResumptionToken.parse(encoded)
            assert parsed == token


class OAITestMixin:
    def oai_component(self, cnx):
        """Return the "oai" component"""
        return self.vreg["components"].select("oai", cnx)


class OAIComponentTC(CubicWebTC, OAITestMixin):
    def test_registered(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            setspecs = oai.__setspecs__
            self.assertCountEqual(list(setspecs.keys()), ["agent", "activity", "thing"])
            self.assertCountEqual(
                list(setspecs["agent"].keys()), ["kind", "involved_in"]
            )
            self.assertCountEqual(
                list(setspecs["activity"].keys()), ["associated_with"]
            )
            self.assertCountEqual(list(setspecs["thing"].keys()), [])

    def test_match(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            with self.assertRaises(NoRecordsMatch) as cm:
                oai.match("cwuser")
            self.assertEqual(
                cm.exception.errors, {"noRecordsMatch": "no setspec matching cwuser"}
            )

    def test_setspecs(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity("Activity", name="hacking")
            bob = agent(cnx, "bob")
            cnx.commit()
            expected = (
                "agent",
                "agent:kind:person",
                "agent:involved_in:hacking",
                "activity",
                "activity:associated_with:%s" % bob.name,
                "thing",
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)

    def test_setspecs_no_identifier_attribute(self):
        """An entity without an "identifier_attribute" set should not yield a
        setspec for related entities.
        """
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx)
            cnx.commit()
            expected = (
                "agent",
                "agent:kind:person",
                "activity",
                "thing",
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)

    def test_metadata_formats(self):
        with self.admin_access.cnx() as cnx:
            oai = self.oai_component(cnx)
            formats = dict(oai.metadata_formats())
            expected = {
                "oai_dc": MetadataFormat(
                    "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
                    "http://www.openarchives.org/OAI/2.0/oai_dc/",
                ),
                "eac_cpf": MetadataFormat(
                    "http://eac.staatsbibliothek-berlin.de/schema/cpf.xsd",
                    "urn:isbn:1-931666-33-4",
                ),
            }
            self.assertEqual(formats, expected)


class OAIRequestTC(CubicWebTC):
    def test_rset(self):
        """Test `rset` function for exceptions."""
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, "bob")
            agent(cnx, "New York City", kind="authority")
            cnx.commit()
        with self.admin_access.web_request() as req:
            for setspec, msg in [
                ("agent:zen", "only handling one or three levels set specifiers"),
                (
                    "agent:kind:family",
                    (
                        "The combination of the values of the from, until, and "
                        "set arguments results in an empty list."
                    ),
                ),
                ("scregneugneu", "no setspec matching scregneugneu"),
            ]:
                oairq = OAIRequest("http://testing.fr", setspec=setspec)
                with self.assertRaises(OAIError) as cm:
                    oairq.rset(req)
                self.assertEqual(cm.exception.errors, {"noRecordsMatch": msg})

    def test_rset_token(self):
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, "bob")
            simpsons = agent(cnx, "The Simpson", kind="family")
            cnx.commit()

        def oairq(**kwargs):
            return OAIRequest("http://testing.fr", setspec="agent", **kwargs)

        with self.admin_access.web_request() as req:
            with temporary_list_max_size(self.config, 1):
                rset, next_eid = oairq().rset(req)
                self.assertEqual(len(rset), 1)
                self.assertEqual(next_eid, str(simpsons.eid))
                token = ResumptionToken(next_eid).encode()
                rset, next_eid = oairq(resumption_token=token).rset(req)
                self.assertEqual(len(rset), 1)
                self.assertIsNone(next_eid)
                res = ResumptionToken.parse(token)
                self.assertEqual(res.complete_list_size, None)
                self.assertEqual(res.cursor, None)
            # All results are returned, the resumptionToken is None.
            rset, next_eid = oairq().rset(req)
            self.assertEqual(len(rset), 2)
            self.assertIsNone(next_eid)
            # and this, even if the user specified an input token.
            token = ResumptionToken(1).encode()
            rset, next_eid = oairq(resumption_token=token).rset(req)
            self.assertEqual(len(rset), 2)
            self.assertIsNone(next_eid)
            res = ResumptionToken.parse(token)
            self.assertEqual(res.complete_list_size, None)
            self.assertEqual(res.cursor, None)

    def test_rset_token_with_until(self):
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, "bob")
            simpsons = agent(cnx, "The Simpson", kind="family")
            cnx.commit()

        def oairq_func(**kwargs):
            return OAIRequest("http://testing.fr", setspec="agent", **kwargs)

        with self.admin_access.web_request() as req:
            with temporary_list_max_size(self.config, 1):
                today = date.today()
                until_date = today.strftime("%Y-%m-%d")
                from_date = (today - timedelta(7)).strftime("%Y-%m-%d")
                oairq = oairq_func(from_date=from_date, until_date=until_date)
                rset, next_eid = oairq.rset(req)
                self.assertEqual(len(rset), 1)
                self.assertEqual(next_eid, str(simpsons.eid))
                complete_list_size = oairq.complete_list_size(req)
                token = oairq.create_resumption_token(
                    next_eid, complete_list_size, 1
                ).encode()
                res = ResumptionToken.parse(token)
                rset, next_eid = oairq_func(resumption_token=token).rset(req)
                self.assertEqual(len(rset), 1)
                self.assertEqual(res.complete_list_size, 2)
                self.assertEqual(res.from_date, from_date)
                self.assertEqual(res.until_date, until_date)
                self.assertEqual(res.cursor, 1)

    def test_init_request_with_token(self):
        setspec = "agent"
        token = ResumptionToken(1, metadata_prefix="oai_dc", setspec=setspec)
        oairq = OAIRequest(
            "http://testing.fr", verb="ListIdentifiers", resumption_token=token.encode()
        )
        self.assertEqual(oairq.setspec, setspec)

    def test_to_xml(self):
        oairq = OAIRequest(
            "http://testing.fr",
            verb="GetRecord",
            identifier="abc",
            metadata_prefix="oai_dc",
        )
        xml = oairq.to_xml()
        expected = {
            "verb": "GetRecord",
            "metadataPrefix": "oai_dc",
            "identifier": "abc",
        }
        self.assertEqual(xml.attrib, expected)

    def test_to_xml_with_dates(self):
        datestr = "2016-09-23T12:34:44Z"
        oairq = OAIRequest(
            "http://testing.fr",
            verb="ListIdentifiers",
            from_date=datestr,
            until_date=None,
        )
        xml = oairq.to_xml()
        expected = {
            "verb": "ListIdentifiers",
            "from": "2016-09-23T12:34:44Z",
        }
        self.assertEqual(xml.attrib, expected)

    def test_to_xml_with_token(self):
        token = ResumptionToken(7)
        oairq = OAIRequest(
            "http://testing.fr", verb="ListIdentifiers", resumption_token=token.encode()
        )
        xml = oairq.to_xml()
        expected = {
            "verb": "ListIdentifiers",
            "resumptionToken": token.encode(),
        }
        self.assertEqual(xml.attrib, expected)

    def test_to_xml_errors(self):
        oairq = OAIRequest(
            "http://testing.fr", verb="ListIdentifiers", metadata_prefix="qwerty"
        )
        xml = oairq.to_xml(errors="yes")
        self.assertEqual(xml.attrib, {})


def no_validate_xml(method):
    """Disable XML schema validation, often because the underlying metadata
    part of the response (RDF, XSD) is not validable (or we don't know how to
    do it).
    """

    @wraps(method)
    def wrapper(self):
        self._validate_xml = False
        self._debug_xml = True
        return method(self)

    return wrapper


def xmlpp(string):
    """Parse and pretty-print XML data from `string`."""
    print(etree.tostring(etree.fromstring(string), pretty_print=True))


class OAIPMHViewsTC(PyramidCWTest, OAITestMixin):
    settings = {
        # to get clean traceback in tests (instead of in an html error page)
        "cubicweb.bwcompat": False,
        # avoid noise in test output (UserWarning: !! WARNING WARNING !! you
        # should stop this instance)
        "cubicweb.session.secret": "x",
        "cubicweb.auth.authtkt.session.secret": "x",
        "cubicweb.auth.authtkt.persistent.secret": "x",
    }

    _validate_xml = True
    _debug_xml = True

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningfull line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        root = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(root):
            print(xml_data)
        xmlschema.assertValid(root)

    def oai_request(self, req, **formparams):
        response = self.webapp.get("/oai", formparams)
        self.assertEqual(response.headers["Content-Type"], "text/xml; charset=UTF-8")
        if self._validate_xml:
            self.assertXmlValid(
                response.body, self.datapath("OAI-PMH.xsd"), debug=self._debug_xml
            )
        return response.body

    def test_xml_attributes_and_namespaces(self):
        """Check XML attributes and namespace declaration of the response."""
        with self.admin_access.web_request() as req:
            # simple request, generating an error but enough to get a properly
            # formatter response.
            result = self.oai_request(req)
            xml = etree.fromstring(result)
            nsmap = {
                None: "http://www.openarchives.org/OAI/2.0/",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
            self.assertEqual(xml.nsmap, nsmap)
            attrib = {
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation": " ".join(
                    [
                        "http://www.openarchives.org/OAI/2.0/",
                        "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd",
                    ]
                ),
            }
            self.assertEqual(xml.attrib, attrib)

    def test_responsedate(self):
        """Check <responseDate>"""
        with self.admin_access.web_request() as req:
            # Simple request, generating an error but enough to get a properly
            # formatter response.
            now = utcnow()
            result = self.oai_request(req)
        # Check tzinfo abbreviation is present (Z for UTC).
        pattern = "<responseDate>{0}</responseDate>".format(
            datetime_isoformat(now)
        ).encode("utf-8")
        self.assertIn(pattern, result)

    def test_noverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req)
        self.assertIn(b"<request>https://localhost:80/oai</request>", result)
        self.assertIn(b'<error code="badVerb">no verb specified</error', result)

    def test_badverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="coucou")
        self.assertIn(b"<request>https://localhost:80/oai</request>", result)
        self.assertIn(b'<error code="badVerb">illegal verb "coucou"</error>', result)

    def test_identify(self):
        self.config.global_set_option("admin-email", "oai-admin@example.org")
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="Identify")
            cwversion = req.find("CWProperty", pkey="system.version.cubicweb").one()
            earliest_datestamp = datetime_isoformat(cwversion.creation_date).encode(
                "ascii"
            )
        self.assertIn(b"<repositoryName>unset title</repositoryName>", result)
        self.assertIn(b"<baseURL>https://localhost:80/oai</baseURL>", result)
        self.assertIn(b"<protocolVersion>2.0</protocolVersion>", result)
        self.assertIn(b"<adminEmail>oai-admin@example.org</adminEmail>", result)
        self.assertIn(
            b"<earliestDatestamp>%s</earliestDatestamp>" % earliest_datestamp, result
        )
        self.assertIn(b"<deletedRecord>no", result)
        self.assertIn(b"<granularity>YYYY-MM-DDThh:mm:ssZ", result)
        with self.admin_access.cnx() as cnx:
            entity = cnx.create_entity("Thing", identifier="123")
            cnx.commit()
            earliest_datestamp = datetime_isoformat(entity.creation_date).encode(
                "ascii"
            )
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="Identify")
        self.assertIn(
            b"<earliestDatestamp>%s</earliestDatestamp>" % earliest_datestamp, result
        )

    def test_identify_badargument(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="Identify", set="plouf")
        self.assertIn(
            b'<error code="badArgument">Identify accepts no argument</error', result
        )

    def test_listmetadaformats(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListMetadataFormats")
        self.assertIn(b"<metadataPrefix>oai_dc</metadataPrefix>", result)
        self.assertIn(b"<metadataPrefix>eac_cpf</metadataPrefix>", result)

    def test_listmetadaformats_iddoesnotexist(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListMetadataFormats", identifier="-123"
            )
        self.assertIn(b'<error code="idDoesNotExist">', result)

    def test_listmetadaformats_by_identifier(self):
        with self.admin_access.cnx() as cnx:
            agent_eid = agent(cnx, "bob").eid
            cnx.create_entity("Thing", identifier="123")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListMetadataFormats", identifier=str(agent_eid)
            )
        self.assertIn(b"<metadataPrefix>oai_dc</metadataPrefix>", result)
        self.assertIn(b"<metadataPrefix>eac_cpf</metadataPrefix>", result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListMetadataFormats", identifier="123")
        self.assertIn(b"<metadataPrefix>oai_dc</metadataPrefix>", result)
        self.assertNotIn(b"<metadataPrefix>eac_cpf</metadataPrefix>", result)

    def test_listsets(self):
        with self.admin_access.cnx() as cnx:
            agent(cnx, "bob")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListSets")
        self.assertIn(
            b'<request verb="ListSets">https://localhost:80/oai</request>', result
        )
        self.assertIn(b"<setSpec>agent</setSpec>", result)
        self.assertIn(b"<setSpec>activity</setSpec>", result)
        self.assertIn(
            (
                b"<setSpec>agent:kind:person</setSpec>"
                b"<setName>An agent of kind person</setName>"
            ),
            result,
        )
        self.assertIn(
            (
                b"<setSpec>activity:associated_with:bob</setSpec>"
                b"<setName>Agent bob's activities</setName>"
            ),
            result,
        )

    def test_listidentifiers_no_metadataprefix(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListIdentifiers")
        self.assertIn(b"<request>https://localhost:80/oai</request>", result)
        self.assertIn(
            (
                b'<error code="badArgument">'
                b'ListIdentifiers verb requires a "metadataPrefix" restriction'
                b"</error>"
            ),
            result,
        )

    def test_listidentifiers_setspect_bad_metadataprefix(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListIdentifiers", set="agent", metadataPrefix="unexisting"
            )
        self.assertIn(b"<request", result)
        self.assertIn(
            (
                b'<error code="cannotDisseminateFormat">'
                b"metadata prefix unexisting not supported for set agent"
                b"</error>"
            ),
            result,
        )

    def test_resumptiontoken_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            bob = agent(cnx, "bob")
            cnx.commit()

        def check_request(expected_identifiers, token=None):
            with self.admin_access.web_request() as req:
                kwargs = {"resumptionToken": token} if token is not None else {}
                result = self.oai_request(
                    req,
                    verb="ListIdentifiers",
                    set="agent",
                    metadataPrefix="oai_dc",
                    **kwargs
                )
                # Ensure there are as many <identifier> tag than expected items.
                self.assertEqual(
                    result.count(b"<identifier>"), len(expected_identifiers)
                )
                for identifier in expected_identifiers:
                    self.assertIn(b"<identifier>%d</identifier>" % identifier, result)
                return result

        result = check_request([alice.eid, bob.eid])
        # All results returned, no resumptionToken is request -> no
        # resumptionToken in response.
        self.assertNotIn(b"resumptionToken", result)
        with temporary_list_max_size(self.config, 1):
            result = check_request([alice.eid])
            root = etree.fromstring(result)
            token = root.find(".//{%s}resumptionToken" % root.nsmap[None])
            date = parse_date(token.attrib["expirationDate"])
            self.assertLess(utcnow() + timedelta(hours=1) - date, timedelta(seconds=1))
            self.assertEqual(token.attrib["completeListSize"], "2")
            self.assertEqual(token.attrib["cursor"], "0")
            expected_token = ResumptionToken(
                bob.eid,
                setspec="agent",
                metadata_prefix="oai_dc",
                complete_list_size=2,
                cursor=1,
            )
            self.assertEqual(token.text, expected_token.encode())
            result = check_request([bob.eid], token=expected_token.encode())
            # No more results -> empty resumptionToken
            # (only attributes completeListSize and cursor)
            self.assertIn(b'<resumptionToken completeListSize="2" cursor="1"/>', result)
            # Empty result, probably a badResumptionToken.
            new_token = ResumptionToken(bob.eid + 1)
            result = check_request([], token=new_token.encode())
            self.assertIn(b"badResumptionToken", result)

    def test_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice").eid
            newyork = agent(cnx, "New York City", "authority").eid
            cnx.create_entity("Thing", identifier="007")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListIdentifiers", metadataPrefix="oai_dc"
            )
            self.assertIn(b"<identifier>%d</identifier>" % newyork, result)
            self.assertIn(b"<identifier>%d</identifier>" % alice, result)
            self.assertIn(b"<identifier>007</identifier>", result)
            self.assertEqual(result.count(b"<identifier>"), 3)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListIdentifiers", metadataPrefix="eac_cpf"
            )
            self.assertIn(b"<identifier>%d</identifier>" % newyork, result)
            self.assertIn(b"<identifier>%d</identifier>" % alice, result)
            self.assertNotIn(b"<identifier>007</identifier>", result)
            self.assertEqual(result.count(b"<identifier>"), 2)

    def test_listidentifiers_setspec(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice").eid
            newyork = agent(cnx, "New York City", "authority").eid
            cnx.create_entity("Thing", identifier="007")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListIdentifiers", set="agent", metadataPrefix="oai_dc"
            )
            self.assertIn(b"<identifier>%d</identifier>" % newyork, result)
            self.assertIn(b"<identifier>%d</identifier>" % alice, result)
            self.assertEqual(result.count(b"<identifier>"), 2)
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                metadataPrefix="oai_dc",
                set="agent:kind:person",
            )
            self.assertIn(b"<identifier>%d</identifier>" % alice, result)
            self.assertNotIn(b"<identifier>%d</identifier>" % newyork, result)
            result = self.oai_request(
                req, verb="ListIdentifiers", set="activity", metadataPrefix="oai_dc"
            )
            self.assertIn(b'<error code="noRecordsMatch">', result)
            result = self.oai_request(
                req, verb="ListIdentifiers", set="thing", metadataPrefix="oai_dc"
            )
            self.assertIn(b"<identifier>007</identifier>", result)

    def test_listidentifiers_deleted(self):
        """Check <header> element (status attribute, datestamp) for deleted
        records in ListIdentifiers response.
        """
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Thing", identifier="a")
            deleted = cnx.create_entity("Thing", identifier="b")
            date_before = deleted.modification_date.replace(tzinfo=pytz.utc)
            cnx.commit()
            time.sleep(1)
            deleted.cw_set(deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListIdentifiers", set="thing", metadataPrefix="oai_dc"
            )
            self.assertIn(b"<identifier>a</identifier>", result)
            self.assertIn(b'<header status="deleted">', result)
            root = etree.fromstring(result)
            ns = root.nsmap[None]
            # only one <header status="..."> element
            (header,) = root.findall(".//{%s}header[@status]" % ns)
            datestamp = header.find("{%s}datestamp" % ns).text
            date = parse_date(datestamp)
            self.assertGreater(date, date_before.replace(microsecond=0))

    def test_listrecords_noargument(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListRecords")
        self.assertIn(b"<request>https://localhost:80/oai</request>", result)
        expected = (
            b'<error code="badArgument">'
            b'ListRecords verb requires a "metadataPrefix" restriction'
            b"</error>"
        )
        self.assertIn(expected, result)

    @no_validate_xml
    def test_listrecords(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            newyork = agent(cnx, "New York", kind="authority")
            cnx.create_entity("Thing", identifier="a")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListRecords", metadataPrefix="oai_dc")
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertIn(b(newyork.eid), result)
            self.assertIn(b"<identifier>a</identifier>", result)

    @no_validate_xml
    def test_listrecords_resumptiontoken(self):
        """ListRecords without set restriction, checking resumptionToken."""
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            newyork = agent(cnx, "New York", kind="authority")
            cnx.create_entity("Thing", identifier="a")
            cnx.commit()
        expected_token = ResumptionToken(
            newyork.eid, metadata_prefix="oai_dc", complete_list_size=3, cursor=1
        )
        with self.admin_access.web_request() as req:
            with temporary_list_max_size(self.config, 1):
                result = self.oai_request(
                    req, verb="ListRecords", metadataPrefix="oai_dc"
                )
                self.assertIn(xmlview_snippet(req, alice.eid), result)
                self.assertNotIn(b"<identifier>%d</identifier>" % newyork.eid, result)
                self.assertNotIn(b"<identifier>a</identifier>", result)
                self.assertIn(
                    "{0}</resumptionToken>".format(expected_token.encode()).encode(
                        "ascii"
                    ),
                    result,
                )
                root = etree.fromstring(result)
                token = root.find(".//{%s}resumptionToken" % root.nsmap[None])
                date = parse_date(token.attrib["expirationDate"])
                self.assertLess(
                    utcnow() + timedelta(hours=1) - date, timedelta(seconds=1)
                )
                self.assertEqual(token.attrib["completeListSize"], "3")
                self.assertEqual(token.attrib["cursor"], "0")
            result = self.oai_request(
                req,
                verb="ListRecords",
                metadataPrefix="oai_dc",
                resumptionToken=expected_token.encode(),
            )  # NB: temporary list max size is no longer 1 for the next test
            self.assertIn(b"<identifier>%d</identifier>" % newyork.eid, result)
            self.assertIn(b"<identifier>a</identifier>", result)
            # The response completes a prior response, we get a resumptionToken
            # with only completeListSize and cursor
            self.assertIn(b'<resumptionToken completeListSize="3" cursor="1"/>', result)

    @no_validate_xml
    def test_listrecords_resumptiontoken_no_metadataprefix(self):
        """ListRecords with resumptionToken but *no metadataPrefix*."""
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            newyork = agent(cnx, "New York", kind="authority")
            cnx.create_entity("Thing", identifier="a")
            cnx.commit()
        # The expected ResumptionToken built from request parameters.
        token = ResumptionToken(
            newyork.eid, metadata_prefix="oai_dc", complete_list_size=3, cursor=1
        )
        with self.admin_access.web_request() as req:
            with temporary_list_max_size(self.config, 1):
                # First request includes metadataPrefix.
                result = self.oai_request(
                    req, verb="ListRecords", metadataPrefix="oai_dc"
                )
                self.assertIn(xmlview_snippet(req, alice.eid), result)
                self.assertNotIn(b"<identifier>%d</identifier>" % newyork.eid, result)
                self.assertNotIn(b"<identifier>a</identifier>", result)
                self.assertIn(
                    "{0}</resumptionToken>".format(token.encode()).encode("ascii"),
                    result,
                )

                root = etree.fromstring(result)
                token_xml = root.find(".//{%s}resumptionToken" % root.nsmap[None])
                date = parse_date(token_xml.attrib["expirationDate"])
                self.assertLess(
                    utcnow() + timedelta(hours=1) - date, timedelta(seconds=1)
                )
                self.assertEqual(token_xml.attrib["completeListSize"], "3")
                self.assertEqual(token_xml.attrib["cursor"], "0")
            # Second request has no metadataPrefix but has resumptionToken,
            # from which metadataPrefix will be fetched.
            result = self.oai_request(
                req, verb="ListRecords", resumptionToken=token.encode()
            )
            self.assertIn(b"<identifier>%d</identifier>" % newyork.eid, result)
            self.assertIn(b"<identifier>a</identifier>", result)
            # The response completes a prior response, we get a resumptionToken
            # with only completeListSize and cursor
            self.assertIn(b'<resumptionToken completeListSize="3" cursor="1"/>', result)

    def test_resumptiontoken_error(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                resumptionToken="junk",
                until="2000-02-05",
            )
            self.assertIn(
                b'<error code="badResumptionToken">The value '
                b"of the resumptionToken argument is invalid or expired.",
                result,
            )

    @no_validate_xml
    def test_listrecords_filter_metadata_prefix(self):
        """Make sure records that do not match requests metadataPrefix are not
        listed.
        """
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            cnx.create_entity("Thing", identifier="a")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListRecords", metadataPrefix="eac_cpf")
            self.assertIn(b"<identifier>%d</identifier>" % alice.eid, result)
            self.assertNotIn(b"<identifier>a</identifier>", result)

        # Make sure records not matching metadataPrefix have no effect on
        # result set (eg. do not modify resumptionToken).
        with self.admin_access.cnx() as cnx:
            bob = agent(cnx, "bob")
            cnx.commit()
        with temporary_list_max_size(self.config, 2):
            with self.admin_access.web_request() as req:
                result = self.oai_request(
                    req, verb="ListRecords", metadataPrefix="eac_cpf"
                )
                self.assertIn(b"<identifier>%d</identifier>" % alice.eid, result)
                self.assertIn(b"<identifier>%d</identifier>" % bob.eid, result)
                self.assertNotIn(b"resumptionToken", result)

    @no_validate_xml
    def test_listrecords_filter_metadata_prefix_no_result(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Thing", identifier="a")
            cnx.create_entity("Thing", identifier="b")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="ListRecords", metadataPrefix="eac_cpf")
            self.assertIn(b"noRecordsMatch", result)
            self.assertNotIn(b"<identifier>", result)

    @no_validate_xml
    def test_listrecords_with_set(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            newyork = agent(cnx, "New York", kind="authority")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListRecords", set="agent", metadataPrefix="oai_dc"
            )
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertIn(b(newyork.eid), result)
            result = self.oai_request(
                req,
                verb="ListRecords",
                set="agent:kind:person",
                metadataPrefix="oai_dc",
            )
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertNotIn(b(newyork.eid), result)

    @no_validate_xml
    def test_listrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in ListRecords response.
        """
        with self.admin_access.cnx() as cnx:
            thing = cnx.create_entity("Thing", identifier="a")
            deleted = cnx.create_entity("Thing", identifier="b", deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="ListRecords", set="thing", metadataPrefix="oai_dc"
            )
            self.assertNotIn(xmlview_snippet(req, deleted.eid), result)
            # but record present
            self.assertIn(b"<identifier>b</identifier>", result)
            # not-deleted thing is present with metadata.
            self.assertIn(xmlview_snippet(req, thing.eid), result)

    def test_getrecord_missing_identifier(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="GetRecord", metadataPrefix="oai_dc")
        self.assertIn(
            (
                b'<error code="badArgument">GetRecord verb requires '
                b'"identifier" restriction'
            ),
            result,
        )

    def test_getrecord_missing_metadataprefix(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb="GetRecord", identifier="doesnotmatter")
        self.assertIn(
            (
                b'<error code="badArgument">GetRecord verb requires '
                b'"metadataPrefix" restriction'
            ),
            result,
        )

    def test_getrecord_bad_identifier(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier='invalid"id', metadataPrefix="oai_dc"
            )
        self.assertIn(
            (
                b"<error code=\"badArgument\">'identifier' doesn't match "
                b"required syntax."
            ),
            result,
        )

    @no_validate_xml
    def test_getrecord(self):
        with self.admin_access.repo_cnx() as cnx:
            thing = cnx.create_entity("Thing", identifier="aaa")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier="aaa", metadataPrefix="oai_dc"
            )
            self.assertIn(xmlview_snippet(req, thing.eid), result)

    @no_validate_xml
    def test_getrecord_agent(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = agent(cnx, "bob")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier=str(bob.eid), metadataPrefix="oai_dc"
            )
        self.assertIn(b'<metadata><Agent eid="%d"' % bob.eid, result)
        self.assertIn(b"bob", result)

    @no_validate_xml
    def test_getrecord_agent_other_prefix(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = agent(cnx, "bob")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier=str(bob.eid), metadataPrefix="eac_cpf"
            )
        expected = (
            "<control><recordId/>{0}</control></eac-cpf>".format(bob.eid)
        ).encode("utf-8")
        self.assertIn(expected, result)

    def test_getrecord_unsupported_metadataprefix(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity("Thing", identifier="aaa")
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier="aaa", metadataPrefix="ahah"
            )
        expected = (
            b'<error code="noRecordsMatch">unsupported metadata prefix "ahah"</error>'
        )
        self.assertIn(expected, result)

    def test_getrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in GetRecord response.
        """
        with self.admin_access.cnx() as cnx:
            cnx.create_entity("Thing", identifier="d", deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier="d", metadataPrefix="oai_dc"
            )
            # record is present
            self.assertIn(b"<identifier>d</identifier>", result)
            # but not data
            self.assertNotIn(b"<metadata>", result)
            self.assertNotIn(b"<Thing", result)

    def test_getrecord_inexistant(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req, verb="GetRecord", identifier="z", metadataPrefix="doesnotmatter"
            )
            self.assertIn(b"idDoesNotExist", result)

    def test_from_until_error(self):
        with self.admin_access.web_request() as req:
            dates = {
                "from": date(2013, 1, 2).isoformat(),
                "until": date(2011, 1, 2).isoformat(),
            }
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **dates
            )
            self.assertIn(b'<error code="badArgument">the from argument', result)

    def test_from_until_dateformat_error(self):
        with self.admin_access.web_request() as req:
            dates = {"from": "junk"}
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **dates
            )
            self.assertIn(
                b"<error code=\"badArgument\">'from' argument must be "
                b"a UTCdatetime value",
                result,
            )
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                until="junk",
            )
            self.assertIn(
                b"<error code=\"badArgument\">'until' argument must be "
                b"a UTCdatetime value",
                result,
            )

    def test_from_until_granularity_error(self):
        with self.admin_access.web_request() as req:
            dates = {"from": "2002-02-05", "until": "2002-02-06T05:35:00Z"}
            result = self.oai_request(
                req, verb="ListRecord", set="agent", metadataPrefix="oai_dc", **dates
            )
            self.assertIn(
                b'<error code="badArgument">from and until dates have '
                b"different granularity",
                result,
            )

    def test_from_until_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            bob = agent(cnx, "bob")
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            alice_date = cnx.entity_from_eid(alice.eid).modification_date
            bob_date = alice_date + timedelta(seconds=2)
            cnx.entity_from_eid(bob.eid).cw_set(modification_date=bob_date)
            cnx.commit()
        in_between_date = datetime_isoformat(alice_date + timedelta(seconds=1))
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **{"from": in_between_date}
            )
            self.assertIn(b(bob.eid), result)
            self.assertNotIn(b(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **{"until": in_between_date}
            )
            self.assertNotIn(b(bob.eid), result)
            self.assertIn(b(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **{"from": "1970-12-1", "until": "2099-01-02"}
            )
            self.assertIn(b(bob.eid), result)
            self.assertIn(b(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **{"until": "1970-12-31"}
            )
            self.assertIn(b'<error code="noRecordsMatch">The combi', result)

    def test_from_until_granularity_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            bob = agent(cnx, "bob")
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            alice_date = cnx.entity_from_eid(alice.eid).modification_date
            bob_date = alice_date + timedelta(seconds=2)
            cnx.entity_from_eid(bob.eid).cw_set(modification_date=bob_date)
            cnx.commit()

        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **{"from": alice_date, "until": alice_date}
            )
            self.assertIn(b(alice.eid), result)
            self.assertNotIn(b(bob.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent",
                metadataPrefix="oai_dc",
                **{"from": alice_date.date(), "until": alice_date.date()}
            )
            self.assertIn(b(alice.eid), result)
            self.assertIn(b(bob.eid), result)

    def test_from_until_listidentifiers_setspec(self):
        """Check from/until restriction with a multi-level setspec
        `agent:kind:family`
        """
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, "alice")
            simpsons = agent(cnx, "The Simpson", "family")
            adams = agent(cnx, "Adams family", "family")
            cnx.commit()
        with self.admin_access.cnx() as cnx:
            simpsons_date = cnx.entity_from_eid(simpsons.eid).modification_date
            adams = cnx.entity_from_eid(adams.eid)
            adams_date = simpsons_date + timedelta(seconds=2)
            adams.cw_set(modification_date=adams_date)
            cnx.commit()
        in_between_date = datetime_isoformat(simpsons_date + timedelta(seconds=1))
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent:kind:family",
                metadataPrefix="oai_dc",
                **{"from": in_between_date}
            )
            self.assertNotIn(b(simpsons.eid), result)
            self.assertIn(b(adams.eid), result)
            self.assertNotIn(b(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent:kind:family",
                metadataPrefix="oai_dc",
                **{"until": in_between_date}
            )
            self.assertIn(b(simpsons.eid), result)
            self.assertNotIn(b(adams.eid), result)
            self.assertNotIn(b(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent:kind:family",
                metadataPrefix="oai_dc",
                **{"from": "1970-12-1", "until": "2099-01-02"}
            )
            self.assertIn(b(simpsons.eid), result)
            self.assertIn(b(adams.eid), result)
            self.assertNotIn(b(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent:kind:family",
                metadataPrefix="oai_dc",
                **{"until": "1970-12-31"}
            )
            self.assertIn(b'<error code="noRecordsMatch">The combi', result)

    def test_related_setspec_role_object(self):
        with self.admin_access.cnx() as cnx:
            bob = agent(cnx, "bob")
            cnx.create_entity("Activity", name="hacking", associated_with=bob)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(
                req,
                verb="ListIdentifiers",
                set="agent:involved_in:hacking",
                metadataPrefix="oai_dc",
            )
            self.assertIn(b"<identifier>%d</identifier>" % bob.eid, result)


if __name__ == "__main__":
    import unittest

    unittest.main()
