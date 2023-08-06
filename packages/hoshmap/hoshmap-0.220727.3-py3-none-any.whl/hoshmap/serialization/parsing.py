#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the hoshmap project.
#  Please respect the license - more about this in the section (*) below.
#
#  hoshmap is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  hoshmap is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with hoshmap.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
import dis
import pickle
import re
from inspect import signature

from hosh import Hosh


def f2hosh(f: callable):
    if hasattr(f, "hosh"):
        return f.hosh
    fields_and_params = signature(f).parameters.values()
    fields_and_params = {v.name: None if v.default is v.empty else v.default for v in fields_and_params}
    # if not fields_and_params:
    #     raise NoInputException(f"Missing function input parameters.")
    # if "_" in fields_and_params:
    #     return None

    # Remove line numbers.
    groups = [l for l in dis.Bytecode(f).dis().split("\n\n") if l]
    clean_lines = [fields_and_params]

    for group in groups:
        # Replace memory addresses and file names by just the object name.
        group = re.sub(r'<code object (.+) at 0x[0-f]+, file ".+", line \d+>', r"\1", group)
        lines = [segment for segment in group.split(" ")][1:]
        clean_lines.append(lines)
    return Hosh(pickle.dumps([fields_and_params, clean_lines], protocol=5))


# def f2code(f: callable):
#     out = StringIO()
#     try:
#         decompile(bytecode_version=(3, 8), co=f.__code__, out=out)
#     except ParserError as e:
#         print(e)
#         raise Exception("Could not extract function code.")
#     code = [line for line in out.getvalue().split("\n") if not line.startswith("#")]
#     return code
