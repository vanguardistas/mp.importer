import pkgutil
from lxml import etree

# Schema for vanguardistas content format
# validates things like <div><p>Paragraph 1</p><p>Paragraph 2</p></div>

_SCHEMAS = {} # populated lazily at runtime with schema objects

def get_schema(schema='content'):
    s = _SCHEMAS.get(schema)
    if s is None:
        filename = schema + '.rng'
        xml = pkgutil.get_data('mp.importer.schema', filename)
        _SCHEMAS[schema] = etree.RelaxNG(etree.fromstring(xml))
        return get_schema(schema=schema)
    return s
