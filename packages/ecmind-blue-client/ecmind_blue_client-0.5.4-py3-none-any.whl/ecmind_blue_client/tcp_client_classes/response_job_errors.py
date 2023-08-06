from protlib import CArray, CInt, CStruct

from .response_job_error_data import ResponseJobErrorData
from .response_job_error_description import ResponseJobErrorDescription


class ResponseJobErrors(CStruct):
    length = CInt()
    count = CInt()
    dummy = CInt()
    description = CArray(length="count", ctype=ResponseJobErrorDescription.get_type())
    data = CArray(length="count", ctype=ResponseJobErrorData.get_type())
