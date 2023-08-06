from __future__ import annotations

from typing import Type

from sarus_data_spec.base import Base
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class Predicate(Base[sp.Predicate]):
    """A python class to describe types"""

    def prototype(self) -> Type[sp.Predicate]:
        """Return the type of the underlying protobuf."""
        return sp.Predicate

    # A bunch of operators
    def __or__(self, predicate: st.Predicate) -> Predicate:
        """Union operator"""
        if self._protobuf.HasField('union'):
            result = Predicate(self._protobuf)
            if predicate.protobuf().HasField('union'):
                result._protobuf.union.predicates.extend(
                    predicate.protobuf().union.predicates
                )
            else:
                result._protobuf.union.predicates.append(predicate.protobuf())
            return result
        else:
            if predicate.protobuf().HasField('union'):
                result = Predicate(predicate.protobuf())
                result._protobuf.union.predicates.insert(0, self._protobuf)
                return result
            else:
                return union(self, predicate)

    def __and__(self, predicate: st.Predicate) -> Predicate:
        """Inter operator"""
        if self._protobuf.HasField('inter'):
            result = Predicate(self._protobuf)
            if predicate.protobuf().HasField('inter'):
                result._protobuf.inter.predicates.extend(
                    predicate.protobuf().inter.predicates
                )
            else:
                result._protobuf.inter.predicates.append(predicate.protobuf())
            return result
        else:
            if predicate.protobuf().HasField('inter'):
                result = Predicate(predicate.protobuf())
                result._protobuf.inter.predicates.insert(0, self._protobuf)
                return result
            else:
                return inter(self, predicate)

    def __invert__(self) -> Predicate:
        """Complement"""
        if self._protobuf.HasField('comp'):
            return Predicate(self._protobuf.comp.predicate)
        else:
            return comp(self)


def inter(*predicates: st.Predicate) -> Predicate:
    return Predicate(
        sp.Predicate(
            inter=sp.Predicate.Inter(
                predicates=(p.protobuf() for p in predicates)
            )
        )
    )


def union(*predicates: st.Predicate) -> Predicate:
    return Predicate(
        sp.Predicate(
            union=sp.Predicate.Union(
                predicates=(p.protobuf() for p in predicates)
            )
        )
    )


def comp(predicate: st.Predicate) -> Predicate:
    return Predicate(
        sp.Predicate(comp=sp.Predicate.Comp(predicate=predicate.protobuf()))
    )


def simple(operator: str, value: str) -> Predicate:
    return Predicate(
        sp.Predicate(
            simple=sp.Predicate.Simple(operator=operator, value=value)
        )
    )
