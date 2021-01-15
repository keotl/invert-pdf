import unittest

from jivago.lang.nullable import Nullable

from pdfinvert.wsgi.application.queueing.control.completion_token import CompletionTokenSource, JobState
from pdfinvert.wsgi.application.queueing.control.completion_token_store import CompletionTokenStore


class CompletionTokenStoreTests(unittest.TestCase):

    def setUp(self):
        self.store = CompletionTokenStore()

    def test_cleanup(self):
        token = CompletionTokenSource("job_id", JobState.COMPLETED)
        self.store.track(token)

        self.store.perform_cleanup()

        self.assertEqual(Nullable.empty(), self.store.find_by_job("job_id"))
