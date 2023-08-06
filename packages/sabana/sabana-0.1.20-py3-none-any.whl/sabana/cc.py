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

import base64
import tarfile
import io
import numpy as np
import sys
from pathlib import Path
from os import getenv
from sabana.common import (
    get_config,
    get_access_token,
    get_id_token,
    post,
    TokenError,
    PostError,
    login_msg,
    icon_confetti,
    icon_rocket,
    print_up,
)


class BuildError(Exception):
    pass


def flatten_name(tarinfo):
    tarinfo.name = str(Path(tarinfo.name).name)
    return tarinfo


# Note: Try to follow:
#       https://www.gnu.org/software/make/manual/html_node/Implicit-Variables.html
class Build:
    """
    Build: provides a handler to interact with Sabana's Build service
    """

    __endpoint = "https://build.sabana.io"
    __supported_march = ["rv32im"]
    __supported_toolchains = {"riscv64-unknown-elf": ["10.2.0"]}

    def __init__(self, toolchain=None, version=None, verbose=False):
        if toolchain not in Build.__supported_toolchains:
            raise BuildError("Toolchain architecture not supported")
        else:
            self.toolchain = toolchain

        if version not in Build.__supported_toolchains[toolchain]:
            raise BuildError("Toolchain version not supported")
        else:
            self.version = version

        try:
            config = get_config()
            self.access_token = get_access_token(config)
            self.id_token = get_id_token(config)
        except TokenError:
            self.access_token = getenv("SABANA_ACCESS_TOKEN")
            self.id_token = getenv("SABANA_ID_TOKEN")
            if not isinstance(self.access_token, str) or not isinstance(
                self.id_token, str
            ):
                print("ERROR: Could not find credentials on local file or environment.")
                print(
                    "       Use the following command to log-in using the Sabana CLI:\n"
                )
                print("sabana login\n")
                print("Alternatively setup the following environment variables:")
                print("SABANA_ACCESS_TOKEN, SABANA_ID_TOKEN")
                sys.exit(-1)
        except Exception as e:
            print("Fatal error trying to get Sabana credentials by the Build object.")
            print("Contact Sabana for support.")
            sys.exit(-1)
        self.files_list = {}
        self.cflags_list = []
        self.ldflags_list = []
        self.ldscript = None
        self.verbose = verbose

    def file(self, path, flags=None):
        filepath = Path(path)
        if not filepath.exists():
            raise BuildError(f"ERROR: {path} does not exist")
        # The following needs to be synchronized with nube/build-api/cc/app.py::project_from_tar
        elif filepath.suffix not in [".cpp", ".cc", ".c", ".h", ".hpp", ".S", ".ld"]:
            raise BuildError(f"ERROR: file extension ({filepath.suffix}) not supported")
        else:
            abspath = str(filepath.resolve())
            if filepath.suffix == ".ld":
                if self.ldscript == None:
                    self.ldscript = abspath
                else:
                    raise BuildError(
                        f"ERROR: there should be only one linker script(ld)"
                    )

            if abspath not in self.files_list:
                self.files_list[abspath] = []
            if isinstance(flags, str):
                self.files_list[abspath].extend(flags.split())

    def cflags(self, flags):
        if isinstance(flags, str):
            flags_list = flags.split()
            for flag in flags_list:
                if "march" not in flag:
                    self.cflags_list.append(flag)
                else:
                    if any(
                        f"-march={march}" == flag for march in Build.__supported_march
                    ):
                        self.cflags_list.append(flag)
                    else:
                        raise BuildError(
                            "Architecture not supported for -march in cflags"
                        )

    def ldflags(self, flags):
        if isinstance(flags, str):
            flags_list = flags.split()
            for flag in flags_list:
                if "march" not in flag:
                    self.ldflags_list.append(flag)
                else:
                    if any(
                        f"-march={march}" == flag for march in Build.__supported_march
                    ):
                        self.ldflags_list.append(flag)
                    else:
                        raise BuildError(
                            "Architecture not supported for -march in ldflags"
                        )
        else:
            raise BuildError("ERROR: Expecting flags as string")

    def compile(self):
        result = {}
        url = f"{self.__endpoint}/api/v0/cc"

        # Create in memory
        buffer = io.BytesIO()
        all_files = list(self.files_list)
        all_files.append(self.ldscript)
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            for path in self.files_list:
                # Using filter to make a flat tar file
                tar.add(path, filter=flatten_name)

        tarbytes = base64.b64encode(buffer.getvalue())
        tarstr = tarbytes.decode("utf-8")
        req = {
            "tar": tarstr,
            "cflags": self.cflags_list,
            "ldflags": self.ldflags_list,
            "toolchain": self.toolchain,
            "version": self.version,
        }

        for file in self.files_list:
            basename = str(Path(file).name)
            req[basename] = self.files_list[file]

        if self.verbose:
            print(icon_rocket, " Requesting program compilation")

        try:
            res = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise BuildError(login_msg)
        except PostError as e:
            raise BuildError("Failed compiling program: {}".format(e))
        else:
            if all(key in res.keys() for key in ("bin", "elf", "objdump")):
                bin_bytes = base64.b64decode(res["bin"].encode("utf-8"))
                result["binarray"] = np.frombuffer(bin_bytes, dtype=np.uint8)
                elf_bytes = base64.b64decode(res["elf"].encode("utf-8"))
                result["elfarray"] = np.frombuffer(elf_bytes, dtype=np.uint8)
                result["objdump"] = res["objdump"]
                if self.verbose:
                    print_up(icon_confetti, "program compilation successful")
                return result
            else:
                raise BuildError("ERROR: bad response from server")
