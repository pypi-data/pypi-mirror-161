from docx.shared import Parented
from docx.text.run import Run


class Revision(Parented):

    def __init__(self, rev, parent):
        super(Revision, self).__init__(parent)
        self._rev = self._element = self.element = rev

    @property
    def runs(self):
        return [Run(r, self) for r in self._rev.r_lst]

    @property
    def text(self):
        text = ''
        for run in self.runs:
            text += run.text
            text += run.del_text
        return text

    @property
    def tagroot(self):
        nspfx, tagroot = self.element._nsptag.split(':')
        return tagroot


class Deltext(Parented):

    def __init__(self, delt, parent):
        super(Deltext, self).__init__(parent)
        self._delt = self._element = self.element = delt

