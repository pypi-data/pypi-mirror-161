from cubicweb.predicates import is_instance
from cubicweb_oaipmh import MetadataFormat
from cubicweb_oaipmh.entities import (
    OAIPMHRecordAdapter,
    ETypeOAISetSpec,
    RelatedEntityOAISetSpec,
)


OAI_DC = MetadataFormat(
    "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
    "http://www.openarchives.org/OAI/2.0/oai_dc/",
)


class AgentOAIPMHRecordAdapter(OAIPMHRecordAdapter):

    __select__ = OAIPMHRecordAdapter.__select__ & is_instance("Agent")
    metadata_formats = {
        "oai_dc": (OAI_DC, "xmlitem"),
        "eac_cpf": (
            MetadataFormat(
                "http://eac.staatsbibliothek-berlin.de/schema/cpf.xsd",
                "urn:isbn:1-931666-33-4",
            ),
            "eac-cpf",
        ),
    }

    @classmethod
    def set_definition(cls):
        specifier = ETypeOAISetSpec(
            "Agent", identifier_attribute=cls.identifier_attribute
        )
        specifier["kind"] = RelatedEntityOAISetSpec(
            "kind", "AgentKind", "name", description="An agent of kind {0}"
        )
        specifier["involved_in"] = RelatedEntityOAISetSpec(
            "associated_with",
            "Activity",
            "name",
            role="object",
            description="Agent {0}'s activities",
        )
        return specifier


class ActivityOAIPMHRecordAdapter(OAIPMHRecordAdapter):

    __select__ = OAIPMHRecordAdapter.__select__ & is_instance("Activity")
    metadata_formats = {
        "oai_dc": (OAI_DC, "xmlitem"),
    }

    @classmethod
    def set_definition(cls):
        specifier = ETypeOAISetSpec(
            "Activity", identifier_attribute=cls.identifier_attribute
        )
        specifier["associated_with"] = RelatedEntityOAISetSpec(
            "associated_with", "Agent", "name", description="Agent {0}'s activities"
        )
        return specifier


class ThingOAIPMHRecordAdapter(OAIPMHRecordAdapter):

    __select__ = OAIPMHRecordAdapter.__select__ & is_instance("Thing")
    metadata_formats = {
        "oai_dc": (OAI_DC, "xmlitem"),
    }

    # A custom identifier_attribute, distinct from eid, which is the default.
    identifier_attribute = "identifier"

    @classmethod
    def set_definition(cls):
        return ETypeOAISetSpec("Thing", identifier_attribute=cls.identifier_attribute)

    @property
    def deleted(self):
        """Indicate that the entity is to be marked as "deleted" in OAI-PMH
        record.
        """
        return self.entity.deleted
