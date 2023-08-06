OAI-PMH server for CubicWeb
===========================

Usage
-----

This cube registers a Pyramid route ``/oai`` against which all OAI-PMH
requests should be performed.

An "admin-email" configuration option should be defined to reference the email
address of an administrator of the OAI-PMH repository.

The implementation relies on `selective harvesting`_ in the sense that only
entity types registering a `set specifier`_ will be visible through OAI-PMH
protocol.

To register an entity type for OAI-PMH harvesting, one should implement
subclasses of ``OAIPMHRecordAdapter`` adapter with a selection context and at
least a concrete definition of ``set_definition`` class method. Other things
like the record view or identifier attribute are configurable through this
adapter.

See ``test/data`` for concrete examples of possible registrations of entity
types as OAI-PMH records.

.. _`selective harvesting`: http://www.openarchives.org/OAI/openarchivesprotocol.html#SelectiveHarvestingandSets
.. _`set specifier`: http://www.openarchives.org/OAI/openarchivesprotocol.html#Set
