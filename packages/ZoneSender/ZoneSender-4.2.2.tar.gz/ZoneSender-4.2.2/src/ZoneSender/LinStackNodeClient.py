from typing import List
import grpc
from . import ZoneSenderData
from .ObjIo import *

from .Protos import LinStackNode_pb2,LinStackNode_pb2_grpc


class LinStackNodeClient(object) :
    def __init__(self) -> None:
        self._linStackStub = LinStackNode_pb2_grpc.LinStackNodeStub(
            channel=grpc.insecure_channel(
                target='{0}:{1}'
                    .format(
                        ZoneSenderData.LIN_STACK_NODE_IP, 
                        ZoneSenderData.LIN_STACK_NODE_PORT),
                options = ZoneSenderData.GRPC_OPTIONS
            )
        )

    def setConfig(self,configs:List[dict]) :
        '''
        configs example:
        [{'hardwareType':'vector','appName':'zoneSender'},{'hardwareType':'pcan','appName':'zoneSender'}]
        '''
        try:
            configs_ = list()
            for config_ in configs :
                configs_.append(
                    LinStackNode_pb2.lin_stack_config(
                        hardwareType = config_['hardwareType'],
                        appName = config_['appName'],
                    )
                )
            res_ = self._linStackStub.SetConfig(
                LinStackNode_pb2.lin_stack_configs(
                    config = configs_,
                )
            )
            print('setConfig result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def startLinStack(self):
        try:
            res_ = self._linStackStub.StartLinStack(
                LinStackNode_pb2.Common__pb2.empty()
            )
            print('StartLinStack result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def stopLinStack(self) :
        try:
            res_ = self._linStackStub.StopLinStack(
                LinStackNode_pb2.Common__pb2.empty()
            )
            print('StopLinStack result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000

    def reset(self) :
        try:
            res_ = self._linStackStub.Reset(
                LinStackNode_pb2.Common__pb2.empty()
            )
            print('ResetLinStack result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000

    def setMessageSimulation(self,channel:int,id:int,simu:bool) :
        try:
            res_ = self._linStackStub.SetMessageSimulation(
                LinStackNode_pb2.lin_message_config(
                    id = id,
                    simu = simu,
                    channel = channel,
                )
            )
            print('setMessageSimulation result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def setHeaderSimulation(self,channel:int,simu:bool) :
        try:
            res_ = self._linStackStub.SetHeaderSimulation(
                LinStackNode_pb2.lin_header_config(
                    simu = simu,
                    channel = channel,
                )
            )
            print('setHeaderSimulation result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def clearSubscribe(self) :
        try:
            res_ = self._linStackStub.ClearSubscribe(
                LinStackNode_pb2.Common__pb2.empty()
            )
            print('clearSubscribe result: {0}, reason: {1}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def isRunning(self) :
        try:
            res_ = self._linStackStub.GetStatus(
                LinStackNode_pb2.Common__pb2.empty()
            )
            # print('isRunning result: {0}, reason: {1}'.format(res_.result, res_.reason))
            if res_.status == 0:
                return True
            else:
                return False
        except Exception as e_ :
            return False