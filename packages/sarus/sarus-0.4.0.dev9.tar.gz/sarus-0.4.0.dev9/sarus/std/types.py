from sarus.dataspec_wrapper import DataSpecWrapper


class List(DataSpecWrapper[list]):
    ...


class Tuple(DataSpecWrapper[tuple]):
    ...


class Int(DataSpecWrapper[int]):
    ...


class Float(DataSpecWrapper[float]):
    ...


class String(DataSpecWrapper[str]):
    ...
