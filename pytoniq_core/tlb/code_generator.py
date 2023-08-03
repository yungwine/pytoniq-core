import os
import re
import typing

from bitarray import bitarray
from bitarray.util import hex2ba


class TlbGeneratorError(BaseException):
    pass


class TlbSchema:
    pass


class TlbSchemas:
    pass


class Lexer:

    def __init__(self):
        self._tag_hex = re.compile(r'#([0-9a-f]+_?|_)')
        self._tag_bin = re.compile(r'\$([01]*_?)')
        # https://www.debuggex.com/r/kT4s0-gThkHLZCGO ; to avoid recursion in reg ex and use built-in "re" lib.
        self._splitter = re.compile(r'[\w]*[^\w\s]*\[[^\]]*\]|'
                                    r'[\w]*[^\w\s]*\([^)(]*(?:\([^)(]*(?:\([^)(]*(?:\([^)(]*\)[^)(]*)*\)[^)(]*)*\)[^)(]*)*\)|'
                                    r'[\w]*[^\w\s]*\{[^\}]*\}|'
                                    r'\S+')

    def detect_tag(self, constructor: str) -> typing.Tuple[str, bitarray]:
        """
        :param constructor: constructor name with tag
        :return: constructor name and tag in bitarray
        """
        # hex_tag = self._tag_hex.findall(constructor)
        # if not hex_tag:
        #     bin_tag = self._tag_bin.findall(constructor)
        #     if not bin_tag:
        #         return constructor, bitarray('')
        #     return bitarray(bin_tag[0])
        # return hex2ba(hex_tag[0], 'big')
        if '#' in constructor:
            cons_name, tag = constructor.split('#')
            tag = tag.replace('_', '')
            return cons_name, hex2ba(tag, 'big')
        if '$' in constructor:
            cons_name, tag = constructor.split('$')
            tag = tag.replace('_', '')
            return cons_name, bitarray(tag)
        return constructor, bitarray('')  # or crc32? TODO

    def split(self, s: str):
        return self._splitter.findall(s)


class TlbRegistrator:

    def __init__(self):
        self._lexer = Lexer()

    def register(self, schema: str) -> TlbSchema:
        if '=' not in schema:
            raise TlbGeneratorError('unknown tlb string')
        splited = self._lexer.split(schema.replace(';', ''))
        eq_i = splited.index('=')

        class_name = splited[eq_i + 1]
        class_args = splited[eq_i + 2:]
        fields = self.parse_args(splited[1: eq_i])
        constructor_name, tag = self._lexer.detect_tag(splited[0])

        s = f'class {class_name}_{tag.tobytes().hex()}:\n'
        s += '\tdef __init__(self, **kwargs):\n'
        s += '\n\t\t"""class args"""\n'
        for arg in class_args:
            s += '\t\t' + f'self.{arg} = None\n'
        s += '\n\t\t"""fields"""\n'
        for field, type_ in fields.items():
            s += '\t\t' + f'self.{field}: {type_} = kwargs.get("{field}")\n'



        print(s)
        # print('schema: ', schema)
        # print('classname: ', class_name)
        # print('class args: ', class_args)
        # print('constructor name: ', constructor_name)
        # print('constructor tag: ', tag)
        # print('args: ', fields, '\n\n')

    @staticmethod
    def parse_args(fields: typing.List[str]) -> dict:
        result = {}
        for field in fields:
            if '{' in field or '}' in field:
                continue
            if field.startswith('^'):
                result['_'] = field
                continue
            # print(fields)
            if ':' not in field:
                continue
            # print(field)
            name, type_ = field.split(':', maxsplit=1)
            result[name] = type_
        return result

class TlbGenerator:
    def __init__(self, path: str, registrator: typing.Optional[TlbRegistrator] = None) -> None:
        self._path = os.path.normpath(path)
        if registrator is None:
            registrator = TlbRegistrator()
        self._registrator = registrator

    def generate(self):
        result = []
        if os.path.isdir(self._path):
            for f in os.listdir(self._path):
                if f.endswith('.tlb'):
                    result += self.from_file(os.path.join(self._path, f))
        else:
            result = self.from_file(self._path)
        return TlbSchemas()

    def from_file(self, file_path: str):
        result = []
        with open(file_path, 'r') as f:
            temp = ''
            comment = False

            for line in f:
                stripped = line.lstrip()
                if '*/' in stripped:
                    comment = False
                    continue

                if not stripped or stripped.startswith('//') or comment:
                    continue

                if '/*' in stripped:
                    comment = True
                    continue

                if '//' in stripped:
                    stripped = stripped.split('//')[0].strip()

                stripped = stripped.replace('\n', ' ')

                if ';' not in stripped:
                    temp += stripped
                    continue
                else:
                    stripped = temp + stripped
                    temp = ''
                result.append(self._registrator.register(stripped))
                # result.append(stripped)
        return result


if __name__ == '__main__':
    TlbGenerator('schemas').generate()
