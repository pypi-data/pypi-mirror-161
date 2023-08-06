from docx.oxml import register_element_cls, CT_R
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from docx.text.run import Run

from pymdocx.oxml.revision import CT_Rev, CT_Deltext
from pymdocx.text.revision import Revision

register_element_cls('w:ins', CT_Rev)
register_element_cls('w:del', CT_Rev)
register_element_cls('w:delText', CT_Deltext)


def monkey_patch_run():
    def del_text(self):
        del_text_list = self._element.findall(qn('w:delText'))
        text = ''
        for dt in del_text_list:
            text += dt.text
        return text
    property_ = property(del_text, None, None)
    setattr(Run, 'del_text', property_)


monkey_patch_run()


def monkey_patch_paragraph():
    def revisions(self):
        rev_ins = self._element.findall(qn('w:ins'))
        rev_del = self._element.findall(qn('w:del'))
        return [Revision(r, self) for r in rev_ins + rev_del]
    setattr(Paragraph, 'revisions', property(revisions, None, None))

    def all_runs_no_ins(self):
        return [Run(r, self) for r in self._p.xpath('.//w:r[not(ancestor::w:r) and not(ancestor::w:ins)]')]
    setattr(Paragraph, 'all_runs_no_ins', property(all_runs_no_ins, None, None))

    def origin_text(self):
        return ''.join([r.del_text if r.del_text else r.text for r in self.all_runs_no_ins])
    setattr(Paragraph, 'origin_text', property(origin_text, None, None))


monkey_patch_paragraph()
