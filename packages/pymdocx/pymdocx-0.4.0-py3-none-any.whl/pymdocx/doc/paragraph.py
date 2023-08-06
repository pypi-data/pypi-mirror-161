import numpy as np
from pprint import pprint

from pymdocx.common.comment import add_p, add_comment_2_p_end, has_comment
from pymdocx.common.revision import add_revision_2_p_end, remove_revision, has_revision
from pymdocx.common.utils import get_element_comment_revision_matrix, \
    _get_actual_p_index


def get_merge_res(m_list):
    # 返回一个字典，每个被批注和修订的段落的索引，以及对应的文档索引
    # key: p index
    # value: 文件 index
    #
    # {0: [0], 1: [1, 0], 2: [0], 8: [0], 10: [0]}
    m_merge = np.array(m_list)
    print('m_merge:')
    print(m_merge)

    print('merge doc modify')
    m_modify = np.max(m_merge, axis=1)
    print(m_modify)

    print('修改')
    m_arg = np.argwhere(m_modify > 0)
    print(m_arg)

    merge_arg_dict = {}
    for doc_index, p_index in m_arg:
        if merge_arg_dict.get(p_index):
            merge_arg_dict.get(p_index).append(doc_index)
        else:
            merge_arg_dict[p_index] = [doc_index]
    return merge_arg_dict


def p_bold_italic(p):
    for r in p.runs:
        r.bold = True
        r.italic = True


class MergePStack:
    def __init__(self, doc_base_p, p_list, doc_base_comments_part_element):
        self.doc_base_p = doc_base_p
        self.p_list = p_list
        self.doc_base_comments_part_element = doc_base_comments_part_element
        self.m_num = len(self.p_list)

        self.merge_blueprint_dict = {}
        self.remove_p_list = []

    def parse_paragraph_differences(self):
        dm_cursor = [-1 for _ in range(self.m_num)]
        for dbpi, dbp in enumerate(self.doc_base_p):
            self.merge_blueprint_dict[dbpi] = {"correspond_p":   [None for _ in range(self.m_num)],
                                               "new_p_pre":          [[] for _ in range(self.m_num)],
                                               "new_p_next":         [[] for _ in range(self.m_num)],
                                               'correspond_p_m': [0 for _ in range(self.m_num)]}
            for dmi, p in enumerate(self.p_list):
                next_p = dm_cursor[dmi] + 1
                for dmpi, dmp in enumerate(p[next_p:], start=next_p):
                    dm_cursor[dmi] = dmpi
                    if dmp.origin_text.strip() == dbp.text.strip():
                        self.merge_blueprint_dict[dbpi]['correspond_p'][dmi] = dmpi
                        if has_comment(dmp) or has_revision(dmp):
                            self.merge_blueprint_dict[dbpi]['correspond_p_m'][dmi] = 1
                        break
                    else:
                        self.merge_blueprint_dict[dbpi]['new_p_pre'][dmi].append(dmpi)
                if dbpi == len(self.doc_base_p) - 1:
                    next_p = dm_cursor[dmi] + 1
                    for dmpi, dmp in enumerate(p[next_p:], start=next_p):
                        self.merge_blueprint_dict[dbpi]['new_p_next'][dmi].append(dmpi)

    def add_p_previous(self, start_p, new_p_index_list, m_d_index):
        for new_p_index in new_p_index_list:
            target_p = self.p_list[m_d_index][new_p_index]
            add_p(start_p, target_p, self.doc_base_comments_part_element, direction='previous')
            start_p = target_p
        return start_p

    def add_p_next(self, end_p, is_m, m_p_index_list, m_d_index, bold_italic=False):
        if is_m:
            for m_p_index in m_p_index_list:
                target_p = self.p_list[m_d_index][m_p_index]
                add_p(end_p, target_p, self.doc_base_comments_part_element)
                end_p = target_p
                if m_d_index > 0 and bold_italic:
                    p_bold_italic(end_p)
        return end_p

    def __call__(self, *args, **kwargs):
        self.parse_paragraph_differences()
        for base_p_index, merge_info in self.merge_blueprint_dict.items():
            start_p = end_p = self.doc_base_p[base_p_index]
            if any(merge_info['correspond_p_m']):
                self.remove_p_list.append(start_p)
            for m_d_index in range(self.m_num):
                start_p = self.add_p_previous(start_p, merge_info['new_p_pre'][m_d_index], m_d_index)
                end_p = self.add_p_next(end_p, merge_info['correspond_p_m'][m_d_index], [merge_info['correspond_p'][m_d_index]], m_d_index, bold_italic=any(merge_info['correspond_p_m'][:m_d_index]))
            for m_d_index in range(self.m_num):
                end_p = self.add_p_next(end_p, merge_info['new_p_next'][m_d_index], merge_info['new_p_next'][m_d_index], m_d_index)
        [rp.delete() for rp in self.remove_p_list]


def merge_paragraph_comment_revision_stack(doc_base_obj, doc_list):
    m = MergePStack(doc_base_obj.paragraphs, [m_doc.paragraphs for m_doc in doc_list], doc_base_obj.comments_part.element)
    m()
    # pprint(m.merge_blueprint_dict)


def merge_paragraph_comment_revision_end(doc_base_obj, doc_list):
    m_list = [get_element_comment_revision_matrix(doc) for doc in doc_list]
    merge_arg_dict = get_merge_res(m_list)

    has_add_mapping = {}
    has_add_p_count = 0
    remove_p_list = []
    for p_index, doc_index_list in merge_arg_dict.items():
        last_p = doc_base_obj.paragraphs[p_index + has_add_p_count]
        remove_p_list.append(last_p)
        for i, doc_index in enumerate(doc_index_list):
            merge_doc_paragraphs = doc_list[doc_index].paragraphs
            has_add_p_count, last_p = _merge_p(i, has_add_mapping, doc_index, p_index, merge_doc_paragraphs, last_p,
                                               doc_base_obj.comments_part.element, has_add_p_count, remove_p_list)

    [rp.delete() for rp in remove_p_list]


def _merge_p(i, has_add_mapping, doc_index, p_index, merge_doc_paragraphs,
             last_p, comments_part_obj, has_add_p_count, remove_p_list):
    if i == 0:
        target_p = merge_doc_paragraphs[_get_actual_p_index(has_add_mapping, doc_index, p_index)]
        if has_comment(target_p):
            add_p(last_p, target_p, comments_part_obj)
            last_p = target_p
            has_add_p_count += 1
        else:
            has_add_mapping[doc_index] -= 1
            remove_p_list.remove(last_p)
        if has_revision(target_p):
            add_revision_2_p_end(last_p, target_p, comments_part_obj)
            remove_revision(last_p)
    else:
        add_comment_2_p_end(last_p, merge_doc_paragraphs[p_index], comments_part_obj)
        add_revision_2_p_end(last_p, merge_doc_paragraphs[p_index], comments_part_obj)
    return has_add_p_count, last_p


merge_paragraph_comment_revision = merge_paragraph_comment_revision_stack