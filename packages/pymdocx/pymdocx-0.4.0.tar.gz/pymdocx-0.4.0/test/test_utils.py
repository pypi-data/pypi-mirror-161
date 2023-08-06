import os

from pymdocx.common.utils import print_doc, get_element_comment_revision_matrix, get_doc

DIR_PATH = './../data/other'


def test_print_doc():
    doc_path = os.path.join(DIR_PATH, 'pt1.docx')
    print_doc(doc_path)


def test_get_element_comment_revision_matrix():
    DIR_PATH = './../data/test_p'
    doc_path_o = os.path.join(DIR_PATH, 'pt0_0.docx')
    doc_path_a = os.path.join(DIR_PATH, 'pt0_a.docx')
    doc_o = get_doc(doc_path_o)
    doc_a = get_doc(doc_path_a)
    print('\n')
    print(get_element_comment_revision_matrix(doc_a))