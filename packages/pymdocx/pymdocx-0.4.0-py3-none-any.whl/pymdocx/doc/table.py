from pprint import pprint

from pymdocx.common.comment import has_comment
from pymdocx.common.revision import has_revision
from pymdocx.doc.paragraph import _merge_p, MergePStack


def detect_comment_revision_in_table(doc_obj_list):
    """
    {
    table_index_1: {cell_index: {p_index: [doc_index_list]}}
    }
    """
    m = {}
    for doc_index, doc_obj in enumerate(doc_obj_list):
        for t_index, t in enumerate(doc_obj.tables):
            for c_index, c in enumerate(t._cells):
                for p_index, p in enumerate(c.paragraphs):
                    if has_comment(p) or has_revision(p):
                        if t_index not in m:
                            m[t_index] = {c_index: {p_index: [doc_index]}}
                        elif c_index in m[t_index] and p_index not in m[t_index][c_index]:
                            m[t_index][c_index][p_index] = [doc_index]
                        elif c_index in m[t_index] and p_index in m[t_index][c_index]:
                            m[t_index][c_index][p_index].append(doc_index)
                        elif c_index not in m[t_index]:
                            m[t_index][c_index] = {p_index: [doc_index]}
    return m


class MergeTStack:
    def __init__(self, doc_base_t, t_list, doc_base_comments_part_element):
        self.doc_base_t = doc_base_t
        self.t_list = t_list
        self.doc_base_comments_part_element = doc_base_comments_part_element
        self.m_num = len(self.t_list)
        self.merge_cell_dict = {}

    def detect_merge_cell_in_table(self):
        """
        {
        table_index: {cell_index: need_merge_bool}}
        }
        """
        for t_index, t in enumerate(self.doc_base_t):
            for c_index, c in enumerate(t._cells):
                need_merge_bool = False
                for m_t in self.t_list:
                    if len(m_t[t_index]._cells[c_index].paragraphs) > len(c.paragraphs):
                        need_merge_bool = True
                        break
                    p_break = 0
                    for p in m_t[t_index]._cells[c_index].paragraphs:
                        if has_comment(p) or has_revision(p):
                            need_merge_bool = True
                            p_break = 1
                            break
                    if p_break:
                        break
                if need_merge_bool:
                    if t_index not in self.merge_cell_dict:
                        self.merge_cell_dict[t_index] = {c_index: 1}
                    elif c_index not in self.merge_cell_dict[t_index]:
                        self.merge_cell_dict[t_index][c_index] = 1

    def __call__(self, *args, **kwargs):
        self.detect_merge_cell_in_table()
        for t_index, m_c_dict in self.merge_cell_dict.items():
            for c_index in m_c_dict.keys():
                MergePStack(self.doc_base_t[t_index]._cells[c_index].paragraphs,
                            [t[t_index]._cells[c_index].paragraphs for t in self.t_list], self.doc_base_comments_part_element)()


def merge_table_comment_revision_stack(doc_base_obj, merge_doc_list):
    mergetstack = MergeTStack(doc_base_obj.tables, [mdoc.tables for mdoc in merge_doc_list], doc_base_obj.comments_part.element)
    mergetstack()
    # pprint(mergetstack.merge_cell_dict)


def merge_table_comment_revision_end(doc_base_obj, merge_doc_list):
    detect_dict = detect_comment_revision_in_table(merge_doc_list)
    for t_index, t_v in detect_dict.items():
        for c_index, c_v in t_v.items():
            has_add_p_count = 0
            remove_p_list = []
            has_add_mapping = {}
            for p_index, doc_index_list in c_v.items():
                base_p = last_p = doc_base_obj.tables[t_index]._cells[c_index].paragraphs[p_index + has_add_p_count]
                remove_p_list.append(last_p)
                for i, doc_index in enumerate(doc_index_list):
                    merge_doc_paragraphs = merge_doc_list[doc_index].tables[t_index]._cells[c_index].paragraphs
                    if merge_doc_paragraphs:
                        has_add_p_count, last_p = _merge_p(i, has_add_mapping, doc_index, p_index, merge_doc_paragraphs, last_p,
                                               doc_base_obj.comments_part.element, has_add_p_count, remove_p_list)
                    else:
                        if base_p in remove_p_list:
                            remove_p_list.remove(base_p)
            [rp.delete() for rp in remove_p_list]


merge_table_comment_revision = merge_table_comment_revision_stack