from lxml import etree
from lxml.builder import ElementMaker

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


class EACCPFView(EntityView):
    __regid__ = "eac-cpf"
    __select__ = is_instance("Agent")
    content_type = "text/xml"
    binary = True
    namespaces = {
        None: "urn:isbn:1-931666-33-4",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xlink": "http://www.w3.org/1999/xlink",
    }

    def entity_call(self, entity):
        E = ElementMaker(namespace=None, nsmap=self.namespaces)
        elem = E("eac-cpf", E.control(E.recordId, str(entity.eid)))
        self.w(etree.tostring(elem, encoding="utf-8"))
