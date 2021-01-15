import unittest
from unittest import mock

from pdfinvert.wsgi.application.queueing.control.completion_token import CompletionTokenSource, JobState


class CompletionTokenSourceTests(unittest.TestCase):

    def setUp(self):
        self.token = CompletionTokenSource("job_id", JobState.PENDING)

    def test_subscribe_notification_on_state_change(self):
        on_state_completed = mock.Mock()
        self.token.subscribe(JobState.COMPLETED, on_state_completed)

        self.token.set_state(JobState.COMPLETED)

        on_state_completed.assert_called_once()

    def test_subscribe_does_not_notify_if_state_is_the_same(self):
        on_state_pending = mock.Mock()
        self.token.subscribe(JobState.PENDING, on_state_pending)

        on_state_pending.reset_mock()
        self.token.set_state(JobState.PENDING)

        on_state_pending.assert_not_called()

