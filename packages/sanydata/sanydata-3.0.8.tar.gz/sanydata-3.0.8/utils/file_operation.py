from utils.cos_handler import CosHandler
from utils.local_handler import LocalHandler
from sanydata import model_data_message_pb2
import json
import grpc
from sanydata import model_data_message_pb2_grpc


def GetDeployment(stub):
    data_input = model_data_message_pb2.GetDeploymentRequest()
    res = stub.GetDeployment(data_input, timeout=20000)

    return res.output


def GetCosToken(stub):
    data_input = model_data_message_pb2.GetCosTokenRequest()
    res = stub.GetCosToken(data_input, timeout=20000)
    return json.loads(res.output)


def GetTargetFile(filelist, cos_tocken):

    deployment = cos_tocken['deployment']

    file_handler = None
    if deployment == "cloud":
        file_handler = CosHandler(cos_tocken)
    elif deployment == "site":
        pass
    elif deployment == "local":
        file_handler = LocalHandler()

    for file in filelist:
        try:
            file = file.replace('../', '')
            data = file_handler.download(file)
            yield data
        except Exception as e:
            print(str(e))
            yield None
