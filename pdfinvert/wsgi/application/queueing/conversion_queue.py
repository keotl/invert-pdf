import abc
import logging
import multiprocessing
import subprocess
import threading
from multiprocessing.pool import ThreadPool
from typing import List, Set, Dict, Tuple

from jivago.config.properties.application_properties import ApplicationProperties
from jivago.inject.annotation import Singleton
from jivago.lang.annotations import Serializable, Override, Inject

from pdfinvert.wsgi.application.queueing.control.completion_token import CompletionToken, CompletionTokenSource, \
    JobState
from pdfinvert.wsgi.application.queueing.control.completion_token_store import CompletionTokenStore
from pdfinvert.wsgi.application.queueing.queued_job import QueuedJob


@Serializable
class QueuedCommand(object):
    job_id: str
    command_index: int
    command: List[str]

    def __init__(self, job_id: str, command_index: int, command: List[str]):
        self.job_id = job_id
        self.command_index = command_index
        self.command = command


class JobQueue(abc.ABC):

    def enqueue(self, job: QueuedJob):
        raise NotImplementedError

    def get_queue_depth(self) -> int:
        raise NotImplementedError


class QueuedCommandStatusReporter(abc.ABC):
    def track_completion(self, job_id: str, command_index: int):
        raise NotImplementedError

    def track_failure(self, job_id: str, command_index: int):
        raise NotImplementedError


@Singleton
class ConversionQueue(JobQueue, QueuedCommandStatusReporter):

    @Inject
    def __init__(self, completion_token_store: CompletionTokenStore, application_properties: ApplicationProperties):
        self.completion_token_store = completion_token_store
        self.queue = multiprocessing.Queue()
        self._completion_stages: Dict[str, Tuple[Set[int], int]] = {}
        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Instantiated conversion job queue with address '{id(self)}.'")
        self.executor = ConversionJobExecutor(self, application_properties.get("reserved_threads") or 2)

    @Override
    def get_queue_depth(self) -> int:
        return self.queue.qsize()

    @Override
    def enqueue(self, job: QueuedJob) -> CompletionToken:
        with self._lock:
            self._completion_stages[job.job_id] = set(), len(job.commands)
            token = CompletionTokenSource(job.job_id, JobState.PENDING)
            self.completion_token_store.track(token)
            for i, command in enumerate(job.commands):
                self.queue.put(QueuedCommand(job.job_id, i, command))

        return token

    @Override
    def track_completion(self, job_id: str, command_index: int):
        with self._lock:
            if self._completion_stages.get(job_id) is None:
                self.logger.warning(
                    f"Tried to track completion for an unknown job command {job_id}:{command_index}. Ignoring.")
            else:
                completed_steps, total = self._completion_stages[job_id]
                completed_steps.add(command_index)
                token = self.completion_token_store.find_by_job(job_id)
                if not token.isPresent():
                    self.logger.warning(
                        f"Got command result for an unknown job. This might indicate a process leak in the application!")
                    return
                if len(completed_steps) == total:
                    try:
                        token.get().set_state(JobState.COMPLETED)
                    finally:
                        try:
                            del self._completion_stages[job_id]
                        except KeyError:
                            pass
                else:
                    token.get().set_state(JobState.RUNNING)

    @Override
    def track_failure(self, job_id: str, command_index: int):
        with self._lock:
            if self._completion_stages.get(job_id) is None:
                self.logger.warning(
                    f"Tried to track failure for an unknown job command {job_id}:{command_index}. Ignoring.")
            else:
                token = self.completion_token_store.find_by_job(job_id)
                if not token.isPresent():
                    self.logger.warning(
                        f"Got command failure for an unknown job. This might indicate a process leak in the application!")
                    return
                try:
                    token.get().set_state(JobState.FAILED)
                finally:
                    try:
                        del self._completion_stages[job_id]
                    except KeyError:
                        pass


class ConversionJobExecutor(object):

    def __init__(self, queue: ConversionQueue, reserved_threads: int):
        self.conversion_queue = queue
        self.job_queue = queue.queue
        self.feedback_queue = multiprocessing.Queue()
        pool_size = max(1, multiprocessing.cpu_count() - reserved_threads)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Created conversion job executor with {pool_size} processes.")
        self.pool = ThreadPool(pool_size, _worker_execute, (self.job_queue, self.feedback_queue))
        self.should_stop = False
        self.feedback_thread = threading.Thread(target=self.feedback_thread_main)
        self.feedback_thread.start()

    def feedback_thread_main(self):
        while not self.should_stop:
            job_id, command_index, status = self.feedback_queue.get(True)
            if status == "SUCCESS":
                self.conversion_queue.track_completion(job_id, command_index)
            elif status == "FAILURE":
                self.conversion_queue.track_failure(job_id, command_index)


def _worker_execute(job_queue: multiprocessing.Queue, feedback_queue: multiprocessing.Queue):
    while True:
        job = job_queue.get(True)
        try:
            subprocess.check_output(job.command)
            feedback_queue.put((job.job_id, job.command_index, "SUCCESS"))
        except Exception as e:
            feedback_queue.put((job.job_id, job.command_index, "FAILURE"))
