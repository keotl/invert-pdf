from typing import List

from jivago.lang.annotations import Serializable


@Serializable
class QueuedJob(object):
    job_id: str
    commands: List[List[str]]

    def __init__(self, job_id: str, commands: List[List[str]]):
        self.job_id = job_id
        self.commands = commands
