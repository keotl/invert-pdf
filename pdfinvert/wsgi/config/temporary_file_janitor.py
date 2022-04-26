from datetime import datetime, timedelta
from glob import glob
import logging
import os
from jivago.config.startup_hooks import PostInit
from jivago.inject.annotation import Component

from jivago.scheduling.annotations import Duration, Scheduled
from jivago.scheduling.regular_interval_schedule import RegularIntervalSchedule
from jivago.scheduling.schedule import Schedule
from jivago.scheduling.task_scheduler import TaskScheduler
from pdfinvert.wsgi.config.conversion_config import ConversionConfig
import shutil
from jivago.lang.annotations import Inject, Override
from jivago.lang.runnable import Runnable

@Component
class TemporaryFileJanitor(Runnable):
    """Cleans up temporary imagemagick files and stray pdf files.
       Relevant for 24/7 operation only."""

    @Inject
    def __init__(self, config: ConversionConfig):
        self._enabled = config.cleanup_enabled
        self._temp_dir = config.temp_directory
        self._logger = logging.getLogger(self.__class__.__name__)

    @Override
    def run(self):
        if not self._enabled:
            return

        cutoff = datetime.now() - timedelta(hours=1)
        count = 0
        for folder in glob("/tmp/magick*"):
            modified = datetime.fromtimestamp(os.path.getmtime(folder))
            if modified < cutoff:
                shutil.rmtree(folder, ignore_errors=True)
                count += 1

        for temp_file in glob(os.path.join(self._temp_dir, "*.pdf")):
            modified = datetime.fromtimestamp(os.path.getmtime(temp_file))
            if modified < cutoff:
                shutil.rmtree(temp_file, ignore_errors=True)
                count += 1

        self._logger.info(f"Removed {count} stray temporary files.")

@PostInit
class CleanupJobInitializer(Runnable):

    @Inject
    def __init__(self, config: ConversionConfig, task_scheduler: TaskScheduler):
        self._enabled = config.cleanup_enabled
        self._task_scheduler = task_scheduler
        self._logger = logging.getLogger(self.__class__.__name__)

    @Override
    def run(self):
        if self._enabled:
            self._logger.info("Running with hourly temporary file cleanup job.")
            self._task_scheduler.schedule_task(TemporaryFileJanitor, RegularIntervalSchedule(Duration.HOUR))
        else:
            self._logger.info("Temporary file cleanup disabled.")
