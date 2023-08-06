import re
import typing

from scdatatools.forge.dftypes import GUID, Record

RECORD_HANDLER = {}


def register_record_handler(dco_type, filename_match=".*"):
    """
    Registers a class handler for the specified `dco_type`.

    Optionally a `filename_match` can be supplied to allow for more specific record handling, e.g. an
    `EntityClassDefinition` type with `spaceships` in the filename could resolve to a :class:`Ship` class instead of
    the base :class:`Entity` class. `filename_match` should be a valid regex.

    This should be used as a decorator for a sub-class of `DataCoreObject`
    """

    def _record_handler_wrapper(handler_class):
        RECORD_HANDLER.setdefault(dco_type, {})[filename_match] = handler_class
        return handler_class

    return _record_handler_wrapper


def dco_from_guid(datacore, guid: typing.Union[str, GUID]) -> "DataCoreObject":
    """
    Takes a :str:`guid` and returns a :class:`DataCoreObject` created from the proper DCO subclass for the record type
    """
    record = datacore.records_by_guid[str(guid)]
    matched = {"": DataCoreObject}

    if record.type in RECORD_HANDLER:
        # find every matching record handler and store them
        for check in sorted(RECORD_HANDLER[record.type], key=len, reverse=True):
            if re.match(check, record.filename):
                matched[check] = RECORD_HANDLER[record.type][check]

    # use the record handler with the most specific (longest) filename check
    return matched[sorted(matched, key=len, reverse=True)[0]](datacore, record)


class DataCoreObject:
    """
    A handy Python representation of a :class:`Record` from a `DataForge`. This base class is subclassed with
    record `type` specific classes that have more convenience functionality for those specific types. The preferred
    method to create a :class:`DataCoreObject` is to the use the :func:`dco_from_guid` function, which will
    automagically use the correct subclass for the :class:`Record` type.
    """

    def __init__(self, datacore, guid_or_dco: typing.Union[str, GUID, Record]):
        self.record = guid_or_dco if isinstance(guid_or_dco, Record) else str(guid_or_dco)
        self._datacore = datacore

    @property
    def guid(self):
        return self.record.id.value

    @property
    def name(self):
        return self.record.name

    @property
    def type(self):
        return self.record.type

    @property
    def filename(self):
        return self.record.filename

    def to_dict(self, depth=100):
        return self.record.dcb.record_to_dict(self.record, depth=depth)

    def to_json(self, depth=100):
        return self.record.dcb.dump_record_json(self.record, depth=depth)

    def to_etree(self, depth=100):
        return self.record.dcb.record_to_etree(self.record, depth=depth)

    def to_xml(self, depth=100):
        return self.record.dcb.dump_record_xml(self.record, depth=depth)
