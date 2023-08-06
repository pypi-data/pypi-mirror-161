import typing
import copy
from .ZoneSenderObject import ZoneSenderObject

class LinMessage(ZoneSenderObject) :
    def __init__(self,
                    channel:int,
                    frameId:int,
                    dlc:int = 0,
                    data:typing.List[int] = [],
                    context:dict = dict(),
                    context_raw: dict = dict(),
                    ) -> None:
        super().__init__()
        self.frame_id = frameId
        self.frame_dlc = dlc
        self.frame_channel = channel
        self.frame_data = data
        self.context = copy.deepcopy(context)
        self.context_raw = copy.deepcopy(context_raw)
        self.name = str()

    def __str__(self) -> str:
        return 'frame_id: {0} data: {1}'.format(hex(self.frame_id).upper(), [hex(x_) for x_ in self.frame_data])