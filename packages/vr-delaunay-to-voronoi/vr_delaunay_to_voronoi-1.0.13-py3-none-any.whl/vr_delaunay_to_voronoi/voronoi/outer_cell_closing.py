from typing import Any, DefaultDict, List, Tuple


def close_outer_cells(
    *,
    cells: DefaultDict[Any, List[Tuple]],
) -> DefaultDict[Any, List[Tuple]]:
    """
    Close the outer cells.
    """
    for polygon_index, line_indices in cells.items():
        dangling_lines = []
        for line_index_0, line_index_1 in line_indices:
            connections = list(
                filter(
                    lambda i12_:
                    (line_index_0, line_index_1) != (i12_[0], i12_[1])
                    and
                    (
                            line_index_0 == i12_[0] or
                            line_index_0 == i12_[1] or
                            line_index_1 == i12_[0] or
                            line_index_1 == i12_[1]
                    ),
                    line_indices
                )
            )
            assert 1 <= len(connections) <= 2
            if len(connections) == 1:
                dangling_lines.append((line_index_0, line_index_1))
        assert len(dangling_lines) in {0, 2}
        if len(dangling_lines) == 2:
            (i11, i12), (i21, i22) = dangling_lines

            # determine which line ends are unconnected
            connected = list(
                filter(
                    lambda i12_:
                        (i12_[0], i12_[1]) != (i11, i12) and
                        (i12_[0] == i11 or i12_[1] == i11),
                    line_indices
                )
            )
            i11_unconnected = not connected

            connected = list(
                filter(
                    lambda i12_:
                        (i12_[0], i12_[1]) != (i21, i22) and
                        (i12_[0] == i21 or i12_[1] == i21),
                    line_indices
                )
            )
            i21_unconnected = not connected

            start_index = i11 if i11_unconnected else i12
            end_index = i21 if i21_unconnected else i22

            cells[polygon_index].append((start_index, end_index))

    return cells
