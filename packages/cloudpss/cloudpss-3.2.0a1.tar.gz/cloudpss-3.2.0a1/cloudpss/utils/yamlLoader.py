import yaml
import io
import gzip
import struct
import base64


class JavascriptSchema():
    def float32Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('f' * (len(data) // 4), data))

    def float64Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('d' * (len(data) // 8), data))

    def uint8Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('B' * (len(data) // 1), data))

    def uint8ClampedArray(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('B' * (len(data) // 1), data))

    def uint16Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('H' * (len(data) // 2), data))

    def uint32Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('I' * (len(data) // 4), data))

    def int8Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('b' * (len(data) // 1), data))

    def int16Array(self, node):
        data = base64.b64decode(node.value)
        return list(struct.unpack('h' * (len(data) // 2), data))

    def int32Array(self, node):

        data = base64.b64decode(node.value)
        return list(struct.unpack('i' * (len(data) // 4), data)).toList()


yaml.add_constructor('tag:yaml.org,2002:js/Float32Array',
                     JavascriptSchema.float32Array)
yaml.add_constructor('tag:yaml.org,2002:js/Float64Array',
                     JavascriptSchema.float64Array)
yaml.add_constructor('tag:yaml.org,2002:js/Uint8Array',
                     JavascriptSchema.uint8Array)
yaml.add_constructor('tag:yaml.org,2002:js/Uint8ClampedArray',
                     JavascriptSchema.uint8ClampedArray)
yaml.add_constructor('tag:yaml.org,2002:js/Uint16Array',
                     JavascriptSchema.uint16Array)
yaml.add_constructor('tag:yaml.org,2002:js/Uint32Array',
                     JavascriptSchema.uint32Array)
yaml.add_constructor('tag:yaml.org,2002:js/Int8Array',
                     JavascriptSchema.int8Array)
yaml.add_constructor('tag:yaml.org,2002:js/Int16Array',
                     JavascriptSchema.int16Array)
yaml.add_constructor('tag:yaml.org,2002:js/Int32Array',
                     JavascriptSchema.int32Array)


def fileLoad(fileName):
    f = open(fileName, 'r+', encoding='utf-8')
    t = f.buffer.read(2)
    f.close()
    data = None
    if t == b'\x1f\x8b':
        with gzip.open(fileName, 'rb') as input_file:
            with io.TextIOWrapper(input_file, encoding='utf-8') as dec:
                r = dec.read()
                data = yaml.load(r, Loader=yaml.FullLoader)
    else:
        f = open(fileName, 'r+', encoding='utf-8')
        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
    return data