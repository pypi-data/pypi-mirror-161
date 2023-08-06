from google.protobuf.json_format import ParseDict
from os import getenv
import sys
from validators.url import url as valid_url
import re
from pathlib import Path
import json

from sabana.common import (
    ndarray_from_values,
    post,
    get_config,
    get_access_token,
    get_id_token,
    value_from_id_token,
    TokenError,
    PostError,
    login_msg,
    icon_confetti,
    icon_rocket,
    icon_check,
    icon_arrow,
)
from sabana.responses import is_error, is_read, execute_response


class InstanceError(Exception):
    pass


class Instance:
    """
    Instance: handler for an instance in the Sabana platform.

              Can be created either by specifying user, instance, tag
              or by providing a URL.
    """

    __endpoint = "https://deploy.sabana.io"

    def __init__(self, image_file=None, image=None, url=None, verbose=False):
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
            print("Fatal error trying to get credentials by the Instance object.")
            print("Contact Sabana for support.")
            sys.exit(-1)

        self.instance_url = None
        self.user = None
        self.image_name = None
        self.image_tag = None
        self.is_up = False
        self.image_file = None
        self.verbose = verbose

        if image_file:
            if isinstance(image_file, Path):
                self.image_file = image_file
            elif isinstance(image_file, str):
                self.image_file = Path(image_file)

        if self.image_file:
            try:
                f = open(self.image_file, "r")
                data = json.load(f)
                self.user = value_from_id_token(
                    self.id_token, "https://sabana.io/username"
                )
                self.image_name = data["name"]
                self.image_tag = data["tag"]
            except:
                raise InstanceError("while processing image file")

        if isinstance(url, str) and valid_url(url):
            self.instance_url = url
        elif url != None:
            raise InstanceError("url is not valid")

        if isinstance(image, str):
            try:
                res = parse_image(image)
                self.user = res["user"]
                self.image_name = res["name"]
                self.image_tag = res["tag"]
            except Exception as e:
                raise e
        elif image != None:
            raise InstanceError("image is not valid")

        a = isinstance(self.image_file, Path)
        b = isinstance(self.instance_url, str)
        c = image != None
        more_than_one = a and (b or c)

        if image_file == None and url == None and image == None:
            raise InstanceError("image_file, url, or image must be provided")
        elif more_than_one:
            raise InstanceError(
                "either image_file, url, or image must be provided, but not more than one"
            )

    def __str__(self) -> str:
        msg = "Sabana Instance:\n"
        if all(
            isinstance(i, str) for i in (self.user, self.image_name, self.image_tag)
        ):
            msg += f"Instance: {self.user}/{self.image_name}:{self.image_tag}\n"
        if isinstance(self.instance_url, str):
            msg += f"Deployed at: {self.instance_url}"
        return msg

    def __del__(self):
        try:
            isup = self.is_up
        except AttributeError:
            # If the user tries to create an object with wrong arguments
            # this function will be called without self.is_up being defined.
            pass
        else:
            if self.is_up:
                self.down()

    def up(self):
        url = "{}/api/v0/up".format(self.__endpoint)
        req = {
            "user": self.user,
            "name": self.image_name,
            "tag": self.image_tag,
        }

        try:
            res = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise InstanceError(login_msg)
        except PostError as e:
            raise InstanceError("Failed bringing instance up: {}".format(e))
        else:
            if not "url" in res:
                print(login_msg)
                raise InstanceError("not able to up that instance")
            if len(res["url"]) == 0:
                raise InstanceError("Got invalid URL from server.")
            else:
                self.instance_url = res["url"]
                self.is_up = True
                if self.verbose:
                    print(
                        "{} {}/{}:{} is ready {} {}".format(
                            icon_confetti,
                            self.user,
                            self.image_name,
                            self.image_tag,
                            icon_arrow,
                            self.instance_url,
                        )
                    )

    def down(self):
        url = "{}/api/v0/down".format(self.__endpoint)
        req = {
            "url": self.instance_url,
        }
        try:
            res = post(req, url, self.access_token, self.id_token)
        except Exception as e:
            raise InstanceError(
                "Failed bringing {} down: {}".format(self.instance_url, str(e))
            )
        else:
            if self.verbose:
                print("{} {} is down".format(icon_check, self.instance_url))
            self.is_up = False
            self.instance_url == ""

    def execute(self, program):
        if not self.is_up and self.instance_url == "":
            raise InstanceError("Need to deploy an instance to execute this program")

        url = "{}/api/v0/execute".format(self.__endpoint)
        req = {
            "url": self.instance_url,
            "program": program.to_dict(),
        }

        try:
            if self.verbose:
                print(icon_rocket, "executing program")
            response = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise InstanceError(login_msg)
        except PostError as e:
            raise InstanceError("Failed executing the program: {}".format(e))
        else:
            reference = execute_response()
            res = ParseDict(response, reference)

            if len(program.req.requests) > 0 and len(res.responses) == 0:
                raise InstanceError("Execute failed with no responses")
            else:
                values = []
                for (a, b, i) in zip(
                    program.req.requests,
                    res.responses,
                    range(len(program.req.requests)),
                ):
                    if is_error(b.outcome):
                        msg = "\nOperation number {}: \n{} - {}\nfailed with: {}\n".format(
                            i, a.resource, str(a), b.outcome.info
                        )
                        raise InstanceError(msg)
                    elif is_read(b):
                        values.append(
                            ndarray_from_values(b.read.values, b.read.datatype).reshape(
                                b.read.shape
                            )
                        )
                return values


def parse_image(input: str) -> dict:
    try:
        input = input.strip()
        m = re.search(r"([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+):(\S+)", input)
        assert len(m.groups()) == 3
        exp = f"{m.group(1)}/{m.group(2)}:{m.group(3)}"
        assert input == exp
        res = {
            "user": m.group(1),
            "name": m.group(2),
            "tag": m.group(3),
        }
    except:
        raise InstanceError("image format is not valid")
    else:
        return res
