from django.test import TestCase

from autoreduce_db.reduction_viewer.models import Status


class TestStatus(TestCase):
    """
    Directly tests the message handling classes
    """
    fixtures = ["autoreduce_db/autoreduce_django/fixtures/status_fixture.json"]

    def test_retrieve_status(self):
        """Test that retrieving the status returns the expected one"""

        assert len(Status._cached_statuses.values()) == 0

        assert Status.get_error() is not None
        assert str(Status.get_error()) == "Error"
        assert len(Status._cached_statuses.values()) == 1

        assert Status.get_completed() is not None
        assert str(Status.get_completed()) == "Completed"
        assert len(Status._cached_statuses.values()) == 2

        assert Status.get_processing() is not None
        assert str(Status.get_processing()) == "Processing"
        assert len(Status._cached_statuses.values()) == 3

        assert Status.get_queued() is not None
        assert str(Status.get_queued()) == "Queued"
        assert len(Status._cached_statuses.values()) == 4

        assert Status.get_skipped() is not None
        assert str(Status.get_skipped()) == "Skipped"
        assert len(Status._cached_statuses.values()) == 5
