# automatically generated by the FlatBuffers compiler, do not modify

# namespace: CalTableFlatBuffers

import flatbuffers
from flatbuffers.compat import import_numpy

np = import_numpy()


class TrtTable(object):
    __slots__ = ["_tab"]

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = TrtTable()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsTrtTable(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)

    # TrtTable
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # TrtTable
    def Dict(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from onnxruntime.quantization.CalTableFlatBuffers.KeyValue import KeyValue

            obj = KeyValue()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # TrtTable
    def DictLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # TrtTable
    def DictIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0


def Start(builder):
    builder.StartObject(1)


def TrtTableStart(builder):
    """This method is deprecated. Please switch to Start."""
    return Start(builder)


def AddDict(builder, dict):
    builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(dict), 0)


def TrtTableAddDict(builder, dict):
    """This method is deprecated. Please switch to AddDict."""
    return AddDict(builder, dict)


def StartDictVector(builder, numElems):
    return builder.StartVector(4, numElems, 4)


def TrtTableStartDictVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartDictVector(builder, numElems)


def End(builder):
    return builder.EndObject()


def TrtTableEnd(builder):
    """This method is deprecated. Please switch to End."""
    return End(builder)
