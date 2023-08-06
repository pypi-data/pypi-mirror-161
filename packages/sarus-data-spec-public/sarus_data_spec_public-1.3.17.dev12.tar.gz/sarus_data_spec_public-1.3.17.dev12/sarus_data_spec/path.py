from __future__ import annotations

from collections import defaultdict
import typing as t

from sarus_data_spec.base import Base
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class Path(Base[sp.Path]):
    """A python class to describe paths"""

    def prototype(self) -> t.Type[sp.Path]:
        """Return the type of the underlying protobuf."""
        return sp.Path

    def label(self) -> str:
        return self.protobuf().label

    def sub_paths(self) -> t.List[st.Path]:
        return [Path(path) for path in self.protobuf().paths]

    def to_strings_list(self) -> t.List[t.List[str]]:
        paths = []
        if len(self.protobuf().paths) == 0:
            return [[self.protobuf().label]]
        for path in self.protobuf().paths:
            out = Path(path).to_strings_list()
            for el in out:
                el.insert(
                    0,
                    self.protobuf().label,
                )
            paths.extend(out)
        return paths

    def to_dict(self) -> t.Dict[str, str]:
        list_paths = self.to_strings_list()
        return {
            '.'.join(path[1:-1]): path[-1] for path in list_paths
        }  # always start with 'data'


def paths(path_list: t.List[t.List[str]]) -> t.List[Path]:
    out = defaultdict(list)
    for path in path_list:
        try:
            first_el = path.pop(0)
        except IndexError:
            return []
        else:
            out[first_el].append(path)
    return [
        Path(
            sp.Path(
                label=element,
                paths=[path.protobuf() for path in paths(path_list)],
            )
        )
        for element, path_list in dict(out).items()
    ]


def path(paths: t.Optional[t.List[st.Path]] = None, label: str = '') -> Path:
    if paths is None:
        paths = []
    return Path(
        sp.Path(label=label, paths=[element.protobuf() for element in paths])
    )


def straight_path(nodes: t.List[str]) -> Path:
    """Returns linear path between elements in the list"""
    built_path = path(label=nodes.pop(-1))
    while len(nodes) > 0:
        built_path = path(label=nodes.pop(-1), paths=[built_path])
    return built_path


if t.TYPE_CHECKING:
    test_path: st.Path = Path(sp.Path())
