"""Contains constants used for asset upload

This module contains a number of constants that are used for constructing
an S3 payload used for asset upload. There is nothing in this module that
you would ever need to change or use explicitly for any reason. So
please move along, nothing to see here...
"""

PYTORCH_INFERENCE = """
import torch
import os
import json
import numpy
import torch.nn as nn
import torch.nn.functional as F



device = torch.device('cpu')

def model_fn(model_dir):
    model = torch.jit.load(os.path.join(model_dir,'model.pt'))
    model.eval()
    return model

def input_fn(request_body, request_content_type):
    assert request_content_type=='application/json'
    data = json.loads(request_body)['inputs']
    data = torch.tensor(data, dtype=torch.float32, device=device)
    data = data.unsqueeze(0)
    return data

def predict_fn(input_object, model):
    with torch.no_grad():
        model.eval()
        data = torch.tensor(input_object[0])
        prediction = model(data)
    return prediction

def output_fn(predictions, content_type):
    assert content_type == 'application/json'
    res = predictions.cpu().numpy().tolist()
    return json.dumps(res)
"""
"""
`inference.py` payload for Pytorch models
"""

SCIKIT_INFERENCE = """
import joblib
import os
import json

def model_fn(model_dir):
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model

def input_fn(request_body, request_content_type):
    if request_content_type == 'application/json':
        request_body = json.loads(request_body)
        inpVar = request_body['Input']
        return inpVar
    else:
        raise ValueError("This model only supports application/json input")

def predict_fn(input_data, model):
    return model.predict(input_data)

def output_fn(prediction, content_type):
    res = prediction[0]
    respJSON = {'Output': res}
    return respJSON
"""
"""
`inference.py` payload for Scikit-Learn models
"""

TENSORFLOW_INFERENCE = """
import json
import requests
import numpy as np
import base64


def handler(data, context):
    processed_input = _process_input(data, context)
    response = requests.post(context.rest_uri, data=processed_input)
    return _process_output(response, context)


def _process_input(data, context):
    if context.request_content_type == 'application/json':
        # pass through json (assumes it's correctly formed)
        d = data.read().decode('utf-8')
        return d if len(d) else ''

    if context.request_content_type == 'text/csv':
        # very simple csv handler
        return json.dumps({
            'instances': [float(x) for x in data.read().decode('utf-8').split(',')]
        })

    raise ValueError('{{"error": "unsupported content type {}"}}'.format(
        context.request_content_type or "unknown"))


def _process_output(data, context):
    if data.status_code != 200:
        raise ValueError(data.content.decode('utf-8'))

    response_content_type = context.accept_header
    raw_prediction = data.content
    prediction = raw_prediction[0].numpy()[0]
    return prediction, response_content_type
"""
"""
`inference.py` payload for Tensorflow models
"""