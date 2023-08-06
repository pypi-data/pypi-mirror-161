from uhf.reader.protocol import *
from uhf.reader.utils import *


class MsgAppSetGpo(Message):

    def __init__(self, **kwargs):
        super().__init__()
        self.mt_8_11 = EnumG.Msg_Type_Bit_App.value
        self.msgId = EnumG.AppMid_SetGpo.value
        self.gpo1 = kwargs.get("gpo1", None)
        self.gpo2 = kwargs.get("gpo2", None)
        self.gpo3 = kwargs.get("gpo3", None)
        self.gpo4 = kwargs.get("gpo4", None)

    def bytesToClass(self):
        pass

    def pack(self):
        buffer = DynamicBuffer()
        if self.gpo1 is not None:
            buffer.putInt(0x01)
            buffer.putInt(self.gpo1)
        if self.gpo2 is not None:
            buffer.putInt(0x02)
            buffer.putInt(self.gpo2)
        if self.gpo3 is not None:
            buffer.putInt(0x03)
            buffer.putInt(self.gpo3)
        if self.gpo4 is not None:
            buffer.putInt(0x04)
            buffer.putInt(self.gpo4)
        self.cData = buffer.tobytes()
        self.dataLen = buffer.len / 8

    def unPack(self):
        if self.cData:
            dirMsg = {0: "Success", 1: "Port parameter reader hardware is not supported ."}
            self.rtCode = self.cData[0]
            if self.rtCode in dirMsg:
                self.rtMsg = dirMsg.get(self.rtCode, None)
