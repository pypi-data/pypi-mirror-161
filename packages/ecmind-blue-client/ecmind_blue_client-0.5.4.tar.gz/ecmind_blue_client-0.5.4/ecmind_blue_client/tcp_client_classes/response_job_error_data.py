from protlib import AUTOSIZED, CString, CStruct


class ResponseJobErrorData(CStruct):
    source_name = CString(length=AUTOSIZED)
    error_message = CString(length=AUTOSIZED)
