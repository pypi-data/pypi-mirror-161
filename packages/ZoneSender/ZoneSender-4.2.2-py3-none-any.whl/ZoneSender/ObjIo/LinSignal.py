import typing
import copy
from .ZoneSenderObject import ZoneSenderObject


class LinSignal(ZoneSenderObject):
    ''' CanSignal 对象，用来描述一个 CAN Signal
    '''
    def __init__(
        self,
        name: 'str',
        channel: 'int',
        data_raw: 'float' = 0.0,
        data = None,
        unit: 'str' = ''
        ) -> None:
        ...
        # #####################################
        super().__init__()
        self.name = name
        self.data_raw = data_raw
        self.channel = channel
        self.data = data
        self.unit = unit
        self.id = None

    def __str__(self) -> str:
        # return super().__str__()
        return 'name: {0} channel: {1} value: {2} '.format(self.name, self.channel, self.data)