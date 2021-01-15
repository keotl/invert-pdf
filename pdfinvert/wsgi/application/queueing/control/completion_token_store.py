import logging
import threading
from typing import List

from jivago.inject.annotation import Component, Singleton
from jivago.lang.annotations import Override, Inject
from jivago.lang.nullable import Nullable
from jivago.lang.runnable import Runnable
from jivago.lang.stream import Stream
from jivago.scheduling.annotations import Scheduled, Duration

from pdfinvert.wsgi.application.queueing.control.completion_token import JobState, \
    CompletionTokenSource


@Component
@Singleton
class CompletionTokenStore(object):

    def __init__(self):
        self._tokens: List[CompletionTokenSource] = []
        self._lock = threading.Lock()

    def track(self, token: CompletionTokenSource):
        with self._lock:
            self._tokens.append(token)

    def perform_cleanup(self):
        with self._lock:
            self._tokens = Stream(self._tokens) \
                .filter(lambda t: t.state in (JobState.RUNNING, JobState.PENDING)) \
                .toList()

    def find_by_job(self, job_id: str) -> Nullable[CompletionTokenSource]:
        return Stream(self._tokens) \
            .firstMatch(lambda x: x.job_id == job_id)


@Component
@Scheduled(every=Duration.MINUTE)
class CompletionTokenStoreCleanupWorker(Runnable):

    @Inject
    def __init__(self, store: CompletionTokenStore):
        self.store = store
        self.logger = logging.getLogger(self.__class__.__name__)

    @Override
    def run(self):
        try:
            self.store.perform_cleanup()
        except Exception as e:
            self.logger.error(f"Error while cleaning up old completion tokens: {e}.")
