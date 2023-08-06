import os

from comtypes import COMError
from comtypes.client import CreateObject

from .client import Client
from .const import ParamTypes
from .job import Job
from .result import Result
from .result_file import ResultFile, ResultFileType


class ComClient(Client):
    def __init__(self, hostname: str, port: int, username: str, password: str):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.server = CreateObject("OxSvrSpt.Server")
        self.session = self.server.Login(username, password, hostname, str(port))

    def execute(self, job: Job) -> Result:
        """Send a job to the com server (OxSvrSpt.Server), execute it and return the response.

        Keyword arguments:
        job -- A previously created Job() object.
        """
        native_job = self.session.NewJob(job.name)

        for param in job.params:
            if param.type == ParamTypes.INTEGER:
                native_job.InputParameters.AddNewIntegerParameter(
                    param.name, param.value
                )
            elif param.type == ParamTypes.BOOLEAN:
                native_job.InputParameters.AddNewBooleanParameter(
                    param.name, param.value
                )
            elif param.type == ParamTypes.DATE_TIME:
                native_job.InputParameters.AddNewDatetimeParameter(
                    param.name, param.value
                )
            elif param.type == ParamTypes.DOUBLE:
                native_job.InputParameters.AddNewDoubleParameter(
                    param.name, param.value
                )
            elif param.type == ParamTypes.STRING:
                native_job.InputParameters.AddNewStringParameter(
                    param.name, param.value
                )
            elif param.type == ParamTypes.BASE64:
                native_job.InputParameters.AddNewXmlParameter(param.name, param.value)
            elif param.type == ParamTypes.DB:
                raise Exception("parameter type DB is not supported.")
            else:
                raise Exception("Unknown parameter type")

        for file in job.files:
            native_job.InputFileParameters.AddExistFile(file)

        error_message = None
        try:
            native_job.Execute()

            result_values = {}
            for output_parameter in native_job.OutputParameters:
                result_values[output_parameter.Name] = output_parameter.XML if output_parameter.type == 6 else output_parameter.Value

            result_files = []
            for ofp in native_job.OutputFileParameters:
                _, file_name = os.path.split(ofp.FileName)
                result_file = ResultFile(
                    ResultFileType.FILE_PATH,
                    file_name=file_name,
                    file_path=ofp.FileName,
                )
                ofp.AutoDelete = False
                result_files.append(result_file)

            result_return_code = native_job.Errors.ResultCode
            return Result(
                result_values, result_files, result_return_code, error_message
            )
        except COMError as ex:
            error_message = str(ex.details)
            return Result(return_code=ex.hresult, error_message=error_message)
