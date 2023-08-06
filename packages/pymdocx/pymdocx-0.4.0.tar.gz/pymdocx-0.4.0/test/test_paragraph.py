import os
from pprint import pprint

from pymdocx.common.utils import get_doc
from pymdocx.doc.paragraph import merge_paragraph_comment_revision, MergePStack

DIR_PATH = './../data/test_p'
OUTPUT_PATH = './../data/output'


def test_parse_paragraph_differences():

    doc_file_path_o = os.path.join(DIR_PATH, "pt0_0.docx")
    doc_file_path_a = os.path.join(DIR_PATH, "pt0_a.docx")
    doc_file_path_c_1 = os.path.join(DIR_PATH, "pt0_c_1.docx")

    doc_o = get_doc(doc_file_path_o)
    doc_a = get_doc(doc_file_path_a)
    doc_c_1 = get_doc(doc_file_path_c_1)
    print(1)
    m = MergePStack(doc_o.paragraphs, [doc_a.paragraphs, doc_c_1.paragraphs], doc_o.comments_part.element)
    m.parse_paragraph_differences()
    pprint(m.merge_blueprint_dict)


def test_mergepend():
    doc_file_path_o = os.path.join(DIR_PATH, "pt0_0.docx")
    doc_file_path_a = os.path.join(DIR_PATH, "pt0_a.docx")
    doc_file_path_c = os.path.join(DIR_PATH, "pt0_c.docx")
    doc_file_path_c_1 = os.path.join(DIR_PATH, "pt0_c_1.docx")
    output_file_path = os.path.join(OUTPUT_PATH, "pt0_new_v2.docx")

    doc_o = get_doc(doc_file_path_o)
    doc_a = get_doc(doc_file_path_a)
    doc_c = get_doc(doc_file_path_c)
    doc_c_1 = get_doc(doc_file_path_c_1)
    print(1)
    m = MergePStack(doc_o.paragraphs, [doc_a.paragraphs, doc_c.paragraphs, doc_c_1.paragraphs], doc_o.comments_part.element)
    m()
    pprint(m.merge_blueprint_dict)
    doc_o.save(output_file_path)


def test_merge_paragraph_comment_revision():

    doc_file_path_o = os.path.join(DIR_PATH, "pt0_0.docx")
    doc_file_path_a = os.path.join(DIR_PATH, "pt0_a.docx")
    doc_file_path_c = os.path.join(DIR_PATH, "pt0_c.docx")
    output_file_path = os.path.join(OUTPUT_PATH, "pt0_new_v2.docx")

    doc_o = get_doc(doc_file_path_o)
    doc_a = get_doc(doc_file_path_a)
    doc_c = get_doc(doc_file_path_c)

    merge_paragraph_comment_revision(doc_o, [doc_a, doc_c])
    doc_o.save(output_file_path)


def test_p_style():
    doc_file_path_c_1 = os.path.join(DIR_PATH, "pt0_c_1.docx")
    doc_c_1 = get_doc(doc_file_path_c_1)
    print(1)
    for r in doc_c_1.paragraphs[2].runs:
        r.bold = True
        r.italic = True