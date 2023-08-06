from collections import defaultdict
from typing import List


class InsertText:
    def __init__(self, text: str, lineno: int, col_offset: int, newline: bool = False):
        self.text = text
        self.lineno = lineno
        self.col_offset = col_offset
        self.newline = newline

    @classmethod
    def before_node(cls, text, node, newline: bool = False):
        return cls(text, node.lineno - 1, node.col_offset, newline)

    @classmethod
    def after_node(cls, text, node, newline: bool = False):
        return cls(text, node.lineno - 1, node.end_col_offset, newline)


def grouped(list, key):
    output = defaultdict(lambda: [])

    for item in list:
        output[key(item)].append(item)

    return {k: output[k] for k in sorted(output.keys())}


def write_file(file_path: str, starting_text: str, inserts=List[InsertText]):
    lines = starting_text.splitlines()
    line_acc = 0

    for _lineno, line_inserts in grouped(inserts, key=lambda x: x.lineno).items():

        col_acc = 0

        for insert in sorted(line_inserts, key=lambda x: x.col_offset):
            lineno = _lineno + line_acc

            if insert.newline:
                lines = (
                    lines[:lineno]
                    + [" " * insert.col_offset + insert.text]
                    + lines[lineno:]
                )
                line_acc += 1
                col_acc += insert.col_offset + len(insert.text)
                continue

            idx = col_acc + insert.col_offset
            lines[lineno] = lines[lineno][:idx] + insert.text + lines[lineno][idx:]
            col_acc += len(insert.text)

    with open(file_path, "w") as out_file:
        out_file.write("\n".join(lines))
