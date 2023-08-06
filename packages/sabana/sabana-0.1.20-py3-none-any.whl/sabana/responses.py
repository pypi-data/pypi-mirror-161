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

import sabana.sabana_pb2 as proto
from sabana.common import into_value
from sabana.common import ty_from_value


def execute_response():
    return proto.ExecuteResponse()


def invalid():
    response = proto.Response()
    response.resource = proto.RESOURCE_INVALID
    return response


def write(name):
    response = proto.Response()
    response.write.name = name
    return response


def read(name, value):
    response = proto.Response()
    response.read.name = name
    [v, l] = into_value(value)
    response.read.shape.extend(value.shape)
    response.read.values.CopyFrom(v)
    response.read.datatype = ty_from_value(value)
    return response


def wait(name):
    response = proto.Response()
    response.wait.name = name
    return response


def alloc(name):
    response = proto.Response()
    response.alloc.name = name
    return response


def dealloc(name):
    response = proto.Response()
    response.dealloc.name = name
    return response


def buffer_res(res):
    res.resource = proto.RESOURCE_BUFFER
    return res


def mmio_res(res):
    res.resource = proto.RESOURCE_MMIO
    return res


def mmio_write(name):
    return mmio_res(write(name))


def mmio_read(name, value):
    return mmio_res(read(name, value))


def mmio_wait(name):
    return mmio_res(wait(name))


def mmio_alloc(name):
    return mmio_res(alloc(name))


def mmio_dealloc(name):
    return mmio_res(dealloc(name))


def buffer_write(name):
    return buffer_res(write(name))


def buffer_read(name, value):
    return buffer_res(read(name, value))


def buffer_wait(name):
    return buffer_res(wait(name))


def buffer_alloc(name):
    return buffer_res(alloc(name))


def buffer_dealloc(name):
    return buffer_res(dealloc(name))


def is_write(res):
    return res.HasField("write")


def is_read(res):
    return res.HasField("read")


def is_wait(res):
    return res.HasField("wait")


def is_alloc(res):
    return res.HasField("alloc")


def is_dealloc(res):
    return res.HasField("dealloc")


def outcome_invalid(res, info=""):
    res.outcome.outcome_type = proto.OUTCOME_INVALID
    res.outcome.info = info
    return res


def outcome_ok(res, info=""):
    res.outcome.outcome_type = proto.OUTCOME_OK
    res.outcome.info = info
    return res


def outcome_error(res, info=""):
    res.outcome.outcome_type = proto.OUTCOME_ERROR
    res.outcome.info = info
    return res


def is_invalid(outcome):
    return outcome.outcome_type == proto.OUTCOME_INVALID


def is_ok(outcome):
    return outcome.outcome_type == proto.OUTCOME_OK


def is_error(outcome):
    return outcome.outcome_type == proto.OUTCOME_ERROR


def is_mmio(res):
    return res.resource == proto.RESOURCE_MMIO


def is_buffer(res):
    return res.resource == proto.RESOURCE_BUFFER


def is_invalid_resource(res):
    return res.resource == proto.RESOURCE_INVALID


def check(responses):
    for response in responses.responses:
        outcome = response.outcome
        if is_error(outcome) or is_invalid(outcome):
            msg = f"Got error or invalid response: {str(response)}"
            raise AssertionError(msg)
