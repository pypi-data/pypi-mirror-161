import numpy as np

from sarus.dataspec_wrapper import DataSpecWrapper


class Bool(DataSpecWrapper[np.bool_]):
    ...


class Byte(DataSpecWrapper[np.byte]):
    ...


class UByte(DataSpecWrapper[np.ubyte]):
    ...


class Short(DataSpecWrapper[np.short]):
    ...


class UShort(DataSpecWrapper[np.ushort]):
    ...


class Intc(DataSpecWrapper[np.intc]):
    ...


class UIntc(DataSpecWrapper[np.uintc]):
    ...


class Int_(DataSpecWrapper[np.int_]):
    ...


class UInt_(DataSpecWrapper[np.uint]):
    ...


class LongLong(DataSpecWrapper[np.longlong]):
    ...


class ULongLong(DataSpecWrapper[np.ulonglong]):
    ...


class Single(DataSpecWrapper[np.single]):
    ...


class Double(DataSpecWrapper[np.double]):
    ...


class LongDouble(DataSpecWrapper[np.longdouble]):
    ...


class CSingle(DataSpecWrapper[np.csingle]):
    ...


class CDouble(DataSpecWrapper[np.cdouble]):
    ...


class CLongDouble(DataSpecWrapper[np.clongdouble]):
    ...
