import os

from pymdocx.common.utils import get_doc
from pymdocx.common.revision import get_ins_in_paragraph

DIR_PATH = './../data/test_p'


def test_get_ins_in_paragraph():
    doc_path = os.path.join(DIR_PATH, 'pt0_a.docx')
    doc_obj = get_doc(doc_path)
    tp = doc_obj.paragraphs[1]
    ins_xml = get_ins_in_paragraph(tp)
    print(ins_xml)