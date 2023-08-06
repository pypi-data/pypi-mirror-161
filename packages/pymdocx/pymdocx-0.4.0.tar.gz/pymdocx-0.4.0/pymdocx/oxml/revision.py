"""
Custom element classes related to the revisions part
"""
from docx.oxml.simpletypes import ST_DecimalNumber, ST_String
from docx.oxml.xmlchemy import BaseOxmlElement, RequiredAttribute, ZeroOrMore


class CT_Rev(BaseOxmlElement):
    """
    ``<w:ins>`` and ``<w:del>`` element, a container for Comment properties
    """
    _id = RequiredAttribute('w:id', ST_DecimalNumber)
    date = RequiredAttribute('w:date', ST_String)
    author = RequiredAttribute('w:author', ST_String)

    r = ZeroOrMore('w:r')


class CT_Deltext(BaseOxmlElement):
    """
    ``<w:del>`` element, a container for Comment properties
    """