# InfluxDB datalogger
This package is used to log data in a format that matches the format that InfluxDB uses. 

## DatabaseWriter
The datalogger comes with an abstract class called `DatabaseWriter`. You need to create a class that inherits from this class and implements the function `write_data`. An object of this type is then used to create a datalogger object. 
The purpose of this object is to write the actual data to the desired database.

Note that whenever data is written to the database, the data that the datalogger has is completely purged because we don't want two calls to `write_data` to write duplicated data. 

### Example
The following example is from the tests in the repository
```python
class DbWriter(influxdb_datalogger.DatabaseWriter):
    def write_data(self, datalogger: influxdb_datalogger.DataLogger):
        dataset = datalogger.dataset
        if os.path.exists(DATA_FILE):
            # If the file exists we are probably writing more than once in a test.
            # Since DbWriter just writes to a JSON file we need to essentially append to the existing data, which is what this does.

            loaded_dataset = json.load(open(DATA_FILE))
            dataset = [*loaded_dataset, *dataset]
        json.dump(dataset, open(DATA_FILE, "w"), indent=2)
```

## Measurements
To use this package, you need to pre-define some measurements and add `Field` and `Tag` objects to them.  

## Fields
You need to define some fields to write data for. A good example of a field is `duration`.  

## Tags
You don't have to define any tags to use the datalogger, but if you are going to take measurements that are taken with differing circumstances you   

## Logging
There are different ways of logging data. This section will explore a few options to use.

### Continuous write
By default, the datalogger doesn't call `write_data` on the database writers configured for the datalogger whenever data is logged. This means the user has to decide when the data is written to the database.
If you want the data to be written continuously, you may create the datalogger object using the variable `continuous_write=True`. This will write the data to the database whenever the function `log` is called.
Note that this function is called inside both `measure` and `measure_block`. 

### `log`
The function `log` in the datalogger is the most basic way of logging the data. You will essentially make the measurements yourself. 
You can use other functions that take the measurements for you if you want to measure durations. If you want to take other measurements, you'll need to use this function.  

### `measure`
The function `measure` on the datalogger is meant to wrap an existing function and essentially execute it and measure the time it takes to run the function. 

#### Example
The following example is from the tests in the repository
```python
class DbWriter(influxdb_datalogger.DatabaseWriter):
    def write_data(self, datalogger: influxdb_datalogger.DataLogger):
        dataset = datalogger.dataset
        if os.path.exists(DATA_FILE):
            # If the file exists we are probably writing more than once in a test.
            # Since DbWriter just writes to a JSON file we need to essentially append to the existing data, which is what this does.

            loaded_dataset = json.load(open(DATA_FILE))
            dataset = [*loaded_dataset, *dataset]
        json.dump(dataset, open(DATA_FILE, "w"), indent=2)


def test_measure():
    f = influxdb_datalogger.Field("duration")
    t = influxdb_datalogger.Tag("identifier")
    m = influxdb_datalogger.Measurement("time-taken", f, t)
    tm = influxdb_datalogger.TagMap.build(t, "test")
    datalogger = influxdb_datalogger.DataLogger(DbWriter())

    def runner(arg1):
        logger.info(f"Taking measurement {m}: {arg1}")

    datalogger.measure(func=runner,
                       measurement=m,
                       field=f,
                       tag_map=tm,
                       logger=logger,
                       log_start=f"Starting {runner.__name__}",
                       log_end=f"Finished {runner.__name__}",
                       args=("test",))

    assert m in datalogger._dataset, f"Measurement {m} not in the dataset"
```

### `measure_block`
Unlike `measure`, this function leverages the `with` keyword in Python to measure a block of code that is executed within the scope. 

#### Example
The following example is from the tests in the repository
```python
class DbWriter(influxdb_datalogger.DatabaseWriter):
    def write_data(self, datalogger: influxdb_datalogger.DataLogger):
        dataset = datalogger.dataset
        if os.path.exists(DATA_FILE):
            # If the file exists we are probably writing more than once in a test.
            # Since DbWriter just writes to a JSON file we need to essentially append to the existing data, which is what this does.

            loaded_dataset = json.load(open(DATA_FILE))
            dataset = [*loaded_dataset, *dataset]
        json.dump(dataset, open(DATA_FILE, "w"), indent=2)

def test_measure_block():
    f = influxdb_datalogger.Field("duration")
    t = influxdb_datalogger.Tag("identifier")
    m = influxdb_datalogger.Measurement("time-taken", f, t)
    tm = influxdb_datalogger.TagMap.build(t, "test")
    datalogger = influxdb_datalogger.DataLogger()
    with datalogger.measure_block(m, f, tm):
        logger.info(f"Taking measurement {m}")
    
    assert m in datalogger._dataset, f"Measurement {m} not in the dataset"
    logger.info(datalogger._dataset)
```

### Events
It's possible to log events that happen which can essentially be used as event markers in something like Grafana to see when measurements are made that execute some code or runs some heavy processes.

Events may be written using the function `log_event` on the datalogger, but this is not recommended. `log_event` doesn't care about `continuous_write`, and it's also a lot more complicated to log the events manually. 
The recommended way to use events is to use either `measure` or `measure_block`. 

#### Example
The following example is from the tests in the repository
```python
class GrafanaEventWriter(influxdb_datalogger.DatabaseWriter):
    def write_data(self, datalogger: influxdb_datalogger.DataLogger):
        events = datalogger.events
        events_to_write = list()
        logger.info(events)
        for event in events:
            event: influxdb_datalogger.datalogger.Event
            marker_data = dict(time=int(event.start * 1000), timeEnd=int(event.stop * 1000), tags=event.tag_map, text=event.measurement)
            events_to_write.append(marker_data)

        if os.path.exists(EVENT_FILE):
            # If the file exists we are probably writing more than once in a test.
            # Since DbWriter just writes to a JSON file we need to essentially append to the existing data, which is what this does.

            loaded_events = json.load(open(EVENT_FILE))
            events_to_write = [*loaded_events, *events_to_write]
        json.dump(events_to_write, open(EVENT_FILE, "w"), indent=2)

def test_events():
    f = influxdb_datalogger.Field("duration")
    t = influxdb_datalogger.Tag("identifier")
    h = influxdb_datalogger.Tag("hostname")

    m = influxdb_datalogger.Measurement("time-taken", f, t)
    etm = influxdb_datalogger.TagMap.build(h, socket.gethostname())

    datalogger = influxdb_datalogger.DataLogger(DbWriter(), GrafanaEventWriter())

    with datalogger.measure_block(m, f, influxdb_datalogger.TagMap.build(t, "first"), event_tags=etm):
        logger.info(f"Taking first measurement and logging events {m}")

    with datalogger.measure_block(m, f, influxdb_datalogger.TagMap.build(t, "second"), event_tags=etm):
        logger.info(f"Taking second measurement and logging events {m}")

    with datalogger.measure_block(m, f, influxdb_datalogger.TagMap.build(t, "third")):
        logger.info(f"Taking third measurement and NOT logging events {m}")

    self.assert_event_file_doesnt_exist()

    datalogger.write_data()

    loaded_events = self.load_events_from_event_file()
    logger.info(loaded_events)
    assert len(loaded_events) == 2
```
