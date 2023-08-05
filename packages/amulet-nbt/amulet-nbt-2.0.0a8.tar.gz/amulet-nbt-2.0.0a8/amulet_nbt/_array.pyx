## This file is generated by tempita. Do not modify this file directly or your changes will get overwritten.
## To edit this file edit the template in template/src

import numpy
cimport numpy
from io import BytesIO
from copy import deepcopy
import warnings

from . import __major__
from ._value cimport AbstractBaseMutableTag
from ._const cimport CommaSpace, ID_BYTE_ARRAY, ID_INT_ARRAY, ID_LONG_ARRAY
from ._util cimport write_array, BufferContext, read_int, read_data
if __major__ <= 2:
    from ._util import primitive_conversion
from ._dtype import EncoderType


cdef class AbstractBaseArrayTag(AbstractBaseMutableTag):
    def __getitem__(AbstractBaseArrayTag self, item):
        raise NotImplementedError

    def __setitem__(AbstractBaseArrayTag self, key, value):
        raise NotImplementedError

    def __array__(AbstractBaseArrayTag self, dtype=None):
        raise NotImplementedError

    def __len__(AbstractBaseArrayTag self):
        raise NotImplementedError

    @property
    def np_array(AbstractBaseArrayTag self):
        """
        A numpy array holding the same internal data.
        Changes to the array will also modify the internal state.
        """
        raise NotImplementedError

    @property
    def py_data(self):
        """
        A python representation of the class. Note that the return type is undefined and may change in the future.
        You would be better off using the py_{type} or np_array properties if you require a fixed type.
        This is here for convenience to get a python representation under the same property name.
        """
        return self.np_array


cdef inline ByteArrayTag read_byte_array_tag(BufferContext buffer, bint little_endian):
    cdef ByteArrayTag tag = ByteArrayTag.__new__(ByteArrayTag)
    cdef int length = read_int(buffer, little_endian)
    cdef int byte_length = length * 1
    cdef char*arr = read_data(buffer, byte_length)
    data_type = numpy.dtype("int8") if little_endian else numpy.dtype("int8")
    tag.value_ = numpy.array(numpy.frombuffer(arr[:byte_length], dtype=data_type, count=length), numpy.dtype("int8")).ravel()
    return tag


cdef class ByteArrayTag(AbstractBaseArrayTag):
    """This class behaves like an 1D Numpy signed integer array with each value stored in a byte."""
    tag_id = ID_BYTE_ARRAY

    def __init__(ByteArrayTag self, object value = ()):
        self.value_ = numpy.asarray(value, numpy.dtype("int8")).ravel()

    cdef str _to_snbt(ByteArrayTag self):
        cdef long long elem
        cdef list tags = []
        for elem in self.value_:
            tags.append(f"{elem}B")
        return f"[B;{CommaSpace.join(tags)}]"

    cdef void write_payload(
        ByteArrayTag self,
        object buffer: BytesIO,
        bint little_endian,
        string_encoder: EncoderType,
    ) except *:
        write_array(
            numpy.asarray(self.value_, numpy.dtype("int8") if little_endian else numpy.dtype("int8")),
            buffer,
            1,
            little_endian
        )

    def __str__(ByteArrayTag self):
        return str(self.value_)

    def __reduce__(ByteArrayTag self):
        return self.__class__, (self.value_,)

    def __deepcopy__(ByteArrayTag self, memo=None):
        return self.__class__(deepcopy(self.value_, memo=memo))

    def __copy__(ByteArrayTag self):
        return self.__class__(self.value_)

    @property
    def np_array(ByteArrayTag self):
        """
        A numpy array holding the same internal data.
        Changes to the array will also modify the internal state.
        """
        return self.value_

    def __repr__(ByteArrayTag self):
        return f"{self.__class__.__name__}({list(self.value_)})"

    def __eq__(ByteArrayTag self, other):
        cdef ByteArrayTag other_
        if isinstance(other, ByteArrayTag):
            other_ = other
            return numpy.array_equal(self.value_, other_.value_)
        elif __major__ <= 2 and isinstance(other, AbstractBaseArrayTag):
            warnings.warn("NBT comparison operator (a == b) will only return True between classes of the same type.", FutureWarning)
            return numpy.array_equal(self.value_, primitive_conversion(other))
        return NotImplemented

    def __getitem__(ByteArrayTag self, item):
        return self.value_.__getitem__(item)

    def __setitem__(ByteArrayTag self, key, value):
        self.value_.__setitem__(key, value)

    def __array__(ByteArrayTag self, dtype=None):
        return numpy.asarray(self.value_, dtype=dtype)

    def __len__(ByteArrayTag self):
        return len(self.value_)

    if __major__ <= 2:
        def __add__(self, other):
            warnings.warn(f"__add__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) + primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __sub__(self, other):
            warnings.warn(f"__sub__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) - primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __mul__(self, other):
            warnings.warn(f"__mul__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) * primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __matmul__(self, other):
            warnings.warn(f"__matmul__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) @ primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __truediv__(self, other):
            warnings.warn(f"__truediv__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) / primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __floordiv__(self, other):
            warnings.warn(f"__floordiv__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) // primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __mod__(self, other):
            warnings.warn(f"__mod__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) % primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __divmod__(self, other):
            warnings.warn(f"__divmod__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return divmod(primitive_conversion(self), primitive_conversion(other))

        def __pow__(self, power, modulo):
            warnings.warn(f"__pow__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return pow(primitive_conversion(self), power, modulo).astype(numpy.dtype("int8"))

        def __lshift__(self, other):
            warnings.warn(f"__lshift__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) << primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __rshift__(self, other):
            warnings.warn(f"__rshift__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) >> primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __and__(self, other):
            warnings.warn(f"__and__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) & primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __xor__(self, other):
            warnings.warn(f"__xor__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) ^ primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __or__(self, other):
            warnings.warn(f"__or__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) | primitive_conversion(other)).astype(numpy.dtype("int8"))

        def __radd__(self, other):
            warnings.warn(f"__radd__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) + primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rsub__(self, other):
            warnings.warn(f"__rsub__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) - primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rmul__(self, other):
            warnings.warn(f"__rmul__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) * primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rtruediv__(self, other):
            warnings.warn(f"__rtruediv__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) / primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rfloordiv__(self, other):
            warnings.warn(f"__rfloordiv__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) // primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rmod__(self, other):
            warnings.warn(f"__rmod__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) % primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rdivmod__(self, other):
            warnings.warn(f"__rdivmod__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return divmod(primitive_conversion(other), primitive_conversion(self))

        def __rpow__(self, other, modulo):
            warnings.warn(f"__rpow__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return pow(primitive_conversion(other), primitive_conversion(self), modulo).astype(numpy.dtype("int8"))

        def __rlshift__(self, other):
            warnings.warn(f"__rlshift__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) << primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rrshift__(self, other):
            warnings.warn(f"__rrshift__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) >> primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rand__(self, other):
            warnings.warn(f"__rand__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) & primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __rxor__(self, other):
            warnings.warn(f"__rxor__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) ^ primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __ror__(self, other):
            warnings.warn(f"__ror__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) | primitive_conversion(self)).astype(numpy.dtype("int8"))

        def __neg__(self):
            warnings.warn(f"__neg__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (-self.value_).astype(numpy.dtype("int8"))

        def __pos__(self):
            warnings.warn(f"__pos__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (+self.value_).astype(numpy.dtype("int8"))

        def __abs__(self):
            warnings.warn(f"__abs__ is depreciated on ByteArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return abs(self.value_).astype(numpy.dtype("int8"))


cdef inline IntArrayTag read_int_array_tag(BufferContext buffer, bint little_endian):
    cdef IntArrayTag tag = IntArrayTag.__new__(IntArrayTag)
    cdef int length = read_int(buffer, little_endian)
    cdef int byte_length = length * 4
    cdef char*arr = read_data(buffer, byte_length)
    data_type = numpy.dtype("<i4") if little_endian else numpy.dtype(">i4")
    tag.value_ = numpy.array(numpy.frombuffer(arr[:byte_length], dtype=data_type, count=length), numpy.int32).ravel()
    return tag


cdef class IntArrayTag(AbstractBaseArrayTag):
    """This class behaves like an 1D Numpy signed integer array with each value stored in a int."""
    tag_id = ID_INT_ARRAY

    def __init__(IntArrayTag self, object value = ()):
        self.value_ = numpy.asarray(value, numpy.int32).ravel()

    cdef str _to_snbt(IntArrayTag self):
        cdef long long elem
        cdef list tags = []
        for elem in self.value_:
            tags.append(f"{elem}")
        return f"[I;{CommaSpace.join(tags)}]"

    cdef void write_payload(
        IntArrayTag self,
        object buffer: BytesIO,
        bint little_endian,
        string_encoder: EncoderType,
    ) except *:
        write_array(
            numpy.asarray(self.value_, numpy.dtype("<i4") if little_endian else numpy.dtype(">i4")),
            buffer,
            4,
            little_endian
        )

    def __str__(IntArrayTag self):
        return str(self.value_)

    def __reduce__(IntArrayTag self):
        return self.__class__, (self.value_,)

    def __deepcopy__(IntArrayTag self, memo=None):
        return self.__class__(deepcopy(self.value_, memo=memo))

    def __copy__(IntArrayTag self):
        return self.__class__(self.value_)

    @property
    def np_array(IntArrayTag self):
        """
        A numpy array holding the same internal data.
        Changes to the array will also modify the internal state.
        """
        return self.value_

    def __repr__(IntArrayTag self):
        return f"{self.__class__.__name__}({list(self.value_)})"

    def __eq__(IntArrayTag self, other):
        cdef IntArrayTag other_
        if isinstance(other, IntArrayTag):
            other_ = other
            return numpy.array_equal(self.value_, other_.value_)
        elif __major__ <= 2 and isinstance(other, AbstractBaseArrayTag):
            warnings.warn("NBT comparison operator (a == b) will only return True between classes of the same type.", FutureWarning)
            return numpy.array_equal(self.value_, primitive_conversion(other))
        return NotImplemented

    def __getitem__(IntArrayTag self, item):
        return self.value_.__getitem__(item)

    def __setitem__(IntArrayTag self, key, value):
        self.value_.__setitem__(key, value)

    def __array__(IntArrayTag self, dtype=None):
        return numpy.asarray(self.value_, dtype=dtype)

    def __len__(IntArrayTag self):
        return len(self.value_)

    if __major__ <= 2:
        def __add__(self, other):
            warnings.warn(f"__add__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) + primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __sub__(self, other):
            warnings.warn(f"__sub__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) - primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __mul__(self, other):
            warnings.warn(f"__mul__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) * primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __matmul__(self, other):
            warnings.warn(f"__matmul__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) @ primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __truediv__(self, other):
            warnings.warn(f"__truediv__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) / primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __floordiv__(self, other):
            warnings.warn(f"__floordiv__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) // primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __mod__(self, other):
            warnings.warn(f"__mod__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) % primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __divmod__(self, other):
            warnings.warn(f"__divmod__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return divmod(primitive_conversion(self), primitive_conversion(other))

        def __pow__(self, power, modulo):
            warnings.warn(f"__pow__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return pow(primitive_conversion(self), power, modulo).astype(numpy.dtype(">i4"))

        def __lshift__(self, other):
            warnings.warn(f"__lshift__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) << primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __rshift__(self, other):
            warnings.warn(f"__rshift__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) >> primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __and__(self, other):
            warnings.warn(f"__and__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) & primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __xor__(self, other):
            warnings.warn(f"__xor__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) ^ primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __or__(self, other):
            warnings.warn(f"__or__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) | primitive_conversion(other)).astype(numpy.dtype(">i4"))

        def __radd__(self, other):
            warnings.warn(f"__radd__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) + primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rsub__(self, other):
            warnings.warn(f"__rsub__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) - primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rmul__(self, other):
            warnings.warn(f"__rmul__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) * primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rtruediv__(self, other):
            warnings.warn(f"__rtruediv__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) / primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rfloordiv__(self, other):
            warnings.warn(f"__rfloordiv__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) // primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rmod__(self, other):
            warnings.warn(f"__rmod__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) % primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rdivmod__(self, other):
            warnings.warn(f"__rdivmod__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return divmod(primitive_conversion(other), primitive_conversion(self))

        def __rpow__(self, other, modulo):
            warnings.warn(f"__rpow__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return pow(primitive_conversion(other), primitive_conversion(self), modulo).astype(numpy.dtype(">i4"))

        def __rlshift__(self, other):
            warnings.warn(f"__rlshift__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) << primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rrshift__(self, other):
            warnings.warn(f"__rrshift__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) >> primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rand__(self, other):
            warnings.warn(f"__rand__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) & primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __rxor__(self, other):
            warnings.warn(f"__rxor__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) ^ primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __ror__(self, other):
            warnings.warn(f"__ror__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) | primitive_conversion(self)).astype(numpy.dtype(">i4"))

        def __neg__(self):
            warnings.warn(f"__neg__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (-self.value_).astype(numpy.dtype(">i4"))

        def __pos__(self):
            warnings.warn(f"__pos__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (+self.value_).astype(numpy.dtype(">i4"))

        def __abs__(self):
            warnings.warn(f"__abs__ is depreciated on IntArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return abs(self.value_).astype(numpy.dtype(">i4"))


cdef inline LongArrayTag read_long_array_tag(BufferContext buffer, bint little_endian):
    cdef LongArrayTag tag = LongArrayTag.__new__(LongArrayTag)
    cdef int length = read_int(buffer, little_endian)
    cdef int byte_length = length * 8
    cdef char*arr = read_data(buffer, byte_length)
    data_type = numpy.dtype("<i8") if little_endian else numpy.dtype(">i8")
    tag.value_ = numpy.array(numpy.frombuffer(arr[:byte_length], dtype=data_type, count=length), numpy.int64).ravel()
    return tag


cdef class LongArrayTag(AbstractBaseArrayTag):
    """This class behaves like an 1D Numpy signed integer array with each value stored in a long."""
    tag_id = ID_LONG_ARRAY

    def __init__(LongArrayTag self, object value = ()):
        self.value_ = numpy.asarray(value, numpy.int64).ravel()

    cdef str _to_snbt(LongArrayTag self):
        cdef long long elem
        cdef list tags = []
        for elem in self.value_:
            tags.append(f"{elem}L")
        return f"[L;{CommaSpace.join(tags)}]"

    cdef void write_payload(
        LongArrayTag self,
        object buffer: BytesIO,
        bint little_endian,
        string_encoder: EncoderType,
    ) except *:
        write_array(
            numpy.asarray(self.value_, numpy.dtype("<i8") if little_endian else numpy.dtype(">i8")),
            buffer,
            8,
            little_endian
        )

    def __str__(LongArrayTag self):
        return str(self.value_)

    def __reduce__(LongArrayTag self):
        return self.__class__, (self.value_,)

    def __deepcopy__(LongArrayTag self, memo=None):
        return self.__class__(deepcopy(self.value_, memo=memo))

    def __copy__(LongArrayTag self):
        return self.__class__(self.value_)

    @property
    def np_array(LongArrayTag self):
        """
        A numpy array holding the same internal data.
        Changes to the array will also modify the internal state.
        """
        return self.value_

    def __repr__(LongArrayTag self):
        return f"{self.__class__.__name__}({list(self.value_)})"

    def __eq__(LongArrayTag self, other):
        cdef LongArrayTag other_
        if isinstance(other, LongArrayTag):
            other_ = other
            return numpy.array_equal(self.value_, other_.value_)
        elif __major__ <= 2 and isinstance(other, AbstractBaseArrayTag):
            warnings.warn("NBT comparison operator (a == b) will only return True between classes of the same type.", FutureWarning)
            return numpy.array_equal(self.value_, primitive_conversion(other))
        return NotImplemented

    def __getitem__(LongArrayTag self, item):
        return self.value_.__getitem__(item)

    def __setitem__(LongArrayTag self, key, value):
        self.value_.__setitem__(key, value)

    def __array__(LongArrayTag self, dtype=None):
        return numpy.asarray(self.value_, dtype=dtype)

    def __len__(LongArrayTag self):
        return len(self.value_)

    if __major__ <= 2:
        def __add__(self, other):
            warnings.warn(f"__add__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) + primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __sub__(self, other):
            warnings.warn(f"__sub__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) - primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __mul__(self, other):
            warnings.warn(f"__mul__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) * primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __matmul__(self, other):
            warnings.warn(f"__matmul__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) @ primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __truediv__(self, other):
            warnings.warn(f"__truediv__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) / primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __floordiv__(self, other):
            warnings.warn(f"__floordiv__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) // primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __mod__(self, other):
            warnings.warn(f"__mod__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) % primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __divmod__(self, other):
            warnings.warn(f"__divmod__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return divmod(primitive_conversion(self), primitive_conversion(other))

        def __pow__(self, power, modulo):
            warnings.warn(f"__pow__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return pow(primitive_conversion(self), power, modulo).astype(numpy.dtype(">i8"))

        def __lshift__(self, other):
            warnings.warn(f"__lshift__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) << primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __rshift__(self, other):
            warnings.warn(f"__rshift__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) >> primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __and__(self, other):
            warnings.warn(f"__and__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) & primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __xor__(self, other):
            warnings.warn(f"__xor__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) ^ primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __or__(self, other):
            warnings.warn(f"__or__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(self) | primitive_conversion(other)).astype(numpy.dtype(">i8"))

        def __radd__(self, other):
            warnings.warn(f"__radd__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) + primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rsub__(self, other):
            warnings.warn(f"__rsub__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) - primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rmul__(self, other):
            warnings.warn(f"__rmul__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) * primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rtruediv__(self, other):
            warnings.warn(f"__rtruediv__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) / primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rfloordiv__(self, other):
            warnings.warn(f"__rfloordiv__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) // primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rmod__(self, other):
            warnings.warn(f"__rmod__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) % primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rdivmod__(self, other):
            warnings.warn(f"__rdivmod__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return divmod(primitive_conversion(other), primitive_conversion(self))

        def __rpow__(self, other, modulo):
            warnings.warn(f"__rpow__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return pow(primitive_conversion(other), primitive_conversion(self), modulo).astype(numpy.dtype(">i8"))

        def __rlshift__(self, other):
            warnings.warn(f"__rlshift__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) << primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rrshift__(self, other):
            warnings.warn(f"__rrshift__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) >> primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rand__(self, other):
            warnings.warn(f"__rand__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) & primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __rxor__(self, other):
            warnings.warn(f"__rxor__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) ^ primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __ror__(self, other):
            warnings.warn(f"__ror__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (primitive_conversion(other) | primitive_conversion(self)).astype(numpy.dtype(">i8"))

        def __neg__(self):
            warnings.warn(f"__neg__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (-self.value_).astype(numpy.dtype(">i8"))

        def __pos__(self):
            warnings.warn(f"__pos__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return (+self.value_).astype(numpy.dtype(">i8"))

        def __abs__(self):
            warnings.warn(f"__abs__ is depreciated on LongArrayTag and will be removed in the future. Please use .np_array to achieve the same behaviour.", DeprecationWarning)
            return abs(self.value_).astype(numpy.dtype(">i8"))