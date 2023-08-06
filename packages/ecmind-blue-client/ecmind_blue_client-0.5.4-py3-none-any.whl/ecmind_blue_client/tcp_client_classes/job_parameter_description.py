from protlib import CInt, CStruct


class JobParameterDescription(CStruct):
    name_offset = CInt()
    type = CInt()
    value_offset = CInt()

    def sizeof(self, cstruct=None) -> int:
        return 12
