from . import onnx, request

INIT_ARG_HANDLERS = {
    *onnx.INIT_ARG_HANDLERS,
}


PREDICT_ARG_HANDLERS = [
    *request.PREDICT_ARG_HANDLERS,
]
