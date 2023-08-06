from __future__ import annotations

import datetime
import functools
import json
import logging

from abc import ABC, abstractmethod
from typing import *

from .measurement import Measurement
from .field import Field, FieldMap
from .tag import Tag, TagMap
from .utils import threaded_execution


class DatabaseWriter(ABC):

    @abstractmethod
    def write_data(self, datalogger: DataLogger):
        """Meant to write the actual data to the database being used"""
        pass


class PostProcessing:
    @staticmethod
    def register(*measurements: Measurement):
        """
        Decorator to define a postprocessing function for CSV logging as a single-entry postprocessing function.

        Function signature example:
            def postprocessor(datalogger: DataLogger, **kwargs: Dict[Measurement, List[DataEntry]])
        """

        def wrap_outer(func):
            func.__setattr__("post_processing", True)
            func.__setattr__("measurements", measurements)

            @functools.wraps(func)
            def wrap_inner(*args, **kwargs):
                return func(*args, **kwargs)

            return wrap_inner

        return wrap_outer


class PostProcessingHandler:
    def __init__(self, func: Callable[PostProcessing]):
        self.func = func
        self.measurements = func.measurements
        self.post_processing = func.post_processing


class DataEntry(dict):
    def __init__(self, measurement: Measurement, fields_map: FieldMap[Field, Any], tags_map: TagMap[Tag, Any] = None):
        fields_map = fields_map or FieldMap()
        tags_map = tags_map or TagMap()

        super(DataEntry, self).__init__()

        self.measurement = measurement
        self.fields = dict(fields_map)
        self.tags = dict(tags_map)
        self.time = str(datetime.datetime.utcnow())

    def __setattr__(self, key, value):
        super(DataEntry, self).__setattr__(key, value)
        super(DataEntry, self).__setitem__(key, value)


class Dataset(dict):
    def __init__(self):
        super(Dataset, self).__init__()

    def log(self, measurement: Measurement, fields_map: FieldMap[Field, Any], tags_map: TagMap[Tag, Any] = None) -> None:
        self.append(DataEntry(measurement, fields_map, tags_map))

    def append(self, __object: DataEntry) -> None:
        if __object.measurement not in self:
            self[__object.measurement] = list()
        self[__object.measurement].append(__object)

    def get_entries_for_measurement(self, measurement: Measurement) -> List[DataEntry]:
        return self.get(measurement)

    def as_list(self) -> List[DataEntry]:
        data = list()
        for values in self.values():
            assert len([v for v in values if isinstance(v, DataEntry)]) == len(values), f"Not all entries are of type {DataEntry}. This is not permitted"
            data.extend(values)
        return data


class Event(dict):
    def __init__(self, measurement: Measurement, start: float, stop: float, tags_map: TagMap):
        super(Event, self).__init__()
        self.measurement = measurement
        self.start = start
        self.stop = stop
        self.tags_map = tags_map

    def __setattr__(self, key, value):
        super(Event, self).__setattr__(key, value)
        super(Event, self).__setitem__(key, value)


class Events(dict):
    def __init__(self):
        super(Events, self).__init__()

    def log(self, measurement: Measurement, start: float, stop: float, tags_map: TagMap):
        self.append(Event(measurement, start, stop, tags_map))

    def append(self, __object: Event) -> None:
        if __object.measurement not in self:
            self[__object.measurement] = list()
        self[__object.measurement].append(__object)

    def get_entries_for_measurement(self, measurement: Measurement) -> List[Event]:
        return self.get(measurement)

    def as_list(self) -> List[Event]:
        data = list()
        for values in self.values():
            assert len([v for v in values if isinstance(v, Event)]) == len(values), f"Not all entries are of type {Event}. This is not permitted"
            data.extend(values)
        return data


class DataLogger:
    def __init__(self, *database_writers: DatabaseWriter, continuous_write: bool = False):
        f"""
        Args:
            database_writers: An arbitrary number of database writers created by the user that are of the type {DatabaseWriter} 
            continuous_write: A bool to tell if writes should be done immediately when {self.log.__name__} is invoked. Removes the need to use {self.write_data.__name__}`
        """
        self._dataset: Dataset = Dataset()
        self.postprocessing_functions = list()
        self._db_writers = list()
        self.continuous_write = continuous_write
        self._events: Events = Events()
        for database_writer in database_writers:
            assert isinstance(database_writer, DatabaseWriter), \
                f"A database writer passed to a '{DataLogger.__module__}.{DataLogger}' object must inherit from type '{DatabaseWriter}'."

            self._db_writers.append(database_writer)

    def __str__(self):
        return json.dumps(self._dataset, indent=2)

    @property
    def dataset(self):
        return self._dataset.as_list()

    @property
    def events(self):
        return self._events.as_list()

    @property
    def db_writers(self):
        return self._db_writers

    def add_post_processing(self, func: Callable[PostProcessing]):
        """
        Adds a post-processing function to a data logger.

        Args:
            func: The callable function to add as a post-processing method.
        """
        assert hasattr(func, "post_processing") and func.post_processing, f"This function does not appear to be registered as a post-processing method. Please use decorator '@{PostProcessing.register}' to register it"
        self.postprocessing_functions.append(PostProcessingHandler(func))

    def measure(self,
                func: Callable,
                measurement: Measurement,
                field: Field,
                tags_map: TagMap = None,
                event_tags: TagMap = None,
                logger: logging.Logger = None, log_start: str = None, log_end: str = None,
                args: tuple = None, kwargs: dict = None):
        """
        This function wraps any arbitrary function and times the duration for that function and then logs the duration
        to a DataLogger object for a given measurement and a field name.
        Wrapping function to call an arbitrary function and calculate the duration of that function.

        Args:
            func: The function to call and calculate the time for.
            measurement: The main measurement to log the time to.
            field: The field in the main measurement to log the duration to.
            tags_map: Optional map of tags to assign to the measurement.
            event_tags: Optional map of tags used for logging events. Events will be written if and only if this variable isn't None.
            logger: Optional logger object. Used to log a message before and/or after calling the function.
            log_start: Optional log message to log before calling the function. Requires that the argument logger is passed to this function.
            log_end: Optional log message to log after calling the function. Requires that the argument logger is passed to this function.
            args: A tuple of arguments to pass to func.
            kwargs: A dict of keyword-arguments to pass to func.
        """
        #
        # Verify the input.
        #
        assert isinstance(func, Callable), f"'func' must be a callable object."

        if args is None:
            args = tuple()
        else:
            assert isinstance(args, tuple), "args must be passed as a tuple"
        if kwargs is None:
            kwargs = dict()
        else:
            assert isinstance(kwargs, dict), "kwargs must be passed as a dict"

        if log_start is not None or log_end is not None:
            assert logger is not None and isinstance(logger, logging.Logger), f"If either 'log_start' or 'log_end' is passed to this method, 'logger' must also be passed as a '{logging.Logger}' object"

        if log_start:
            logger.info(log_start)

        #
        # Execute wrapped function
        #
        ts_start = datetime.datetime.utcnow()
        return_values = func(*args, **kwargs)
        ts_stop = datetime.datetime.utcnow()

        #
        # Get duration
        #
        dur = (ts_stop - ts_start).total_seconds()

        #
        # Log event for measurement (if event_tags is not None)
        #
        if event_tags:
            self.log_event(measurement, ts_start, ts_start, event_tags)

        #
        # Log duration to measurement.
        #
        self.log(measurement, FieldMap.build(field, dur), tags_map=tags_map)

        if log_end:
            logger.info(log_end)

        return return_values

    def measure_block(self, measurement: Measurement, field: Field, tags_map: TagMap = None, event_tags: TagMap = None):
        """
        This function uses the `with` syntax in Python to measure the duration for an arbitrary block of code.

        Usage:
        ```
        f = influxdb_datalogger.Field("duration")
        t = influxdb_datalogger.Tag("identifier")
        m = influxdb_datalogger.Measurement("time-taken", f, t)
        tm = influxdb_datalogger.TagMap.build(t, "test")
        datalogger = influxdb_datalogger.DataLogger()

        with datalogger.measure_block(measurement=m, field=f, tags_map=tm):
            time.sleep(1)
        ```

        Args:
            measurement: The main measurement to log the time to.
            field: The field in the main measurement to log the duration to.
            tags_map: Optional map of tags to assign to the measurement.
            event_tags: Optional map of tags used for logging events. Events will be written if and only if this variable isn't None.
        """
        class BlockMeasurer:
            def __init__(self, datalogger: DataLogger, measurement: Measurement, field: Field, tags_map: TagMap = None, event_tags: TagMap = None):
                self.datalogger = datalogger
                self.measurement = measurement
                self.field: Field = field
                self.tags_map: TagMap = tags_map
                self.start_time: datetime.datetime = None
                self.end_time: datetime.datetime = None
                self.event_tags: TagMap = event_tags

            def __enter__(self):
                self.start_time = datetime.datetime.utcnow()

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.end_time = datetime.datetime.utcnow()
                duration = (self.end_time - self.start_time).total_seconds()
                if self.event_tags:
                    self.datalogger.log_event(self.measurement, self.start_time, self.end_time, self.event_tags)

                self.datalogger.log(self.measurement, FieldMap.build(self.field, duration), self.tags_map)

        return BlockMeasurer(datalogger=self, measurement=measurement, field=field, tags_map=tags_map, event_tags=event_tags)

    def log(self, measurement: Measurement, fields_map: FieldMap, tags_map: TagMap = None):
        """
        Used to log data for a measurement using a fields_map and an optional tags_map.

        Args:
            measurement: The measurement to log the data for.
            fields_map: A FieldMap object to write data to the measurement.
            tags_map: An optional TagMap to tag the data written for the measurement.
        """

        assert isinstance(measurement, Measurement), f"'measurement' must be of type '{Measurement.__module__}.{Measurement}'."
        assert isinstance(fields_map, FieldMap), f"'fields_map' must be of type '{FieldMap.__module__}.{FieldMap}', not '{type(fields_map)}'"
        assert isinstance(tags_map, TagMap) or tags_map is None, f"'tags_map' must be {None}, or of type '{TagMap.__module__}.{TagMap}', not '{type(tags_map)}'"

        tags_defaulted = measurement.get_defaulted_tags()
        tags_predefined = measurement.get_predefined_tags()
        # Add together all maps of tags
        tags_all = TagMap()
        # Add the set of defaulted tags first
        tags_all.update(tags_defaulted)
        # Add the set of pre-defined tags second
        tags_all.update(tags_predefined)
        # Add the set of configured tags third (if they aren't None) so that the user may overwrite pre-defined tags if they have been configured manually.
        if tags_map:
            tags_all.update(tags_map)
        # Assert tags are defined in measurement
        for tag in tags_all:
            assert tag in measurement.tags, f"Tag '{tag}' is not defined as a tag for measurement '{measurement}'"

        fields_defaulted = measurement.get_default_fields()
        fields_predefined = measurement.get_predefined_fields()
        # Add together all maps of fields
        fields_all = FieldMap()
        # Add the set of defaulted fields first
        fields_all.update(fields_defaulted)
        # Add the set of pre-defined fields second
        fields_all.update(fields_predefined)
        # Add the set of configured fields third so that the user may overwrite pre-defined tags if they have been configured manually.
        fields_all.update(fields_map)
        # Assert fields are in measurement
        for field in fields_all:
            assert field in measurement.fields, f"Field '{field}' is not defined as a field for measurement '{measurement}'"

        # Log the measurement to the dataset
        self._dataset.log(measurement, fields_all, tags_all)

        # If continuous_write is configured we should write the data immediately
        if self.continuous_write:
            self.write_data()

    def log_event(self, measurement: Measurement, start_time: datetime.datetime, stop_time: datetime.datetime, event_tags_map: TagMap = None):
        """
        Used to log data for a measurement using a fields_map and an optional tags_map.

        Args:
            measurement: The measurement to log the event for.
            start_time: datetime.datetime object for when the event started. Should be in UTC
            stop_time: datetime.datetime object for when the event stopped. Should be in UTC
            event_tags_map: An optional TagMap to tag the event data written for the measurement.
        """
        epoch_ts_start = start_time.replace(tzinfo=datetime.timezone.utc).timestamp()
        epoch_ts_stop = stop_time.replace(tzinfo=datetime.timezone.utc).timestamp()
        self._events.log(measurement=measurement, start=epoch_ts_start, stop=epoch_ts_stop, tags_map=event_tags_map)

    def write_data(self):
        """
        Write data to all database writers configured to the data logger.

        Steps done:
        1. Validate the integrity of the data that has been written to the logger.
        2. Run all post-processing methods configured for the logger.
        3. Since the dataset have changed after post-processing, we need to validate the dataset again.
        4. Write the dataset to all database writers configured for the logger.
        5. Clean the dataset since the data has been written.
        """
        #
        # Validate the integrity of the dataset based on how it has been created.
        #
        self._validate_dataset()

        #
        # Do post-processing that has been added on the recently validated dataset.
        #
        self._do_post_processing()

        #
        # Validate the integrity of the dataset again after doing post-processing.
        #
        self._validate_dataset()

        #
        # Write the dataset to all database writers configured to the data logger.
        #
        for writer in self._db_writers:
            assert isinstance(writer, DatabaseWriter)
            writer.write_data(self)

        #
        # Clean the dataset since it has all been written to the databases.
        #
        self._dataset.clear()
        self._events.clear()

    def _validate_dataset(self):
        def validate_entry(entry: DataEntry):
            measurement = entry.measurement
            assert isinstance(measurement, Measurement)
            measurement_tags = measurement.tags
            measurement_fields = measurement.fields
            fields = entry.fields
            tags = entry.tags

            for field in measurement_fields:
                assert field in fields and fields[field] is not None, \
                    f"Field '{field}' has not been logged with a value. This is not permitted."

            for tag in measurement_tags:
                assert (tag in tags and tags[tag] is not None) or tag in measurement.optional_tags, \
                    f"Tag '{tag}' has not been configured with a value, and is not configured as an optional tag. This is not permitted."

        threaded_execution(validate_entry, self._dataset.as_list())

    def _do_post_processing(self):
        for post_processing in self.postprocessing_functions:
            assert isinstance(post_processing, PostProcessingHandler)
            assert hasattr(post_processing.func, "post_processing") and post_processing.func.post_processing
            all_measurement_entries = dict()
            for measurement in post_processing.measurements:
                measurement_entries = self._dataset.get_entries_for_measurement(measurement)
                all_measurement_entries[measurement] = measurement_entries
            post_processing.func(self, **all_measurement_entries)
