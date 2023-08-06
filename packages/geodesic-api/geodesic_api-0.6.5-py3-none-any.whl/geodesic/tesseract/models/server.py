import os
import logging
from time import time
from types import FunctionType
from typing import Iterator
from uuid import uuid4
import grpc
import numpy as np
from concurrent import futures

from geodesic.tesseract.models.inference_pb2_grpc import InferenceServiceV1Servicer,\
    add_InferenceServiceV1Servicer_to_server
from geodesic.tesseract.models.inference_pb2 import SendAssetDataResponse, SendAssetDataRequest, AssetDataHeader

in_base_path = '/tmp/data/in'
out_base_path = '/tmp/data/out'

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def read_array_file(path: str, shape: tuple, dtype: str):
    with open(path, 'rb') as fp:
        data = fp.read()

    array = np.frombuffer(data, dtype=dtype)
    array = array.reshape(shape)

    return array


def write_array_file(data: np.ndarray) -> str:
    path = os.path.join(out_base_path, str(uuid4()))
    with open(path, 'wb') as fp:
        b = data.tobytes()
        fp.write(b)
    return path


class TesseractModelServicer(InferenceServiceV1Servicer):
    def __init__(self, inference_func):
        self.inference_func = inference_func
        if not callable(inference_func):
            raise ValueError('inference_func must be a callable')

    def SendAssetData(
            self,
            request: Iterator[SendAssetDataRequest],
            context: grpc.ServicerContext) -> Iterator[SendAssetDataResponse]:

        # Parsed asset data
        in_assets = {}

        logger.debug("receiving SendAssetDataRequest")

        # Get all the assets from the stream
        for req in request:
            name = req.name
            type_ = req.type
            header = req.header

            logger.debug(f"received asset '{name}'")

            if type_ != 'tensor':
                logger.error(f"asset '{name}' invalid type {type_}. Must be 'tensor'")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"this model only works with 'tensor' inputs, got a '{type_}' input")
                yield SendAssetDataResponse()
                return

            if header is not None:
                filepath = header.filepath
                shape = header.shape
                dtype = header.dtype
                logger.debug(f"reading asset '{name}' from {filepath}")
                asset_array = read_array_file(filepath, shape, dtype)
                in_assets[name] = asset_array
                logger.debug(f"read asset '{name}'")

        try:
            logger.info("running inference_func")
            t = time()
            out_assets = self.inference_func(in_assets, logger.getChild('model'))
            logger.info(f"Done, inference_func finished in {time() - t} s")
        except Exception as e:
            logger.error(f"inference failed with Exception {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            yield SendAssetDataResponse()
            return

        logger.debug("sending SendAssetDataResponse")
        for name, out_asset in out_assets.items():
            logger.debug(f"writing out asset '{name}'")
            filepath = write_array_file(out_asset)

            logger.debug(f"sending response for asset '{name}'")
            res = SendAssetDataResponse(
                name=name,
                type="tensor",
                header=AssetDataHeader(
                    filepath=filepath,
                    shape=out_asset.shape,
                    dtype=out_asset.dtype.descr[0][1]
                )
            )

            yield res

        logger.debug("inference finished")


def serve(inference_func: FunctionType) -> grpc.Server:
    logger.info("initializing server")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = TesseractModelServicer(inference_func=inference_func)
    add_InferenceServiceV1Servicer_to_server(servicer, server)

    port = os.getenv('MODEL_CONTAINER_GRPC_PORT')
    if port is None or port == "":
        port = '8081'
    logger.info("initializing starting server on %s", f'[::]:{port}')
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info("server started")
    server.wait_for_termination()
