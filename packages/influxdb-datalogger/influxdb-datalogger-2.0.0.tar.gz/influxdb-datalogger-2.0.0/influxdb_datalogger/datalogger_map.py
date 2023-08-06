from abc import abstractmethod


class DataLoggerMap(dict):

    @property
    @abstractmethod
    def key_type(self):
        raise NotImplementedError()

    def __init__(self, kwargs=None):
        if kwargs:
            super(DataLoggerMap, self).__init__(kwargs)
        else:
            super(DataLoggerMap, self).__init__()

    @classmethod
    def build(cls, *items):
        assert len(items) % 2 == 0, "The number of items must be even in order to make pairs."
        dlm = cls()

        paired_items = list()
        assert len(items) % 2 == 0, "The number of items to build pairs is not even; In order to build pairs from a list of items, math mandates an even number of items."
        for i, item in enumerate(items):
            # if i == i, then i - 1 == 0;
            # e.g. items[i - 1] is the name of the field/tag and items[i] is the value.
            if i % 2 != 0:
                name = items[i - 1]
                value = items[i]
                assert isinstance(name, dlm.key_type) and not isinstance(value, dlm.key_type), f"The pairs must be on the format: ({dlm.key_type}, (int, float, str, etc, but NOT {dlm.key_type}))"
                paired_items.append((name, value))

        for pair in paired_items:
            assert isinstance(pair, tuple)
            dlm.update({pair[0]: pair[1]})

        return dlm
