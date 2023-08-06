import grpc
import control_server_pb2_grpc
import control_server_pb2

import os

class PyScaleboxApi():
    def __init__(self):
        self.body = ""
        self.a = 0

    def send_message(self,body):
        channel = grpc.insecure_channel(os.getenv('CSST_PIPELINE_GRPC_SERVER'))

        stub = control_server_pb2_grpc.BoxServiceStub(channel)
        test = control_server_pb2.JobKey()
        test.job1_name = str(os.getenv('CSST_ADML2_NAME'))
        test.job0_id = int(os.getenv('CSST_ADML2_JOB_ID'))
        print("test.job1_name = "+os.getenv('CSST_ADML2_NAME'))

        test.key_text = body
        self.body = body
        
        reflag = stub.SendToNextJob(test)
        print(reflag.value)
        return reflag.value
    def func(self,a):
        b = a + 1
        self.a = a
        return b


    
# import grpc
# import control_server_pb2_grpc
# import control_server_pb2
# import os

# body="brickid,name1,name2,name3"
# channel = grpc.insecure_channel(os.getenv('CSST_PIPELINE_GRPC_SERVER'))

# stub = control_server_pb2_grpc.BoxServiceStub(channel)
# test = control_server_pb2.JobKey()
# test.job1_name = str(os.getenv('CSST_ADML2_NAME'))
# test.job0_id = int(os.getenv('CSST_ADML2_JOB_ID'))

# test.key_text = body
# reflag = stub.SendToNextJob(test)
# print(reflag.value)
        