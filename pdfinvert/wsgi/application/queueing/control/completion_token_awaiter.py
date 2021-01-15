import multiprocessing
import time

from pdfinvert.wsgi.application.queueing.control.completion_token import CompletionToken, JobState


class CompletionTokenAwaiter(object):

    def __init__(self, completion_token: CompletionToken, on_failure: Exception = None, timeout: int = None,
                 on_timeout: Exception = None):
        self._timeout_exception = on_timeout
        self._error_exception = on_failure
        self.timeout = timeout
        self._token = completion_token
        self.queue = multiprocessing.Queue(3)
        if self.timeout:
            self._timeout_thread = multiprocessing.Process(target=_timeout_thread_main, args=(timeout, self.queue))
        completion_token.subscribe(JobState.FAILED, self.on_failure)
        completion_token.subscribe(JobState.COMPLETED, self.on_success)

    def on_failure(self):
        self.queue.put("FAILURE")

    def on_success(self):
        self.queue.put("SUCCESS")

    def wait(self):
        if self.timeout:
            self._timeout_thread.start()

        reason = self.queue.get(True)
        if self.timeout is not None and self._timeout_thread.is_alive():
            self._timeout_thread.terminate()
        if reason == "FAILURE" and self._error_exception is not None:
            raise self._error_exception
        if reason == "TIMEOUT" and self._timeout_exception is not None:
            raise self._timeout_exception
        return


def _timeout_thread_main(timeout: int, queue: multiprocessing.Queue):
    time.sleep(timeout)
    queue.put("TIMEOUT")
