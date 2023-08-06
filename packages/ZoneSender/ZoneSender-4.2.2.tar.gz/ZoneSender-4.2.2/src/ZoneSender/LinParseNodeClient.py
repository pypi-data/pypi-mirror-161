from signal import raise_signal
from typing import Union
import grpc
import json

from . import ZoneSenderData
from .ObjIo import *

from .Protos import LinParserNode_pb2,LinParserNode_pb2_grpc

class LinParseNodeClient(object) :
    def __init__(self) -> None:
        self._linDbParserStub = LinParserNode_pb2_grpc.LinParserNodeStub(
            channel=grpc.insecure_channel(
                target='{0}:{1}'
                    .format(
                        ZoneSenderData.LIN_PARSERNODE_NODE_IP, 
                        ZoneSenderData.LIN_PARSERNODE_NODE_PORT),
                options = ZoneSenderData.GRPC_OPTIONS
            )
        )
    
    def setChannelConfig(self,appChannel:int,ldfPath:str,linMode:str,
                            txrecv:int = 0,baudrate:int = 0) :
        try:
            res_ = self._linDbParserStub.SetChannelConfig(
                LinParserNode_pb2.lin_channel_config(
                    ldf_path = ldfPath,
                    lin_mode = linMode,
                    txrecv = txrecv,
                    baudrate = baudrate,
                    lin_channel = appChannel,
                )
            )
            print('setChannelConfig result: {0}, reason: {0}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def getLdfJson(self) :
        try:
            res_ = self._linDbParserStub.GetLdfJsonTree(
                LinParserNode_pb2.Common__pb2.empty()
            )
            print('getLdfJson result: {0}, reason: {0}'.format(res_.result, res_.reason))
            if res_.result == 0 :
                return json.loads(res_.json_data)
            else:
                raise Exception(f'{res_.reason}')
        except Exception as e_ :
            print(e_)
            return 1000

    def clearChannelConfig(self) :
        try:
            res_ = self._linDbParserStub.ClearDbfile(
                LinParserNode_pb2.Common__pb2.empty()
            )
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def clearSubscribe(self) :
        try:
            res_ = self._linDbParserStub.ClearSubscribe(
                LinParserNode_pb2.Common__pb2.empty()
            )
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000
    
    def clearSubscribe(self) :
        try:
            res_ = self._linDbParserStub.ClearSubscribe(
                LinParserNode_pb2.Common__pb2.empty()
            )
            print('清除所有 LinParser 的订阅 result: {0}, reason: {0}'.format(res_.result, res_.reason))
            return res_.result
        except Exception as e_ :
            print(e_)
            return 1000

    def setFrameSimulation(self,channel:int,frame:Union[int,str],simu:bool) :
        try:
            if isinstance(frame,str) :
                linframe = LinParserNode_pb2.lin_frame_config(
                    frame_name = frame,
                    channel = channel,
                    simu = simu,
                )
            elif isinstance(frame,int) :
                linframe = LinParserNode_pb2.lin_frame_config(
                    frame_id = frame,
                    channel = channel,
                    simu = simu,
                )
            else :
                print(f'frame type unsupport,input type is {type(frame)}')
                return 1000
            res_ = self._linDbParserStub.SetFrameSimulation(linframe)
            print('setFrameSimulation result: {0}, reason: {0}'.format(res_.result, res_.reason))
            return res_.result
        except Exception  as e_ :
            print(e_)
            return 1000

    def setNodeSimulation(self,channel:int,Node:str,simu:bool) :
        try:
            if isinstance(Node,str) :
                res_ = self._linDbParserStub.SetNodeSimulation(
                    LinParserNode_pb2.lin_node_config(
                        node_name = Node,
                        channel = channel,
                        simu = simu,
                    )
                )
            else :
                print(f'Node type unsupport,input type is {type(Node)}')
                return 1000
            print('setNodeSimulation result: {0}, reason: {0}'.format(res_.result, res_.reason))
            return res_.result
        except Exception  as e_ :
            print(e_)
            return 1000

        

