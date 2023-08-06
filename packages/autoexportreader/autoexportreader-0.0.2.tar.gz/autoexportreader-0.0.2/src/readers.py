import xmltodict

class AutoExportReader:
    def __init__(self):
        self._dialect = None


def parse_xml(xml: str) -> dict:
    return xmltodict.parse(xml)
