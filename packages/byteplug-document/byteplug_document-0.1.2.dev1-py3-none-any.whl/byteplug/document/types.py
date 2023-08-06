# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, June 2022

class Type:
    def __init__(self, name=None, description=None, option=None) -> None:
        self.name = name
        self.description = description
        self.option = option

    def update_object(self, object):
        if self.name:
            object['name'] = self.name
        if self.description:
            object['description'] = self.description
        if self.option:
            object['option'] = True

class Flag(Type):
    def __init__(self, **kwargs) -> None:
        Type.__init__(self, **kwargs)

    def to_object(self):
        object = {'type': 'flag'}

        Type.update_object(self, object)
        return object

class Integer(Type):
    def __init__(self, min=None, max=None, **kwargs) -> None:
        Type.__init__(self, **kwargs)

        # Integer(min=42)
        # Integer(min=(42, True))
        # Integer(min=(42, False))
        # Integer(max=42)
        # Integer(max=(42, True))
        # Integer(max=(42, False))
        if min:
            assert type(min) in [int, tuple], "min value is invalid"
            if type(min) is tuple:
                assert type(min[0]) is int, "min value in invalid"
                assert type(min[1]) is bool, "min value in invalid"

        if max:
            assert type(max) in [int, tuple], "max value is invalid"
            if type(max) is tuple:
                assert type(max[0]) is int, "max value in invalid"
                assert type(max[1]) is bool, "max value in invalid"

        self.minimum = min
        self.maximum = max

    def to_object(self):
        object = {'type': 'integer'}

        if self.minimum:
            if type(self.minimum) is int:
                object['minimum'] = self.minimum
            else:
                object['minimum'] = {
                    'exclusive': self.minimum[1],
                    'value': self.minimum[0]
                }

        if self.maximum:
            if type(self.maximum) is int:
                object['maximum'] = self.maximum
            else:
                object['maximum'] = {
                    'exclusive': self.maximum[1],
                    'value': self.maximum[0]
                }

        Type.update_object(self, object)
        return object

class Decimal(Type):
    def __init__(self, min=None, max=None, **kwargs) -> None:
        Type.__init__(self, **kwargs)

        # Decimal(min=42.5)
        # Decimal(min=(42.5, True))
        # Decimal(min=(42.5, False))
        # Decimal(max=42.5)
        # Decimal(max=(42.5, True))
        # Decimal(max=(42.5, False))
        if min:
            assert type(min) in [int, float, tuple], "min value is invalid"

            if type(min) is int:
                min = float(min)

            if type(min) is tuple:
                assert type(min[0]) in [int, float], "min value in invalid"

                if type(min[0]) is int:
                    min[0] = float(min[0])

                assert type(min[1]) is bool, "min value in invalid"

        if max:
            assert type(max) in [int, float, tuple], "max value is invalid"

            if type(max) is int:
                max = float(max)

            if type(max) is tuple:
                assert type(max[0]) in [int, float], "max value in invalid"

                if type(max[0]) is int:
                    max[0] = float(max[0])

                assert type(max[1]) is bool, "max value in invalid"

        self.minimum = min
        self.maximum = max

    def to_object(self):
        object = {'type': 'decimal'}

        if self.minimum:
            if type(self.minimum) is float:
                object['minimum'] = self.minimum
            else:
                object['minimum'] = {
                    'exclusive': self.minimum[1],
                    'value': self.minimum[0]
                }

        if self.maximum:
            if type(self.maximum) is float:
                object['maximum'] = self.maximum
            else:
                object['maximum'] = {
                    'exclusive': self.maximum[1],
                    'value': self.maximum[0]
                }

        Type.update_object(self, object)
        return object

class String(Type):
    def __init__(self, length=None, pattern=None, **kwargs) -> None:
        Type.__init__(self, **kwargs)
        # String(length=42)
        # String(length=(42, None))
        # String(length=(None, 42))
        # String(length=(42, 42))

        if length:
            assert type(length) in [int, tuple], "length value is invalid"
            if type(length) is tuple:
                assert length[0] is None or type(length[0]) is int, "length value in invalid"
                assert length[1] is None or type(length[1]) is int, "length value in invalid"

        self.length = length
        self.pattern = pattern

    def to_object(self):
        object = {'type': 'string'}
        if self.length:
            if type(self.length) is int:
                object['length'] = self.length
            else:
                length = {}
                if self.length[0] is not None:
                    length['minimum'] = self.length[0]
                if self.length[1] is not None:
                    length['maximum'] = self.length[1]
                object['length'] = length
        if self.pattern:
            object['pattern'] = self.pattern

        Type.update_object(self, object)
        return object

class Enum(Type):
    def __init__(self, values, **kwargs) -> None:
        Type.__init__(self, **kwargs)
        self.values = values

    def to_object(self):
        object = {'type': 'enum'}
        object['values'] = list(self.values)

        Type.update_object(self, object)
        return object

class List(Type):
    def __init__(self, value, length=None, **kwargs) -> None:
        Type.__init__(self, **kwargs)

        assert isinstance(value, Type), "value type is invalid"
        self.value = value

        if length:
            assert type(length) in [int, tuple], "length value is invalid"
            if type(length) is tuple:
                assert length[0] is None or type(length[0]) is int, "length value in invalid"
                assert length[1] is None or type(length[1]) is int, "length value in invalid"

        self.length = length

    def to_object(self):
        object = {'type': 'list'}
        object['value'] = self.value.to_object()
        if self.length:
            if type(self.length) is int:
                object['length'] = self.length
            else:
                length = {}
                if self.length[0] is not None:
                    length['minimum'] = self.length[0]
                if self.length[1] is not None:
                    length['maximum'] = self.length[1]
                object['length'] = length

        Type.update_object(self, object)
        return object

class Tuple(Type):
    def __init__(self, values, **kwargs) -> None:
        Type.__init__(self, **kwargs)

        assert type(values) in [list, tuple], "values type is invalid"
        for value in values:
            assert isinstance(value, Type), "one of the value is invalid"

        self.values = values

    def to_object(self):
        object = {'type': 'tuple'}
        object['values'] = list(map(lambda value: value.to_object(), self.values))

        Type.update_object(self, object)
        return object

class Map(Type):
    def __init__(self, fields, **kwargs) -> None:
        Type.__init__(self, **kwargs)

        assert type(fields) is dict, "fields type is invalid"
        for key, value in fields.items():
            assert type(key) is str, "one of the value is invalid"
            assert isinstance(value, Type), "one of the value is invalid"

        self.fields = fields

    def to_object(self):
        object = {'type': 'map'}
        object['fields'] = {key: value.to_object() for key, value in self.fields.items()}

        Type.update_object(self, object)
        return object
