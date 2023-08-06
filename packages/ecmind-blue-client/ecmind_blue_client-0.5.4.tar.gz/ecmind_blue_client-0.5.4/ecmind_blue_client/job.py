from typing import List, Union

from .const import Jobs, ParamTypes
from .param import Param


class Job:
    def __init__(
        self,
        jobname: Union[str, Jobs],
        files: Union[List[str], None] = None,
        context_user: Union[str, None] = None,
        **params,
    ):
        """Create a new Job() object.

        Keyword arguments:
        jobname -- String with the a blue jobname, i. e. 'dms.GetResultList'
        files -- (Optional) List of strings with file paths to add to the job.
        context_user -- (Optional) Set the magical parameter `$$$SwitchContextUserName$$$` to a username.
        **params -- Add arbitrary job input parameters. Uses Param.infer_type() to guess the blue parameter type.
        """
        self.name = jobname.value if isinstance(jobname, Jobs) else jobname
        self.params: List[Param] = []
        self.files = files if files is not None else []
        for name, value in params.items():
            self.append(Param.infer_type(name, value))
        if context_user:
            self.append(Param("$$$SwitchContextUserName$$$", ParamTypes.STRING, context_user))

    def append(self, param: Param):
        """Appends a job input parameter.
        Keyword arguments:
        param -- Param object.
        """
        self.params.append(param)

    def update(self, param: Param):
        """Updates a job input parameters value and type. Appends the parameter if not allready present.
        Keyword arguments:
        param -- Param object.
        """
        for current_param in self.params:
            if current_param.name == param.name:
                current_param.value = param.value
                current_param.type = param.type
                return True
        self.append(param)

    def append_file(self, filepath: str):
        """Appends a job input file parameter.
        Keyword arguments:
        filepath -- String with file path to append.
        """
        self.files.append(filepath)

    def __repr__(self) -> str:
        return f'Job "{self.name}" ({len(self.files)} files): {self.params}'
