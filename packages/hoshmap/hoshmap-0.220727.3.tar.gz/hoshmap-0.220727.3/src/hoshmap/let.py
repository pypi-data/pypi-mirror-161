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
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
from inspect import signature
from typing import Union, Iterable

from hosh import Hosh


class Let:
    def __init__(self, f: callable, in_out: str, id: Union[str, Hosh] = None, /, _metadata=None, **kwargs):
        # REMINDER: 'id' is only positional arg, so if 'f()' takes an 'id' argument, it's ok to provide both.
        in_out = in_out.replace("->", "→")
        if "→" not in in_out:  # pragma: no cover
            raise Exception(f"Missing '→' in in_out schema ({in_out}).")
        instr, outstr = in_out.split("→")
        if outstr == "":  # pragma: no cover
            raise Exception(f"Missing output field names after '→' in in_out schema ({in_out}).")
        self.f = f
        self.input = {}
        self.input_space = {}
        self.input_values = {}
        if instr == "":  # TODO: always parse signature, so user can omit some fields in in_out
            for par in signature(f).parameters.values():
                self.input[par.name] = par.name
                if par.default is not par.empty:
                    self.input_values[par.name] = par.default
                if par.name in kwargs:  # TODO: verify if this is needed
                    self.input_values[par.name] = kwargs[par.name]
            instr = " ".join(self.input.values())
            in_out = instr + "→" + outstr
            self.parsed = True
        else:
            self._parse_instr(instr, kwargs)
            self.parsed = False
        self.output = outstr.split(" ")
        self.id = id
        self.metadata = _metadata
        self.in_out = in_out
        self.instr = instr
        self.outstr = outstr

    def _parse_instr(self, instr, kwargs):
        for par in instr.split(" "):
            if ":" in par:
                split = par.split(":")
                if len(split) != 2:  # pragma: no cover
                    raise Exception(f"Wrong number ({len(split)}) of ':' chars: {split}")
                isource = split[0]
                itarget = par if ":*" in par else split[1]
            else:
                isource = itarget = par
            if isource.startswith("~"):  # TODO: write test
                isource = isource[1:]
                if isource not in kwargs or isinstance(kwargs[isource], Iterable):
                    raise Exception(f"Sampleable input {isource} must provide an iterable default value.")
                self.input_space[isource] = kwargs[isource]
            elif isource in kwargs:  # TODO: write test
                self.input_values[isource] = kwargs[isource]
            self.input[isource] = itarget


# TODO: add : mapping to output as well, so to accept exploding returned dicts
