# automatically generated by the FlatBuffers compiler, do not modify

# namespace: fbs

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class StringStringEntry(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsStringStringEntry(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = StringStringEntry()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def StringStringEntryBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x4F\x52\x54\x4D", size_prefixed=size_prefixed)

    # StringStringEntry
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # StringStringEntry
    def Key(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

    # StringStringEntry
    def Value(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def StringStringEntryStart(builder): builder.StartObject(2)
def StringStringEntryAddKey(builder, key): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(key), 0)
def StringStringEntryAddValue(builder, value): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(value), 0)
def StringStringEntryEnd(builder): return builder.EndObject()
