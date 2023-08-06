# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""Models that represent the tables in the database."""
# pylint:disable=no-member
import json
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models


class ReductionScript(models.Model):
    """
    Holds a sharable reduction script's text.

    Fields:
        text: The script's text
    """
    text = models.TextField(blank=True, validators=[MaxLengthValidator(100000)])


class ReductionArguments(models.Model):
    """
    Holds a sharable reduction argument's raw JSON dump representation
    as well as allows for scope of the arguments via start_run and experiment_reference

    Fields:
        start_run: The first run number from which the arguments will be effective.
                They will be passed to the reduction script.
        experiment_reference: The experiment for which the arguments will be effective.
                Experiment arguments override ALL other arguments.
                This is enforced in the queue processor.
    """
    raw = models.TextField(blank=False, validators=[MaxLengthValidator(100000)])
    start_run = models.IntegerField(null=True, blank=True)
    experiment_reference = models.IntegerField(blank=True, null=True)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE, related_name="arguments")

    def as_dict(self) -> dict:
        """Loads the raw string back into a dict object and returns it."""
        return json.loads(self.raw)


class Instrument(models.Model):
    """
    Holds data about an Instrument.

    Fields:
        name: Name of the instrument
        is_active: Whether the instrument is active. If not active,
                   the queue processor will skip runs for it.
        is_paused: Whether the instrument has been MANUALLY paused from the webapp.
        is_flat_output: Determines the output structure of the reduction.
                        If true, the output for all run versions will be in the same folder.
                        If false, each run version will be saved in a separate folder.
    """
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=False)
    is_paused = models.BooleanField(default=False)
    is_flat_output = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    def get_last_for_rerun(self, runs=None) -> 'ReductionRun':
        """
        Return the last non-skipped run. If all the runs are skipped, return the
        last skipped run.

        Args:
            runs: Pre-queried runs for the instrument.
                  If None, then reduction_runs.all() will be queried from the database.
        Returns:
            The last not-skipped reduction run in the queryset.
        """
        if not runs:
            runs = self.reduction_runs.all()

        last_run = runs.exclude(status=Status.get_skipped()).last()
        if not last_run:
            last_run = runs.last()

        return last_run


class Experiment(models.Model):
    """
    Holds data about an Experiment.

    Fields:
        reference_number: The experiment reference number assigned to the experiment.
                          Also referred to as rb_number because of convention in ISIS.
    """
    reference_number = models.IntegerField(unique=True)

    def __str__(self):
        return f"RB{self.reference_number}"


class Status(models.Model):
    """
    Enum table for status types of messages. Caches the objects internally at runtime
    to avoid repeated queries to the DB for the status objects.

    Fields:
        value: The value of the status. One of STATUS_CHOICES
    """
    _cached_statuses = {}
    STATUS_CHOICES = (('q', 'Queued'), ('p', 'Processing'), ('s', 'Skipped'), ('c', 'Completed'), ('e', 'Error'))

    value = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def value_verbose(self) -> str:
        """Return the status as its textual value."""
        return dict(Status.STATUS_CHOICES)[self.value]

    def __str__(self) -> str:
        return self.value_verbose()

    @staticmethod
    def _get_status(status_value: str):
        """
        Return a status matching the given name or create one if it doesn't yet
        exist.

        Args:
            status_value: The value of the status record in the database.
        """
        if status_value in Status._cached_statuses:
            return Status._cached_statuses[status_value]
        else:
            status_record = Status.objects.get_or_create(value=status_value)[0]
            Status._cached_statuses[status_value] = status_record

        return status_record

    @staticmethod
    def get_error():
        """Return the error status."""
        return Status._get_status('e')

    @staticmethod
    def get_completed():
        """Return the completed status."""
        return Status._get_status('c')

    @staticmethod
    def get_processing():
        """Return the processing status."""
        return Status._get_status('p')

    @staticmethod
    def get_queued():
        """Return the queued status."""
        return Status._get_status('q')

    @staticmethod
    def get_skipped():
        """Return the skipped status."""
        return Status._get_status('s')


class Software(models.Model):
    """Represents the software used to perform the reduction."""
    name = models.CharField(max_length=100, blank=False, null=False)
    version = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return f"{self.name}-{self.version}"


class ReductionRun(models.Model):
    """
    Table designed to link all table together. This represents a single
    reduction run that takes place at ISIS. Thus, this will store all the
    relevant data regarding that run.


    Fields:
        run_version: The run version of the reduction run.
                     This gets incremented if a run is re-run from the webapp.
        started_by: The user who started the reduction run.
                    Runs submitted from run_detection will have -1 as the user id, which
                    gets assigned "Autoreduction service" in the webapp.
        run_description: The description of the reduction run.
                         Manually specified by the user during re-run.
        run_title: The title of the reduction run. Value is taken from the ICAT
                   entry for the run.
        admin_log: The admin log for the reduction run, containing debug information
                   for the runtime environment.
        graph: FIXME - I am not sure this is used for anything anymore.
        message: The ActiveMQ message with which the reduction run was submitted.
                 Can be used to replicate the reduction run.
        reduction_log: User facing output from the reduction execution, i.e. things that
                       are logged to the stdout/console.
        reduction_host: The hostname of the machine that ran the reduction. Useful
                        for tracking down issues that occurred during reduction.
        created: The date and time the reduction run was created.
        finished: The date and time the reduction run was finished.
        last_updated: The date and time the reduction run was last updated.
        started: The date and time the reduction run was started.

        hidden_in_failviewer: Can be set from failed queue page to hide the run from showing up
                              in the failed queue page again.

        overwrite: If true, the output folder will be overwritten.
        batch_run: Whether this reduction run is for a batch run.

        experiment: Foreign key to the experiment this reduction run belongs to.
        instrument: Foreign key to the instrument this reduction run belongs to.
        arguments: Foreign key to the arguments used to run the reduction.
        script: Foreign key to the script used to run the reduction.
        retry_run: Foreign key to a rerun of this run. Not actively used and
                   will be removed with https://autoreduce.atlassian.net/browse/AR-1554
        status: Foreign key to the status of the reduction run.
        software: Foreign key to the software used to run the reduction.
    """
    # Integer fields
    run_version = models.IntegerField(blank=False, validators=[MinValueValidator(0)])
    started_by = models.IntegerField(null=True, blank=True)

    # Char fields
    run_description = models.CharField(max_length=200, blank=True)
    run_title = models.CharField(max_length=200, blank=True)

    # Text fields
    admin_log = models.TextField(blank=True)
    graph = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    reduction_log = models.TextField(blank=True)
    reduction_host = models.TextField(default="", blank=True, verbose_name="Reduction hostname")

    # Date time fields
    created = models.DateTimeField(auto_now_add=True, blank=False)
    finished = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, blank=False)
    started = models.DateTimeField(null=True, blank=True)

    # Bool field
    hidden_in_failviewer = models.BooleanField(default=False)
    overwrite = models.BooleanField(default=False)
    batch_run = models.BooleanField(default=False)

    # Foreign Keys
    experiment = models.ForeignKey(Experiment, blank=False, related_name='reduction_runs', on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, related_name='reduction_runs', null=True, on_delete=models.CASCADE)
    arguments = models.ForeignKey(ReductionArguments,
                                  blank=False,
                                  related_name='reduction_runs',
                                  on_delete=models.CASCADE)
    script = models.ForeignKey(ReductionScript, blank=False, related_name='reduction_runs', on_delete=models.CASCADE)
    status = models.ForeignKey(Status, blank=False, related_name='+', on_delete=models.CASCADE)
    # Allowed software field to be black in code line below. Issued opened (#852) to later
    # populate this field
    software = models.ForeignKey(
        Software,
        blank=True,
        related_name='reduction_runs',
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title()

    def title(self):
        """
        Return an interface-friendly name that identifies this run using either
        run name or run version.
        """
        try:
            title = f"{self.run_number}"
        except ValueError:
            title = f"Batch {self.run_numbers.first()} → {self.run_numbers.last()}"

        if self.run_version > 0:
            title += f" - {self.run_version}"

        if not self.batch_run and self.run_title:
            title += f" - {self.run_title}"
        elif self.batch_run and self.run_description:
            title += f" - {self.run_description}"

        return title

    @property
    def run_number(self) -> int:
        """
        Return the value of the run_number, if only a single one is associated
        with this run. This replicates the behaviour of a one to one
        relationship between a ReductionRun and a RunNumber.
        """
        if self.run_numbers.count() == 1:
            return self.run_numbers.first().run_number
        else:
            raise ValueError(
                "This run has more then one run_number associated with it. You must iterate run_numbers manually")


class RunNumber(models.Model):
    """
    Represents the run number or run numbers that a ReductionRun spans.

    Normal reduction runs will have 1 RunNumber.
    Batch reduction runs will have >1 RunNumbers.


    Fields:
        run_number: A run number associated with the reduction run.
        reduction_run: Foreign key to the reduction run this run number belongs to.
    """
    run_number = models.IntegerField(blank=False, validators=[MinValueValidator(0)])
    reduction_run = models.ForeignKey(ReductionRun, blank=False, related_name='run_numbers', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.run_number}"


class DataLocation(models.Model):
    """
    Represents the location at which the unreduced data is stored on disk.

    Fields:
        file_path: The path to the file on disk.
        reduction_run: Foreign key to the reduction run this data location belongs to.
    """
    file_path = models.CharField(max_length=255)
    reduction_run = models.ForeignKey(ReductionRun, blank=False, related_name='data_location', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.file_path}"


class ReductionLocation(models.Model):
    """
    Represents the location at which the reduced data is stored on disk.

    Fields:
        file_path: The path to the file on disk.
        reduction_run: Foreign key to the reduction run this data location belongs to.
    """
    file_path = models.CharField(max_length=255)
    reduction_run = models.ForeignKey(
        ReductionRun,
        blank=False,
        related_name='reduction_location',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.file_path}"


class Notification(models.Model):
    """
    Represents possible notification messages regarding reduction runs.

    Fields:
        message: The message to be displayed.
        is_active: Whether the notification is active or not.
        severity: The severity of the message.
        is_staff_only: Whether the message is only visible to staff.
                       If False, then it will be shown to all users
    """
    SEVERITY_CHOICES = (('i', 'info'), ('w', 'warning'), ('e', 'error'))

    message = models.CharField(max_length=255, blank=False)
    is_active = models.BooleanField(default=True)
    severity = models.CharField(max_length=1, choices=SEVERITY_CHOICES, default='i')
    is_staff_only = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification: {self.message}"

    def severity_verbose(self) -> str:
        """Return the severity as its textual value."""
        return dict(Notification.SEVERITY_CHOICES)[self.severity]
