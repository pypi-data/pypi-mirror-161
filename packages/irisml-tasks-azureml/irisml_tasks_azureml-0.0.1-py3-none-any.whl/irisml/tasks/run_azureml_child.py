import dataclasses
import typing
import irisml.core


class Task(irisml.core.TaskBase):
    @dataclasses.dataclass
    class Config:
        tasks: typing.List[irisml.core.TaskDescription]

    def execute(self, inputs):
        # TODO
        raise NotImplementedError

    def dry_run(self, inputs):
        raise NotImplementedError
