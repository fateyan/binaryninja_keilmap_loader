import sys

from enum import Enum
from dataclasses import dataclass
from typing import Optional
    

class KeilSymbolType(Enum):
    NUMBER = 'Number'
    THUMB_CODE = 'Thumb Code'
    SECTION = 'Section'
    DATA = 'Data'

@dataclass
class KeilSymbol:
    name: str
    value: int
    type: KeilSymbolType
    size: int
    is_absolute: Optional[bool] # don't know if law of excluded middle applies
    is_local: bool # nor local

class KeilSymbolParser:
    text = ''
    cur = 0

    def log_debug(self, *args):
        print(*args)

    def log_near_lines(self, cur, no_lines=2):
        lloc = cur
        rloc = cur

        cnt = 0
        while cnt < no_lines:
            if lloc == 0:
                break

            if self.text[lloc] == '\n':
                cnt += 1
            lloc -= 1

        cnt = 0
        while cnt < no_lines:
            if rloc == len(self.text)-1:
                break

            if self.text[rloc] == '\n':
                cnt += 1
            rloc += 1

        self.log_debug(self.text[lloc:rloc])
        

    def has(self, sym: str) -> int:
        if self.text[self.cur:self.cur+len(sym)] == sym:
            self.cur = self.cur+len(sym)
            return self.cur
        return -1

    def whitespace(self):
        while True:
            if self.cur >= len(self.text) or not self.text[self.cur].isspace():
                break
            self.cur += 1

    def to_newline(self):
        buf = ''
        while True:
            if self.cur >= len(self.text) or self.text[self.cur] == '\n':
                self.cur += 1
                break
            buf += self.text[self.cur]
            self.cur += 1
        return buf

    def header(self):
        self.whitespace()
        i = self.has('Symbol Name')
        if i == -1:
            raise Exception('header not found')
        self.to_newline()

    def entries(self):
        self.whitespace()

        syms = []
        while True:
            line = self.to_newline()
            if line.strip() == '':
                break
            sym = self.entry(line)
            if sym is not None:
                syms.append(sym)
        return syms

    def entry(self, line):
        # FIXME: filepath with whitespace is not considered now.
        values = line.strip().split()

        if values[2] == 'Thumb' and values[3] == 'Code':
            values[2] = 'Thumb Code'
            del values[3]

        if values[1] == '-':
            self.log_debug(f'Undefined Weak Reference: {values[0]}')
            return None

        try:
            params = {
                'name': values[0],
                'value': int(values[1], base=16),
                'type': values[2],
                'size': int(values[3]),
                'is_absolute': bool(values[4]), # optional token
                'is_local': True,
            }
        except Exception as e:
            self.log_debug(e)
            self.log_near_lines(self.cur)

        sym = KeilSymbol(**params)

        return sym

    def main(self) -> [KeilSymbol]:
        syms = []
        while True:
            if self.cur >= len(self.text):
                break

            self.whitespace()
            if self.has('Local Symbols') != -1:
                self.header()
                syms += self.entries()
                continue
                
            if self.has('Global Symbols') != -1:
                self.header()
                _syms = self.entries()
                for sym in _syms:
                    sym.is_local = False
                syms += _syms
                continue

            self.cur += 1

        return syms

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        content = f.read()

    parser = KeilSymbolParser()
    parser.text = content
    print(parser.main())

