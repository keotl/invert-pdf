import unittest
from unittest import mock

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

    def test_update_state(self):
        # Given
        token = CompletionTokenSource("job_id", JobState.PENDING)
        self.store.track(token)
        on_completed = mock.Mock()
        token.subscribe(JobState.COMPLETED, on_completed)

        # When
        self.store.update_state("job_id", JobState.COMPLETED)

        # Then
        on_completed.assert_called_once()
