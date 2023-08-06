from __future__ import annotations

import datetime
import json
import typing as t

import numpy as np
import pandas as pd
import pyarrow as pa

from sarus_data_spec.base import Base
from sarus_data_spec.constants import (
    ARRAY_VALUES,
    LIST_VALUES,
    OPTIONAL_VALUE,
    TEXT_CHARSET,
    TEXT_MAX_LENGTH,
)
from sarus_data_spec.path import Path
from sarus_data_spec.predicate import Predicate
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as sdt

try:
    import tensorflow as tf
except ModuleNotFoundError:
    pass


class Type(Base[sp.Type]):
    """A python class to describe types"""

    def prototype(self) -> t.Type[sp.Type]:
        """Return the type of the underlying protobuf."""
        return sp.Type

    def name(self) -> str:
        """Returns the name of the underlying protobuf."""
        return self.protobuf().name

    # A Visitor acceptor
    def accept(self, visitor: sdt.TypeVisitor) -> None:
        dispatch: t.Callable[[], None] = {
            'null': visitor.Null,
            'unit': visitor.Unit,
            'boolean': visitor.Boolean,
            'integer': lambda: visitor.Integer(
                min=self._protobuf.integer.min,
                max=self._protobuf.integer.max,
                base=sdt.IntegerBase(self._protobuf.integer.base),
            ),
            'id': lambda: visitor.Id(
                base=sdt.IdBase(self._protobuf.id.base),
                unique=self._protobuf.id.unique,
                reference=Path(self._protobuf.id.reference)
                if self._protobuf.id.reference != sp.Path()
                else None,
            ),
            'enum': lambda: visitor.Enum(
                self._protobuf.name,
                [
                    (name_value.name, name_value.value)
                    for name_value in self._protobuf.enum.name_values
                ],
                self._protobuf.enum.ordered,
            ),
            'float': lambda: visitor.Float(
                min=self._protobuf.float.min,
                max=self._protobuf.float.max,
                base=sdt.FloatBase(self._protobuf.float.base),
            ),
            'text': lambda: visitor.Text(self._protobuf.text.encoding),
            'bytes': visitor.Bytes,
            'struct': lambda: visitor.Struct(
                {
                    field.name: Type(field.type)
                    for field in self._protobuf.struct.fields
                },
                name=None
                if self._protobuf.name == ''
                else self._protobuf.name,
            ),
            'union': lambda: visitor.Union(
                {
                    field.name: Type(field.type)
                    for field in self._protobuf.union.fields
                },
                name=None
                if self._protobuf.name == ''
                else self._protobuf.name,
            ),
            'optional': lambda: visitor.Optional(
                Type(self._protobuf.optional.type),
                None if self._protobuf.name == '' else self._protobuf.name,
            ),
            'list': lambda: visitor.List(
                Type(self._protobuf.list.type),
                max_size=self._protobuf.list.max_size,
                name=None
                if self._protobuf.name == ''
                else self._protobuf.name,
            ),
            'array': lambda: visitor.Array(
                Type(self._protobuf.array.type),
                tuple(self._protobuf.array.shape),
                None if self._protobuf.name == '' else self._protobuf.name,
            ),
            'datetime': lambda: visitor.Datetime(
                self._protobuf.datetime.format,
                self._protobuf.datetime.min,
                self._protobuf.datetime.max,
                sdt.DatetimeBase(self._protobuf.datetime.base),
            ),
            'constrained': lambda: visitor.Constrained(
                Type(self._protobuf.constrained.type),
                Predicate(self._protobuf.constrained.constraint),
                None if self._protobuf.name == '' else self._protobuf.name,
            ),
            'hypothesis': lambda: visitor.Hypothesis(
                *[
                    (Type(scored.type), scored.score)
                    for scored in self._protobuf.hypothesis.types
                ],
                name=None
                if self._protobuf.name == ''
                else self._protobuf.name,
            ),
            None: lambda: None,
        }[self._protobuf.WhichOneof('type')]
        dispatch()

    def latex(self: sdt.Type, parenthesized: bool = False) -> str:
        """return a latex representation of the type"""

        class Latex(sdt.TypeVisitor):
            result: str = ''

            def Null(self) -> None:
                self.result = r'\emptyset'

            def Unit(self) -> None:
                self.result = r'\mathbb{1}'

            def Boolean(self) -> None:
                self.result = r'\left\{0,1\right}'

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                if (
                    min <= np.iinfo(np.int32).min
                    or max >= np.iinfo(np.int32).max
                ):
                    self.result = r'\mathbb{N}'
                else:
                    self.result = (
                        r'\left[' + str(min) + r'..' + str(max) + r'\right]'
                    )

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                if len(name_values) > 3:
                    self.result = r'\left\{'
                    for name, _ in name_values[:2]:
                        self.result += r'\text{' + name + r'}, '
                    self.result += r',\ldots, '
                    for name, _ in name_values[-1:]:
                        self.result += r'\text{' + name + r'}, '
                    self.result = self.result[:-2] + r'\right\}'
                elif len(name_values) > 0:
                    self.result = r'\left\{'
                    for name, _ in name_values:
                        self.result += r'\text{' + name + r'}, '
                    self.result = self.result[:-2] + r'\right\}'
                else:
                    self.Unit()

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                if (
                    min <= np.finfo(np.float32).min
                    or max >= np.finfo(np.float32).max
                ):
                    self.result = r'\mathbb{R}'
                else:
                    self.result = (
                        r'\left[' + str(min) + r', ' + str(max) + r'\right]'
                    )

            def Text(self, encoding: str) -> None:
                self.result = r'\text{Text}'

            def Bytes(self) -> None:
                self.result = r'\text{Bytes}'

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                if len(fields) > 0:
                    if name is None:
                        self.result = r'\left\{'
                    else:
                        self.result = r'\text{' + name + r'}: \left\{'
                    for type_name, type in fields.items():
                        self.result = (
                            self.result
                            + r'\text{'
                            + type_name
                            + r'}:'
                            + Type.latex(type, parenthesized=True)
                            + r', '
                        )
                    self.result = self.result[:-2] + r'\right\}'
                else:
                    self.Unit()

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                if len(fields) > 0:
                    for type in fields.values():
                        self.result = (
                            self.result
                            + Type.latex(type, parenthesized=True)
                            + r' | '
                        )
                    self.result = self.result[:-2]
                    if parenthesized:
                        self.result = r'\left(' + self.result + r'\right)'
                else:
                    self.Null()

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = Type.latex(type, parenthesized=True) + r'?'

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                if max_size < 100:
                    self.result = (
                        Type.latex(type, parenthesized=True)
                        + r'^{'
                        + str(max_size)
                        + r'}'
                    )
                else:
                    self.result = Type.latex(type, parenthesized=True) + r'^*'

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = (
                    Type.latex(type)
                    + r'^{'
                    + r'\times '.join([str(i) for i in shape])
                    + r'}'
                )

            def Datetime(
                self,
                format: str,
                min: str,
                max: str,
                base: sdt.DatetimeBase,
            ) -> None:
                self.result = r'\text{Date}'

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:
                if len(types) > 0:
                    for type, score in types:
                        self.result = (
                            self.result
                            + Type.latex(type, parenthesized=True)
                            + f',{score}|'
                        )
                    self.result = self.result[:-2]
                    self.result = r'\langle' + self.result + r'\rangle'
                else:
                    self.Null()

        visitor = Latex()
        self.accept(visitor)
        return visitor.result

    def compact(self: sdt.Type, parenthesized: bool = False) -> str:
        """return a compact representation of the type"""

        class Compact(sdt.TypeVisitor):
            result: str = ''

            def Null(self) -> None:
                self.result = r'∅'
                self.result = r'∅'

            def Unit(self) -> None:
                self.result = r'𝟙'

            def Boolean(self) -> None:
                self.result = r'𝔹'

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                if (
                    min <= np.iinfo(np.int32).min
                    or max >= np.iinfo(np.int32).max
                ):
                    self.result = r'ℕ'
                else:
                    self.result = r'[' + str(min) + r'..' + str(max) + r']'

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                if len(name_values) > 3:
                    self.result = r'{'
                    for name, _ in name_values[:2]:
                        self.result += name
                    self.result += r',..., '
                    for name, _ in name_values[-1:]:
                        self.result += name + r', '
                    self.result = self.result[:-2] + r'}'
                elif len(name_values) > 0:
                    self.result = r'{'
                    for name, _ in name_values:
                        self.result += name + r', '
                    self.result = self.result[:-2] + r'}'
                else:
                    self.Unit()

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                if (
                    min <= np.finfo(np.float32).min
                    or max >= np.finfo(np.float32).max
                ):
                    self.result = r'ℝ'
                else:
                    self.result = r'[' + str(min) + r', ' + str(max) + r']'

            def Text(self, encoding: str) -> None:
                self.result = r'𝒯'

            def Bytes(self) -> None:
                self.result = r'ℬ'

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                if len(fields) > 0:
                    if name is None:
                        self.result = '{'
                    else:
                        self.result = name + r': {'
                    for type_name, type in fields.items():
                        self.result = (
                            self.result
                            + type_name
                            + r': '
                            + Type.compact(type, parenthesized=True)
                            + r', '
                        )
                    self.result = self.result[:-2] + r'}'
                else:
                    self.Unit()

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                if len(fields) > 0:
                    for type in fields.values():
                        self.result = (
                            self.result
                            + Type.compact(type, parenthesized=True)
                            + r' | '
                        )
                    self.result = self.result[:-2]
                    if parenthesized:
                        self.result = r'(' + self.result + r')'
                else:
                    self.Null()

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = Type.compact(type, parenthesized=True) + r'?'

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                self.result = Type.compact(type, parenthesized=True) + r'*'

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = (
                    Type.compact(type)
                    + r'**('
                    + r'x'.join([str(i) for i in shape])
                    + r')'
                )

            def Datetime(
                self,
                format: str,
                min: str,
                max: str,
                base: sdt.DatetimeBase,
            ) -> None:
                self.result = r'𝒟'

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:
                if len(types) > 0:
                    self.result = r'<'
                    for type, score in types:
                        self.result = (
                            self.result
                            + Type.compact(type, parenthesized=False)
                            + f',{score}|'
                        )
                    self.result = self.result[:-1] + r'>'
                else:
                    self.Null()

        visitor = Compact()
        self.accept(visitor)
        return visitor.result

    def get(self: Type, item: sdt.Path) -> sdt.Type:
        """Return a projection of the considered type defined by the path.
        The projection contains all the parents types of the leaves of
        the path. If the path stops at a Union, Struct or Optional,
        it also returns that type with everything it contains."""

        class Select(sdt.TypeVisitor):
            result = Type(sp.Type())

            def __init__(
                self, properties: t.Optional[t.Mapping[str, str]] = None
            ):
                self.properties = properties

            def Null(self) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Null()

            def Id(
                self,
                unique: bool,
                reference: t.Optional[sdt.Path] = None,
                base: t.Optional[sdt.IdBase] = None,
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Id(base=base, unique=unique, reference=reference)

            def Unit(self) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Unit(properties=self.properties)

            def Boolean(self) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Boolean()

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Integer(
                    min=min, max=max, properties=self.properties
                )

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Enum(
                    name=name,
                    name_values=name_values,
                    ordered=ordered,
                    properties=self.properties,
                )

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Float(
                    min=min, max=max, properties=self.properties
                )

            def Text(self, encoding: str) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Text(
                    encoding=encoding, properties=self.properties
                )

            def Bytes(self) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Bytes()

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                proto = item.protobuf()
                new_fields = {}
                for path in proto.paths:
                    # here struct each path must have a label
                    new_fields[path.label] = fields[path.label].get(Path(path))
                self.result = Struct(
                    fields=new_fields if len(new_fields) > 0 else fields,
                    name=name if name is not None else 'Struct',
                    properties=self.properties,
                )

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                proto = item.protobuf()
                new_fields = {}
                for path in proto.paths:
                    new_fields[path.label] = fields[path.label].get(Path(path))
                self.result = Union(
                    fields=new_fields if len(new_fields) > 0 else fields,
                    name=name if name is not None else 'Union',
                    properties=self.properties,
                )

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:

                proto = item.protobuf()
                assert len(proto.paths) <= 1
                self.result = Optional(
                    type.get(Path(proto.paths[0]))
                    if len(proto.paths) > 0
                    else type,
                    name=t.cast(str, name),
                    properties=self.properties,
                )

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) <= 1
                self.result = List(
                    type.get(Path(proto.paths[0]))
                    if len(proto.paths) > 0
                    else type,
                    name=t.cast(str, name),
                    max_size=max_size,
                    properties=self.properties,
                )

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) <= 1
                self.result = Array(
                    type.get(Path(proto.paths[0]))
                    if len(proto.paths) > 0
                    else type,
                    name=t.cast(str, name),
                    shape=shape,
                    properties=self.properties,
                )

            def Datetime(
                self,
                format: str,
                min: str,
                max: str,
                base: sdt.DatetimeBase,
            ) -> None:
                proto = item.protobuf()
                assert len(proto.paths) == 0
                self.result = Datetime(
                    format=format,
                    min=min,
                    max=max,
                    properties=self.properties,
                    base=base,
                )

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:

                # TODO
                pass

        visitor = Select(properties=self.properties())
        self.accept(visitor)
        return visitor.result

    def sub_types(self: Type, item: sdt.Path) -> t.List[sdt.Type]:
        """Returns a list of the subtypes corresponding to the
        leaves of the input path"""

        class Select(sdt.TypeVisitor):
            def __init__(self, type_item: sdt.Type):
                self.result = [type_item]

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                for sub_path in item.sub_paths():
                    result.extend(fields[sub_path.label()].sub_types(sub_path))
                if len(result) > 0:
                    self.result = result
                    # otherwise struct is empty and it is a terminal node

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                for sub_path in item.sub_paths():
                    result.extend(fields[sub_path.label()].sub_types(sub_path))
                if len(result) > 0:
                    self.result = result
                    # otherwise union is empty and it is a terminal node

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:

                result = []
                if len(item.sub_paths()) == 1:
                    result.extend(type.sub_types(item.sub_paths()[0]))
                    self.result = result

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                if len(item.sub_paths()) == 1:
                    result.extend(type.sub_types(item.sub_paths()[0]))
                    self.result = result

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                if len(item.sub_paths()) == 1:
                    result.extend(type.sub_types(item.sub_paths()[0]))
                    self.result = result

        visitor = Select(type_item=self)
        self.accept(visitor)
        return visitor.result

    def structs(self: Type) -> t.Optional[t.List[sdt.Path]]:
        """Returns the path to the first level structs encountered in the type.
        For example, Union[Struct1,Union[Struct2[Struct3]] will return only a
        path that brings to Struct1 and Struct2.
        """

        class AddPath(sdt.TypeVisitor):
            result: t.Optional[t.List[sdt.Path]] = None

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = []

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                paths = []
                for type_name, curr_type in fields.items():
                    if curr_type.protobuf().WhichOneof('type') == 'struct':
                        paths.append(Path(sp.Path(label=type_name)))
                    else:
                        sub_paths = curr_type.structs()
                        if sub_paths is not None:
                            paths.extend(
                                [
                                    Path(
                                        sp.Path(
                                            label=type_name,
                                            paths=[subpath.protobuf()],
                                        )
                                    )
                                    for subpath in sub_paths
                                ]
                            )
                if len(paths) > 0:
                    self.result = t.cast(t.List[sdt.Path], paths)

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                if type.protobuf().WhichOneof('type') == 'struct':
                    self.result = [Path(sp.Path(label=OPTIONAL_VALUE))]
                else:
                    sub_paths = type.structs()
                    if sub_paths is not None:
                        self.result = [
                            Path(
                                sp.Path(
                                    label=OPTIONAL_VALUE,
                                    paths=[
                                        subpath.protobuf()
                                        for subpath in sub_paths
                                    ],
                                )
                            )
                        ]

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                if type.protobuf().WhichOneof('type') == 'struct':
                    self.result = [Path(sp.Path(label=LIST_VALUES))]
                else:
                    sub_paths = type.structs()
                    if sub_paths is not None:
                        self.result = [
                            Path(
                                sp.Path(
                                    label=LIST_VALUES,
                                    paths=[
                                        subpath.protobuf()
                                        for subpath in sub_paths
                                    ],
                                )
                            )
                        ]

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                if type.protobuf().WhichOneof('type') == 'struct':
                    self.result = [Path(sp.Path(label=ARRAY_VALUES))]
                else:
                    sub_paths = type.structs()
                    if sub_paths is not None:
                        self.result = [
                            Path(
                                sp.Path(
                                    label=ARRAY_VALUES,
                                    paths=[
                                        subpath.protobuf()
                                        for subpath in sub_paths
                                    ],
                                )
                            )
                        ]

        visitor = AddPath()
        self.accept(visitor)
        return visitor.result

    def leaves(self: sdt.Type) -> t.List[sdt.Type]:
        """Returns a list of the sub-types corresponding to
        the leaves of the type tree structure"""

        class AddLeaves(sdt.TypeVisitor):
            result: t.List[sdt.Type] = []

            def __init__(self, type_item: sdt.Type):
                self.result = [type_item]

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                for item_name in fields.keys():
                    result.extend(fields[item_name].leaves())
                if len(result) > 0:
                    self.result = result

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                for item_name in fields.keys():
                    result.extend(fields[item_name].leaves())
                if len(result) > 0:
                    self.result = result

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:

                result = []
                result.extend(type.leaves())
                if len(result) > 0:
                    self.result = result

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                result.extend(type.leaves())
                if len(result) > 0:
                    self.result = result

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                result = []
                result.extend(type.leaves())
                if len(result) > 0:
                    self.result = result

        visitor = AddLeaves(type_item=self)
        self.accept(visitor)
        return visitor.result

    def children(self: sdt.Type) -> t.Dict[str, sdt.Type]:
        """Returns the children contained in the type tree structure"""

        class GetChildren(sdt.TypeVisitor):
            result: t.Dict[str, sdt.Type] = {}

            def __init__(
                self, properties: t.Optional[t.Mapping[str, str]] = None
            ):
                self.properties = properties

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = t.cast(t.Dict[str, sdt.Type], fields)

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = t.cast(t.Dict[str, sdt.Type], fields)

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = {OPTIONAL_VALUE: type}

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                self.result = {LIST_VALUES: type}

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = {ARRAY_VALUES: type}

        visitor = GetChildren(properties=self.properties())
        self.accept(visitor)
        return visitor.result

    def example(self) -> pa.Array:
        """This methods returns a pyarrow scalar that matches the type.
        For an optional type, we consider the case where, the field
        is not missing.
        """

        class ToArrow(sdt.TypeVisitor):
            result = pa.nulls(0)

            def __init__(
                self, properties: t.Optional[t.Mapping[str, str]] = None
            ):
                self.properties = properties if properties is not None else {}

            def Null(self) -> None:
                raise NotImplementedError

            def Unit(self) -> None:
                self.result = pa.nulls(0)

            def Boolean(self) -> None:
                self.result = pa.array([True], type=pa.bool_())

            def Id(
                self,
                unique: bool,
                reference: t.Optional[sdt.Path] = None,
                base: t.Optional[sdt.IdBase] = None,
            ) -> None:
                # TODO: we should clarify for Ids, user_input
                # and so on, to be consistent
                if base == sdt.IdBase.STRING:
                    self.result = pa.array(['1'], pa.string())
                elif base == sdt.IdBase.INT64:
                    self.result = pa.array([1], pa.int64())
                else:
                    raise NotImplementedError

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                self.result = pa.array([int((min + max) / 2)], type=pa.int64())

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                self.result = pa.array([name_values[0][0]], pa.string())

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                self.result = pa.array([(min + max) / 2], type=pa.float64())

            def Text(self, encoding: str) -> None:
                try:
                    char_set = json.loads(self.properties[TEXT_CHARSET])
                except json.JSONDecodeError:
                    self.result = pa.array([""], pa.string())
                else:
                    max_length = int(self.properties[TEXT_MAX_LENGTH])
                    ex = ''.join(char_set)
                    if len(ex) > max_length:
                        ex = ex[:max_length]
                    self.result = pa.array([ex], pa.string())

            def Bytes(self) -> None:
                self.result = pa.array(
                    [bytes('1', 'utf-8')], pa.binary(length=1)
                )

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = pa.StructArray.from_arrays(
                    arrays=[
                        field_type.example() for field_type in fields.values()
                    ],
                    names=list(fields.keys()),
                )

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                n_fields = len(fields)
                arrays = []
                for j, field_type in enumerate(fields.values()):
                    middle_arr = field_type.example()
                    early_arr = pa.nulls(j, type=middle_arr.type)
                    late_arr = pa.nulls(n_fields - j - 1, type=middle_arr.type)
                    arrays.append(
                        pa.concat_arrays([early_arr, middle_arr, late_arr])
                    )
                names = list(fields.keys())
                arrays.append(pa.array(names, pa.string()))
                names.append('field_selected')
                self.result = pa.StructArray.from_arrays(
                    arrays=arrays,
                    names=names,
                )

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = type.example()

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Datetime(
                self, format: str, min: str, max: str, base: sdt.DatetimeBase
            ) -> None:
                self.result = pa.array(
                    pd.to_datetime([max], format=format), pa.timestamp('ns')
                )

            def Constrained(
                self,
                type: sdt.Type,
                constraint: sdt.Predicate,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

        visitor = ToArrow(properties=self.properties())
        self.accept(visitor)
        return visitor.result

    def numpy_example(self) -> np.ndarray:
        """Returns an example of numpy array matching the type.
        For an optional type, it returns a non missing value of the type.
        """
        return self.example().to_numpy(zero_copy_only=False)  # type:ignore

    def tensorflow_example(self) -> t.Any:
        """This methods returns a dictionary where the leaves are
        tf tensors. For optional types, we consider the case
        where the field is not missing.
        """

        class TensorflowExample(sdt.TypeVisitor):
            result = {}

            def __init__(
                self, properties: t.Optional[t.Mapping[str, str]] = None
            ):
                self.properties = properties if properties is not None else {}

            def Null(self) -> None:
                raise NotImplementedError

            def Unit(self) -> None:
                self.result = tf.constant([np.NaN], dtype=tf.float64)

            def Boolean(self) -> None:
                self.result = tf.constant([1], dtype=tf.int64)

            def Id(
                self,
                unique: bool,
                reference: t.Optional[sdt.Path] = None,
                base: t.Optional[sdt.IdBase] = None,
            ) -> None:
                # TODO: we should clarify for Ids, user_input
                # and so on, to be consistent
                if base == sdt.IdBase.STRING:
                    self.result = tf.constant(['1'], tf.string)
                elif base == sdt.IdBase.INT64:
                    self.result = tf.constant([1], tf.int64)
                else:
                    raise NotImplementedError

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                self.result = tf.constant([int((min + max) / 2)], tf.int64)

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                self.result = tf.constant([name_values[0][0]], tf.string)

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                self.result = tf.constant([(min + max) / 2], dtype=tf.float64)

            def Text(self, encoding: str) -> None:
                try:
                    char_set = json.loads(self.properties[TEXT_CHARSET])
                except json.JSONDecodeError:
                    self.result = tf.constant([""], tf.string)
                else:
                    max_length = int(self.properties[TEXT_MAX_LENGTH])
                    ex = ''.join(char_set)
                    if len(ex) > max_length:
                        ex = ex[:max_length]
                    self.result = tf.constant([ex], tf.string)

            def Bytes(self) -> None:
                self.result = tf.constant(['1'], tf.string)

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = {
                    field_name: field_type.tensorflow_example()
                    for field_name, field_type in fields.items()
                }

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = {
                    field_name: field_type.tensorflow_example()
                    for field_name, field_type in fields.items()
                }

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = {
                    'input_mask': tf.constant([1], dtype=tf.int64),
                    'values': type.tensorflow_example(),
                }

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Datetime(
                self, format: str, min: str, max: str, base: sdt.DatetimeBase
            ) -> None:
                self.result = tf.constant([min], dtype=tf.string)

            def Constrained(
                self,
                type: sdt.Type,
                constraint: sdt.Predicate,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

        visitor = TensorflowExample(properties=self.properties())
        self.accept(visitor)
        return visitor.result

    def default(self) -> pa.Array:
        """This methods returns a pyarrow scalar that matches the type.
        For an optional type, we consider the case where, the field
        is missing.
        """

        class Default(sdt.TypeVisitor):
            result = pa.nulls(0)

            def __init__(
                self, properties: t.Optional[t.Mapping[str, str]] = None
            ):
                self.properties = properties if properties is not None else {}

            def Null(self) -> None:
                raise NotImplementedError

            def Unit(self) -> None:
                self.result = pa.nulls(0)

            def Boolean(self) -> None:
                self.result = pa.array([True], type=pa.bool_())

            def Id(
                self,
                unique: bool,
                reference: t.Optional[sdt.Path] = None,
                base: t.Optional[sdt.IdBase] = None,
            ) -> None:
                # TODO: we should clarify for Ids, user_input
                # and so on, to be consistent
                if base == sdt.IdBase.STRING:
                    self.result = pa.array(['1'], pa.string())
                elif base == sdt.IdBase.INT64:
                    self.result = pa.array([1], pa.int64())
                else:
                    raise NotImplementedError

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                self.result = pa.array([int((min + max) / 2)], type=pa.int64())

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                self.result = pa.array([name_values[0][0]], pa.string())

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                self.result = pa.array([(min + max) / 2], type=pa.float64())

            def Text(self, encoding: str) -> None:
                try:
                    char_set = json.loads(self.properties[TEXT_CHARSET])
                except json.JSONDecodeError:
                    self.result = pa.array([""], pa.string())
                else:
                    max_length = int(self.properties[TEXT_MAX_LENGTH])
                    ex = ''.join(char_set)
                    if len(ex) > max_length:
                        ex = ex[:max_length]
                    self.result = pa.array([ex], pa.string())

            def Bytes(self) -> None:
                self.result = pa.array(
                    [bytes('1', 'utf-8')], pa.binary(length=1)
                )

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = pa.StructArray.from_arrays(
                    arrays=[
                        field_type.default() for field_type in fields.values()
                    ],
                    names=list(fields.keys()),
                )

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                n_fields = len(fields)
                arrays = []
                for j, field_type in enumerate(fields.values()):
                    middle_arr = field_type.default()
                    early_arr = pa.nulls(j, type=middle_arr.type)
                    late_arr = pa.nulls(n_fields - j - 1, type=middle_arr.type)
                    arrays.append(
                        pa.concat_arrays([early_arr, middle_arr, late_arr])
                    )
                names = list(fields.keys())
                arrays.append(pa.array(names, pa.string()))
                names.append('field_selected')
                self.result = pa.StructArray.from_arrays(
                    arrays=arrays,
                    names=names,
                )

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = pa.array([None], type=type.default().type)

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Datetime(
                self, format: str, min: str, max: str, base: sdt.DatetimeBase
            ) -> None:
                self.result = pa.array(
                    pd.to_datetime([max], format=format), pa.timestamp('ns')
                )

            def Constrained(
                self,
                type: sdt.Type,
                constraint: sdt.Predicate,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

        visitor = Default(properties=self.properties())
        self.accept(visitor)
        return visitor.result

    def numpy_default(self) -> np.ndarray:
        """Returns an example of numpy array matching the type.
        For an optional type, it sets the default missing value
        """
        return self.default().to_numpy(zero_copy_only=False)  # type:ignore

    def tensorflow_default(self, is_optional: bool = False) -> t.Any:
        """This methods returns a dictionary with tensors as leaves
        that match the type.
        For an optional type, we consider the case where the field
        is missing, and set the default value for each missing type.
        """

        class ToTensorflow(sdt.TypeVisitor):
            result = {}

            def __init__(
                self, properties: t.Optional[t.Mapping[str, str]] = None
            ):
                self.properties = properties if properties is not None else {}

            def Null(self) -> None:
                raise NotImplementedError

            def Unit(self) -> None:
                self.result = tf.constant([np.NaN], dtype=tf.float64)

            def Boolean(self) -> None:
                if is_optional:
                    self.result = tf.constant(
                        [np.iinfo(np.int64).max], dtype=tf.int64
                    )
                else:
                    self.result = tf.constant([1], dtype=tf.int64)

            def Id(
                self,
                unique: bool,
                reference: t.Optional[sdt.Path] = None,
                base: t.Optional[sdt.IdBase] = None,
            ) -> None:
                # TODO: we should clarify for Ids, user_input
                # and so on, to be consistent
                if is_optional:
                    if base == sdt.IdBase.STRING:
                        self.result = tf.constant([''], dtype=tf.string)
                    elif base == sdt.IdBase.INT64:
                        self.result = tf.constant(
                            [np.iinfo(np.int64).max], pa.string()
                        )
                    else:
                        raise NotImplementedError
                else:
                    if base == sdt.IdBase.STRING:
                        self.result = tf.constant(['1'], tf.string)
                    elif base == sdt.IdBase.INT64:
                        self.result = tf.constant([1], tf.int64)
                    else:
                        raise NotImplementedError

            def Integer(
                self, min: int, max: int, base: sdt.IntegerBase
            ) -> None:
                if is_optional:
                    self.result = tf.constant(
                        [np.iinfo(np.int64).min], dtype=tf.int64
                    )
                else:
                    self.result = tf.constant(
                        [int((min + max) / 2)], type=tf.int64
                    )

            def Enum(
                self,
                name: str,
                name_values: t.Sequence[t.Tuple[str, int]],
                ordered: bool,
            ) -> None:
                if is_optional:
                    self.result = tf.constant([''], dtype=tf.string)
                else:
                    self.result = tf.constant([name_values[0][0]], tf.string)

            def Float(
                self, min: float, max: float, base: sdt.FloatBase
            ) -> None:
                if is_optional:
                    self.result = tf.constant([np.NaN], dtype=tf.float64)
                else:
                    self.result = tf.constant(
                        [(min + max) / 2], dtype=tf.float64
                    )

            def Text(self, encoding: str) -> None:
                if is_optional:
                    self.result = tf.constant([''], dtype=tf.string)
                else:
                    try:
                        char_set = json.loads(self.properties[TEXT_CHARSET])
                    except json.JSONDecodeError:
                        self.result = tf.constant([""], tf.string)
                    else:
                        max_length = int(self.properties[TEXT_MAX_LENGTH])
                        ex = ''.join(char_set)
                        if len(ex) > max_length:
                            ex = ex[:max_length]
                        self.result = tf.constant([ex], tf.string)

            def Bytes(self) -> None:
                if is_optional:
                    self.result = tf.constant([''], dtype=tf.string)
                else:
                    self.result = tf.constant(['1'], tf.string)

            def Struct(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = {
                    field_name: field_type.tensorflow_default(
                        is_optional=is_optional
                    )
                    for field_name, field_type in fields.items()
                }

            def Union(
                self,
                fields: t.Mapping[str, sdt.Type],
                name: t.Optional[str] = None,
            ) -> None:
                self.result = {
                    field_name: field_type.tensorflow_default(
                        is_optional=is_optional
                    )
                    for field_name, field_type in fields.items()
                }

            def Optional(
                self, type: sdt.Type, name: t.Optional[str] = None
            ) -> None:
                self.result = {
                    'input_mask': tf.constant([0], dtype=tf.int64),
                    'values': type.tensorflow_default(is_optional=True),
                }

            def List(
                self,
                type: sdt.Type,
                max_size: int,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Array(
                self,
                type: sdt.Type,
                shape: t.Tuple[int, ...],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Datetime(
                self, format: str, min: str, max: str, base: sdt.DatetimeBase
            ) -> None:
                if is_optional:
                    self.result = tf.constant([''], dtype=tf.string)
                else:
                    self.result = tf.constant([min], dtype=tf.string)

            def Constrained(
                self,
                type: sdt.Type,
                constraint: sdt.Predicate,
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

            def Hypothesis(
                self,
                *types: t.Tuple[sdt.Type, float],
                name: t.Optional[str] = None,
            ) -> None:
                raise NotImplementedError

        visitor = ToTensorflow(properties=self.properties())
        self.accept(visitor)
        return visitor.result


# A few builders
def Null() -> Type:
    return Type(sp.Type(name='Null', null=sp.Type.Null()))


def Unit(properties: t.Optional[t.Mapping[str, str]] = None) -> Type:
    return Type(
        sp.Type(name='Unit', unit=sp.Type.Unit(), properties=properties)
    )


def Id(
    unique: bool,
    base: t.Optional[sdt.IdBase] = None,
    reference: t.Optional[sdt.Path] = None,
) -> Type:
    if base is None:
        base = sdt.IdBase.STRING
    if reference is None:
        return Type(
            sp.Type(name='Id', id=sp.Type.Id(base=base.value, unique=unique))
        )
    return Type(
        sp.Type(
            name='Id',
            id=sp.Type.Id(
                base=base.value, unique=unique, reference=reference.protobuf()
            ),
        )
    )


def Boolean() -> Type:
    return Type(sp.Type(name='Boolean', boolean=sp.Type.Boolean()))


def Integer(
    min: t.Optional[int] = None,
    max: t.Optional[int] = None,
    base: t.Optional[sdt.IntegerBase] = None,
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    if base is None:
        base = sdt.IntegerBase.INT64
    if min is None:
        if base == sdt.IntegerBase.INT64:
            min = np.iinfo(np.int64).min
        elif base == sdt.IntegerBase.INT32:
            min = np.iinfo(np.int32).min
        elif base == sdt.IntegerBase.INT16:
            min = np.iinfo(np.int16).min
        else:
            min = np.iinfo(np.int8).min
    if max is None:
        if base == sdt.IntegerBase.INT64:
            max = np.iinfo(np.int64).max
        elif base == sdt.IntegerBase.INT32:
            max = np.iinfo(np.int32).max
        elif base == sdt.IntegerBase.INT16:
            max = np.iinfo(np.int16).max
        else:
            max = np.iinfo(np.int8).max
    return Type(
        sp.Type(
            name='Integer',
            integer=sp.Type.Integer(base=base.value, min=min, max=max),
            properties=properties,
        )
    )


def Enum(
    name: str,
    name_values: t.Union[
        t.Sequence[str], t.Sequence[int], t.Sequence[t.Tuple[str, int]]
    ],
    ordered: bool = False,
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    enum_name_values: t.List[sp.Type.Enum.NameValue]
    if len(name_values) == 0:
        raise ValueError("No enum values")
    if isinstance(name_values[0], str):
        name_values = t.cast(t.Sequence[str], name_values)
        enum_name_values = [
            sp.Type.Enum.NameValue(name=n, value=v)
            for v, n in enumerate(sorted(name_values))
        ]
    elif isinstance(name_values[0], int):
        name_values = t.cast(t.Sequence[int], name_values)
        enum_name_values = [
            sp.Type.Enum.NameValue(name=str(v), value=v)
            for v in sorted(name_values)
        ]
    elif isinstance(name_values[0], tuple):
        name_values = t.cast(t.Sequence[t.Tuple[str, int]], name_values)
        enum_name_values = [
            sp.Type.Enum.NameValue(name=n, value=v)
            for n, v in sorted(name_values)
        ]
    return Type(
        sp.Type(
            name=name,
            enum=sp.Type.Enum(
                base=sp.Type.Enum.Base.INT64,
                ordered=ordered,
                name_values=enum_name_values,
            ),
            properties=properties,
        )
    )


def Float(
    min: t.Optional[float] = np.finfo(np.float64).min,
    max: t.Optional[float] = np.finfo(np.float64).max,
    base: t.Optional[sdt.FloatBase] = None,
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    if base is None:
        base = sdt.FloatBase.FLOAT64
    if min is None:
        if base == sdt.FloatBase.FLOAT64:
            min = np.finfo(np.float64).min
        elif base == sdt.FloatBase.FLOAT32:
            min = np.finfo(np.float32).min
        else:
            min = np.finfo(np.float16).min
    if max is None:
        if base == sdt.FloatBase.FLOAT64:
            max = np.finfo(np.float64).max
        elif base == sdt.FloatBase.FLOAT32:
            max = np.finfo(np.float32).max
        else:
            max = np.finfo(np.float16).max
    return Type(
        sp.Type(
            name='Float64',
            float=sp.Type.Float(base=base.value, min=min, max=max),
            properties=properties,
        )
    )


def Text(
    encoding: str = 'UTF-8', properties: t.Optional[t.Mapping[str, str]] = None
) -> Type:
    return Type(
        sp.Type(
            name=f'Text {encoding}',
            text=sp.Type.Text(encoding='UTF-8'),
            properties=properties,
        )
    )


def Bytes() -> Type:
    return Type(sp.Type(name='Bytes', bytes=sp.Type.Bytes()))


def Struct(
    fields: t.Mapping[str, sdt.Type],
    name: str = 'Struct',
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name=name,
            struct=sp.Type.Struct(
                fields=[
                    sp.Type.Struct.Field(name=name, type=type.protobuf())
                    for name, type in fields.items()
                ]
            ),
            properties=properties,
        )
    )


def Union(
    fields: t.Mapping[str, sdt.Type],
    name: str = 'Union',
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name=name,
            union=sp.Type.Union(
                fields=[
                    sp.Type.Union.Field(
                        name=field_name, type=field_type.protobuf()
                    )
                    for field_name, field_type in fields.items()
                ]
            ),
            properties=properties,
        )
    )


def Optional(
    type: sdt.Type,
    name: str = 'Optional',
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name=name,
            optional=sp.Type.Optional(type=type.protobuf()),
            properties=properties,
        )
    )


def List(
    type: sdt.Type,
    max_size: int = np.iinfo(np.int64).max,
    name: str = 'List',
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name=name,
            list=sp.Type.List(type=type.protobuf(), max_size=max_size),
            properties=properties,
        )
    )


def Array(
    type: sdt.Type,
    shape: t.Sequence[int],
    name: str = 'Array',
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name=name,
            array=sp.Type.Array(type=type.protobuf(), shape=shape),
            properties=properties,
        )
    )


def Datetime(
    format: t.Optional[str] = None,
    min: t.Optional[str] = None,
    max: t.Optional[str] = None,
    base: t.Optional[sdt.DatetimeBase] = None,
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    if format is None:
        format = '%Y-%m-%dT%H:%M:%S'
    if base is None:
        base = sdt.DatetimeBase.INT64_NS
    assert base == sdt.DatetimeBase.INT64_NS
    bounds = []
    iint64 = np.iinfo(np.int64)
    for i, bound in enumerate((min, max)):
        if bound is None:  # the bound is assumed to be sound otherwise
            # This starts with the true bounds for the type datetime64[ns]
            # However, storing dates as string implies an aliasing:
            # datetime.datetime cannot be more precise than µs.
            # So this would truncate the nanoseconds:
            # ```
            # min = (min + np.timedelta64(1, "us")).astype("datetime64[us]")
            # max = max.astype("datetime64[us]")
            # ```
            # More generally, the date format can only store a bound lower
            # than that bound, which is fine with the max but not for the
            # min, as it truncates some time units.
            if i == 0:
                bound = iint64.min + 1  # iint64.min maps to 'NaT'
                aliasing = np.timedelta64(0, 'ns')
                # This looks for the lowest offset for the format:
                # see:
                # https://numpy.org/doc/stable/reference/arrays.datetime.html#datetime-and-timedelta-arithmetic
                for unit, np_unit in [
                    ("%Y", "Y"),
                    ("%m", "M"),
                    ("%d", "D"),
                    ("%H", "h"),
                    ("%M", "m"),
                    ("%S", "s"),
                    ("%f", "us"),
                ]:
                    if unit not in format:
                        break
                    elif unit in ["%m", "%Y"]:
                        # months and years have variable length
                        as_unit = np.datetime64(bound, np_unit)
                        aliasing = np.timedelta64(1, np_unit)
                        aliasing = as_unit + aliasing - as_unit
                        aliasing = aliasing.astype("timedelta64[ns]")
                    else:
                        aliasing = np.timedelta64(1, np_unit)
            elif i == 1:
                bound = iint64.max
                aliasing = np.timedelta64(0, 'ns')
            bound = str(
                (np.datetime64(bound, "ns") + aliasing).astype(
                    "datetime64[us]"
                )
            )
            bound = datetime.datetime.strptime(
                bound, '%Y-%m-%dT%H:%M:%S.%f'
            ).strftime(format)
        bounds.append(bound)

    return Type(
        sp.Type(
            name='Datetime',
            datetime=sp.Type.Datetime(
                format=format, min=bounds[0], max=bounds[1], base=base.value
            ),
            properties=properties,
        )
    )


def Constrained(
    type: sdt.Type,
    constraint: Predicate,
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name='Constrained',
            constrained=sp.Type.Constrained(
                type=type.protobuf(), constraint=constraint._protobuf
            ),
            properties=properties,
        )
    )


def Hypothesis(
    *types: t.Tuple[sdt.Type, float],
    name: str = 'Hypothesis',
    properties: t.Optional[t.Mapping[str, str]] = None,
) -> Type:
    return Type(
        sp.Type(
            name=name,
            hypothesis=sp.Type.Hypothesis(
                types=(
                    sp.Type.Hypothesis.Scored(type=v.protobuf(), score=s)
                    for v, s in types
                )
            ),
            properties=properties,
        )
    )


def extract_filter_from_types(
    initial_type: sdt.Type, goal_type: sdt.Type
) -> sdt.Type:
    class FilterVisitor(sdt.TypeVisitor):
        """Visitor that select type for filtering, it only takes
        the Union types of the goal type and the rest is taken from
        the initial type
        """

        filter_type = initial_type

        def Union(
            self,
            fields: t.Mapping[str, sdt.Type],
            name: t.Optional[str] = None,
        ) -> None:
            # here select the fields in the goal type
            self.filter_type = Union(
                fields={
                    field_name: extract_filter_from_types(
                        initial_type=initial_type.children()[field_name],
                        goal_type=field_type,
                    )
                    for field_name, field_type in fields.items()
                }
            )

        def Struct(
            self,
            fields: t.Mapping[str, sdt.Type],
            name: t.Optional[str] = None,
        ) -> None:
            # here select the fields in the initial type
            self.filter_type = Struct(
                fields={
                    field_name: (
                        extract_filter_from_types(
                            initial_type=field_type,
                            goal_type=fields[field_name],
                        )
                        if fields.get(field_name) is not None
                        else field_type
                    )
                    for field_name, field_type in initial_type.children().items()  # noqa: E501
                }
            )

        def Optional(
            self, type: sdt.Type, name: t.Optional[str] = None
        ) -> None:
            # here it does not change
            self.filter_type = Optional(
                type=extract_filter_from_types(
                    initial_type=initial_type.children()[OPTIONAL_VALUE],
                    goal_type=type,
                )
            )

    visitor = FilterVisitor()
    goal_type.accept(visitor)
    return visitor.filter_type


def extract_project_from_types(
    initial_type: sdt.Type, goal_type: sdt.Type
) -> sdt.Type:
    class ProjectVisitor(sdt.TypeVisitor):
        """Visitor that select type for projecting, it only takes
        the Project types of the goal type and the rest is taken from
        the initial type
        """

        project_type = initial_type

        def Union(
            self,
            fields: t.Mapping[str, sdt.Type],
            name: t.Optional[str] = None,
        ) -> None:
            # here select the fields in the initial type
            self.project_type = Union(
                fields={
                    field_name: (
                        extract_filter_from_types(
                            initial_type=field_type,
                            goal_type=fields[field_name],
                        )
                        if fields.get(field_name) is not None
                        else field_type
                    )
                    for field_name, field_type in initial_type.children().items()  # noqa: E501
                }
            )

        def Struct(
            self,
            fields: t.Mapping[str, sdt.Type],
            name: t.Optional[str] = None,
        ) -> None:
            # here select the fields in the goal type
            self.project_type = Struct(
                fields={
                    field_name: extract_project_from_types(
                        initial_type=initial_type.children()[field_name],
                        goal_type=field_type,
                    )
                    for field_name, field_type in fields.items()
                }
            )

        def Optional(
            self, type: sdt.Type, name: t.Optional[str] = None
        ) -> None:
            # here it does not change
            self.project_type = Optional(
                type=extract_filter_from_types(
                    initial_type=initial_type.children()[OPTIONAL_VALUE],
                    goal_type=type,
                )
            )

    visitor = ProjectVisitor()
    goal_type.accept(visitor)
    return visitor.project_type


if t.TYPE_CHECKING:
    test_type: sdt.Type = Type(sp.Type())
