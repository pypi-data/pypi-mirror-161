# Copyright 2022 Sabana Technologies, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentError
import sabana.sabana_pb2 as proto
from sabana.common import into_value, ty_from_value, ty_from_dtype


def execute_request():
    return proto.ExecuteRequest()


def alloc(name, size, mmio, offset):
    if not isinstance(name, str):
        raise ArgumentError("name must be a string")
    if not isinstance(mmio, str):
        raise ArgumentError("mmio must be a string")
    if not isinstance(offset, int) or offset < 0:
        raise ArgumentError("offset must be a positive integer")
    if not isinstance(size, int) or size < 0:
        raise ArgumentError("size must be a positive integer")

    req = proto.Request()
    req.alloc.name = name
    req.alloc.size = size
    req.alloc.mmio_name = mmio
    req.alloc.mmio_offset = offset
    return req


def write(name, offset, value):
    if not isinstance(name, str):
        raise ArgumentError("name must be a string")
    if not isinstance(offset, int) or offset < 0:
        raise ArgumentError("offset must be a positive integer")
    req = proto.Request()
    req.write.name = name
    req.write.offset = offset
    [v, l] = into_value(value)
    req.write.shape.extend(value.shape)
    req.write.values.CopyFrom(v)
    req.write.datatype = ty_from_value(value)
    req.write.shape.extend(value.shape)
    return req


def wait(name, offset, value, timeout):
    if not isinstance(name, str):
        raise ArgumentError("name must be a string")
    if not isinstance(offset, int) or offset < 0:
        raise ArgumentError("offset must be a positive integer")
    if not isinstance(timeout, int) or offset < 0:
        raise ArgumentError("timeout must be a positive integer")
    req = proto.Request()
    req.wait.name = name
    req.wait.offset = offset
    [v, l] = into_value(value)
    req.wait.shape.extend(value.shape)
    req.wait.values.CopyFrom(v)
    req.wait.datatype = ty_from_value(value)
    req.wait.shape.extend(value.shape)
    req.wait.timeout = timeout
    return req


def read(name, offset, dtype, shape):
    if not isinstance(name, str):
        raise ArgumentError("name must be a string")
    if not isinstance(offset, int) or offset < 0:
        raise ArgumentError("offset must be a positive integer")
    if not isinstance(shape, tuple) and not isinstance(shape, list):
        raise ArgumentError("shape must be a tuple or list")
    req = proto.Request()
    req.read.name = name
    req.read.offset = offset
    req.read.datatype = ty_from_dtype(dtype)
    req.read.shape.extend(shape)
    return req


def dealloc(name):
    if not isinstance(name, str):
        raise ArgumentError("name must be a string")
    req = proto.Request()
    req.dealloc.name = name
    return req


def buffer_req(req):
    req.resource = proto.RESOURCE_BUFFER
    return req


def mmio_req(req):
    req.resource = proto.RESOURCE_MMIO
    return req


def mmio_write(name, offset, value):
    return mmio_req(write(name, offset, value))


def mmio_read(name, offset, dtype, shape):
    return mmio_req(read(name, offset, dtype, shape))


def mmio_wait(name, offset, value, timeout):
    return mmio_req(wait(name, offset, value, timeout))


def mmio_alloc(name, size):
    return mmio_req(alloc(name, size, "", 0))


def mmio_dealloc(name):
    return mmio_req(dealloc(name))


def buffer_write(name, offset, value):
    return buffer_req(write(name, offset, value))


def buffer_read(name, offset, dtype, shape):
    return buffer_req(read(name, offset, dtype, shape))


def buffer_wait(name, offset, value, timeout):
    return buffer_req(wait(name, offset, value, timeout))


def buffer_alloc(name, size, mmio, offset):
    return buffer_req(alloc(name, size, mmio, offset))


def buffer_dealloc(name):
    return buffer_req(dealloc(name))


def is_write(req):
    return req.HasField("write")


def is_read(req):
    return req.HasField("read")


def is_wait(req):
    return req.HasField("wait")


def is_alloc(req):
    return req.HasField("alloc")


def is_dealloc(req):
    return req.HasField("dealloc")


def is_mmio(req):
    return req.resource == proto.RESOURCE_MMIO


def is_buffer(req):
    return req.resource == proto.RESOURCE_BUFFER
