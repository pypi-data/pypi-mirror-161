from protlib import AUTOSIZED, CString, CStruct


class JobParameterData(CStruct):
    name = CString(length=AUTOSIZED)
    value = CString(length=AUTOSIZED)

    def sizeof(self, cstruct=None) -> int:
        return len(self.name) + len(self.value) + 2
