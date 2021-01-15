import time
import unittest
from unittest import mock
from unittest.mock import patch

from pdfinvert.wsgi.application.queueing.control.completion_token import JobState
from pdfinvert.wsgi.application.queueing.control.completion_token_store import CompletionTokenStore
from pdfinvert.wsgi.application.queueing.conversion_queue import ConversionQueue
from pdfinvert.wsgi.application.queueing.queued_job import QueuedJob
import subprocess


class ConversionQueueTests(unittest.TestCase):

    def setUp(self):
        self.queue = ConversionQueue(CompletionTokenStore(), {})

    @patch("subprocess.check_output")
    def test_run_job(self, CheckOutput):
        CheckOutput = lambda: time.sleep(1)
        on_completion = mock.Mock()

        token = self.queue.enqueue(QueuedJob("job_id", [["echo", "foobar"]]))
        token.subscribe(JobState.COMPLETED, on_completion)
        time.sleep(1.5)
        # time.sleep(1000)

        on_completion.assert_called_once()
