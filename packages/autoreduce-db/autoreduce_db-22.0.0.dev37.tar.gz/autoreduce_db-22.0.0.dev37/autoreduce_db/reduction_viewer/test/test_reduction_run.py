# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2021 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Tests for the ReductionRun class."""
# pylint:disable=no-member
from django.test import TestCase

from autoreduce_db.reduction_viewer.models import ReductionRun


class TestReductionRun(TestCase):
    """Directly tests the message handling classes."""
    fixtures = [
        "autoreduce_db/autoreduce_django/fixtures/status_fixture.json",
        "autoreduce_db/autoreduce_django/fixtures/run_with_multiple_variables.json"
    ]

    def setUp(self) -> None:
        self.reduction_run = ReductionRun.objects.first()
        return super().setUp()

    def test_title_with_one_run_number(self):
        """
        Test that retrieving the title of a `ReductionRun` with just one run and
        no other attributes returns just the run number.
        """
        assert self.reduction_run.title() == "123456"

    def test_title_with_one_run_number_and_version(self):
        """
        Test that retrieving the title of a `ReductionRun` with just one run and
        a given `run_version` returns the run number followed by the run
        version.
        """
        run_version = self.reduction_run.run_version = 2
        assert self.reduction_run.title() == f"123456 - {run_version}"

    def test_title_with_one_run_number_and_title(self):
        """
        Test that retrieving the title of a `ReductionRun` with just one run and
        a given `run_title` returns the run number followed by the run title.
        """
        run_title = self.reduction_run.run_title = "larmor0102"
        assert self.reduction_run.title() == f"123456 - {run_title}"

    def test_title_with_one_run_number_and_title_and_version(self):
        """
        Test that retrieving the title of a ReductionRun with just one run and
        a given `run_title` returns the run number followed by the run version
        and run title.
        """
        run_version = self.reduction_run.run_version = 2
        run_title = self.reduction_run.run_title = "larmor0102"
        assert self.reduction_run.title() == f"123456 - {run_version} - {run_title}"

    def test_title_with_multiple_run_numbers(self):
        """
        Test that retrieving the title of a ReductionRun with a batch of runs
        returns the expected batch.
        """
        next_run = 123457
        self.reduction_run.run_numbers.create(run_number=next_run)
        self.reduction_run.batch_run = True
        assert self.reduction_run.title() == f"Batch 123456 → {next_run}"

    def test_title_with_multiple_run_numbers_and_version(self):
        """
        Test that retrieving the title of a ReductionRun with a batch of runs
        and a given `run_version` returns the expected batch followed by the run
        version.
        """
        next_run = 123457
        self.reduction_run.run_numbers.create(run_number=next_run)
        self.reduction_run.batch_run = True
        run_version = self.reduction_run.run_version = 2
        assert self.reduction_run.title() == f"Batch 123456 → {next_run} - {run_version}"

    def test_title_with_multiple_run_numbers_and_title(self):
        """
        Test that retrieving the title of a ReductionRun with a batch of runs
        and a given `run_title` returns the expected batch followed by the run
        title.
        """
        next_run = 123457
        self.reduction_run.run_numbers.create(run_number=next_run)
        self.reduction_run.batch_run = True
        self.reduction_run.run_title = "larmor0102"
        run_description = self.reduction_run.run_description = "test description"
        result_title = self.reduction_run.title()
        assert result_title == f"Batch 123456 → {next_run} - {run_description}"

    def test_title_with_multiple_run_numbers_and_title_and_version(self):
        """
        Test that retrieving the title of a ReductionRun with a batch of runs
        and a given `run_version` and `run_title` returns the expected batch
        followed by the run version and run title.
        """
        next_run = 123457
        self.reduction_run.run_numbers.create(run_number=next_run)
        self.reduction_run.batch_run = True
        run_version = self.reduction_run.run_version = 2
        self.reduction_run.run_title = "larmor0102"
        run_description = self.reduction_run.run_description = "test description"
        assert self.reduction_run.title() == f"Batch 123456 → {next_run} - {run_version} - {run_description}"
        assert str(self.reduction_run) == f"Batch 123456 → {next_run} - {run_version} - {run_description}"

    def test_run_number(self):
        """Test that retrieving the status returns the expected one."""
        assert self.reduction_run.run_number == 123456

    def test_run_number_multiple_run_numbers(self):
        """Test that retrieving the status returns the expected one."""
        self.reduction_run.run_numbers.create(run_number=123457)
        with self.assertRaises(ValueError):
            self.reduction_run.run_number
        assert [run.run_number for run in self.reduction_run.run_numbers.all()] == [123456, 123457]

    def test_run_arguments(self):
        """Test that retrieving the arguments and converting them to a dict works"""
        args = self.reduction_run.arguments.as_dict()
        assert "standard_vars" in args

    def test_run_script(self):
        """Test that retrieving the script works"""
        assert "def main" in self.reduction_run.script.text
