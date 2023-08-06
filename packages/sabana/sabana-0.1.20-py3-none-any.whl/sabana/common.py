import numpy as np
import json
from jose import jwt
import requests
from pathlib import Path
from os import getenv

import sabana.sabana_pb2 as proto

login_msg = "Error: up was not successful. Have you logged in?\n       to login use the Sabana CLI: sabana login"


icon_check = "\U00002714"
icon_confetti = "\U0001F389"
icon_rocket = "\U0001F680"
icon_arrow = "\U000027A1"


def print_up(*args):
    up_clear = "\033[1A" + "\x1b[2K"
    if isinstance(args, str) and len(args) == 1:
        print(up_clear + args)
    else:
        print(up_clear, *args)


class TokenError(Exception):
    pass


class PostError(Exception):
    pass


class CommonError(Exception):
    pass


def value_from_id_token(id_token, key):
    try:
        data = jwt.get_unverified_claims(id_token)
        value = data[key]
    except:
        raise TokenError("while decoding id token")
    else:
        return value


def get_config():
    if hasattr(Path, "home") and callable(getattr(Path, "home")):
        home_path = Path.home()
    elif isinstance(getenv("HOME"), str):
        home_path = getenv("HOME")
        if len(home_path) <= 0:
            raise TokenError("not able to determine user's home folder")
    else:
        raise TokenError("not able to determine user's home folder")

    config = Path(home_path, ".sabana", "config.json")
    if not config.is_file():
        raise TokenError("are you logged in?, use <sabana login>")
    with open(config, "r") as f:
        return json.load(f)


def get_access_token(config):
    if not "access_token" in config:
        raise TokenError("access token not found in config file")
    else:
        return config["access_token"]


def get_id_token(config):
    if not "access_token" in config:
        raise TokenError("id token not found in config file")
    else:
        return config["id_token"]


def post(request, url, access_token, id_token):
    response = requests.post(
        url,
        data=json.dumps(request),
        headers={
            "Content-Type": "application/json",
            "Authorization": access_token,
        },
    )
    resjson = response.json()
    if response.status_code == 400:
        raise PostError(f"Request failed with: {resjson['error']}")
    elif response.status_code == 500:
        raise PostError("There was an error on the Sabana platform.")
    else:
        return resjson


def ndarray_from_values(input, ty):
    if ty == proto.TYPE_INT8:
        values = input.int_values
    elif ty == proto.TYPE_UINT8:
        values = input.uint_values
    elif ty == proto.TYPE_INT16:
        values = input.int_values
    elif ty == proto.TYPE_UINT16:
        values = input.uint_values
    elif ty == proto.TYPE_INT32:
        values = input.int_values
    elif ty == proto.TYPE_UINT32:
        values = input.uint_values
    elif ty == proto.TYPE_FP32:
        values = input.fp32_values
    elif ty == proto.TYPE_INT64:
        values = input.int64_values
    elif ty == proto.TYPE_UINT64:
        values = input.uint64_values
    else:
        raise CommonError("Input type {} not supported".format(input))
    return np.array(values, dtype=dtype_from_ty(ty))


def value_from_numpy(input):
    output = proto.Value()
    data = input.flatten()
    if np.issubsctype(input, np.int8):
        output.int_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.uint8):
        output.uint_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.int16):
        output.int_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.uint16):
        output.uint_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.int32):
        output.int_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.uint32):
        output.uint_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.float32):
        output.fp32_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.int64):
        output.int64_values[:] = data
        return output, data.shape[0]
    elif np.issubsctype(input, np.uint64):
        output.uint64_values[:] = data
        return output, data.shape[0]
    else:
        raise CommonError("invalid numpy data type {}".format(input.dtype))


def into_value(input):
    if isinstance(input, np.ndarray):
        return value_from_numpy(input)
    else:
        raise CommonError("invalid value type {}".format(type(input)))


def ty_from_dtype(input):
    if input is np.int8:
        return proto.TYPE_INT8
    elif input is np.uint8:
        return proto.TYPE_UINT8
    elif input is np.int16:
        return proto.TYPE_INT16
    elif input is np.uint16:
        return proto.TYPE_UINT16
    elif input is int or input is np.int32:
        return proto.TYPE_INT32
    elif input is np.uint32:
        return proto.TYPE_UINT32
    elif input is np.float32:
        return proto.TYPE_FP32
    elif input is np.int64:
        return proto.TYPE_INT64
    elif input is np.uint64:
        return proto.TYPE_UINT64
    else:
        raise CommonError("invalid input type {}".format(input))


def ty_from_value(input):
    if np.issubsctype(input, np.int8):
        return proto.TYPE_INT8
    elif np.issubsctype(input, np.uint8):
        return proto.TYPE_UINT8
    elif np.issubsctype(input, np.int16):
        return proto.TYPE_INT16
    elif np.issubsctype(input, np.uint16):
        return proto.TYPE_UINT16
    elif isinstance(input, int) or np.issubsctype(input, np.int32):
        return proto.TYPE_INT32
    elif np.issubsctype(input, np.uint32):
        return proto.TYPE_UINT32
    elif np.issubsctype(input, np.float32):
        return proto.TYPE_FP32
    elif np.issubsctype(input, np.int64):
        return proto.TYPE_INT64
    elif np.issubsctype(input, np.uint64):
        return proto.TYPE_UINT64
    else:
        raise CommonError("invalid input type {}".format(input))


def dtype_from_ty(input):
    if input == proto.TYPE_INT8:
        return np.int8
    elif input == proto.TYPE_UINT8:
        return np.uint8
    elif input == proto.TYPE_INT16:
        return np.int16
    elif input == proto.TYPE_UINT16:
        return np.uint16
    elif input == proto.TYPE_INT32:
        return np.int32
    elif input == proto.TYPE_UINT32:
        return np.uint32
    elif input == proto.TYPE_FP32:
        return np.float32
    elif input == proto.TYPE_INT64:
        return np.int64
    elif input == proto.TYPE_UINT64:
        return np.uint64
    else:
        raise CommonError("invalid input type {}".format(input))
