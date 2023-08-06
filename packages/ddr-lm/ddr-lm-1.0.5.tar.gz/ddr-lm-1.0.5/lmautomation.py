'''
  lmautomation.py
  
  Helper functions extending radkit_helpers for additional DDR operations
'''

from enum import Enum
from os import path
from typing import Optional, Union, List, Dict
from radkit_common.nglog import debug, warning, info, error, basicConfig, DEBUG
from radkit_client.device import DeviceDict, Device

import radkit_client.helpers as lmerrors


def scp_upload_from_buffer(
    target_dev: Union[DeviceDict, Device, lmerrors.DeviceFlow],
    target_filename: str,
    chmod: str,
    data: bytes,
) -> None:
    
    if isinstance(target_dev, Device):
        target_dev = target_dev.singleton()
    elif isinstance(target_dev, lmerrors.DeviceFlow):
        target_dev = target_dev.active_devices

    for device in target_dev.values():
        debug(f"  target device: {device.name}")
        scp = device.scp_upload_from_stream(target_filename, len(data)).wait()
        debug("  SCP ready")
        scp.result.write(data)
        scp.wait()
        debug("  Write done")
        scp.result.close()

def _read_file(filename: str) -> bytes:
    info(f"Reading file '{filename}'")

    with open(filename, "r") as f:
        return f.read().encode()


class Model(Enum):
    CLIPS = 0
    PYTHON = 1


CLIPS_COMPONENTS = ["devices", "facts", "flags", "rules"]


class Automation:
    def __init__(
        self, name: str, model: Optional[Model] = None, elements: Optional[dict] = None
    ) -> None:
        self.name = name.strip()
        self.model = model
        if elements is None:
            self.elements = {}
        else:
            self.elements = elements

    @classmethod
    def read_from_file(cls, name: str, filename: str) -> "Automation":
        ddr_components = {}
        if path.isdir(filename):
            model = Model.CLIPS
            for component in CLIPS_COMPONENTS:
                file_component = path.join(filename, f"ddr-{component}")
                debug(f"Loading '{file_component}'")
                try:
                    ddr_components[component] = _read_file(file_component)
                except OSError as e:
                    error(f"Could not open file '{file_component}'")
                    raise
            info(file_component)
        elif path.isfile(filename) and filename[-3:] == ".py":
            model = Model.PYTHON
            ddr_components["script"] = _read_file(filename)
        else:
            raise ValueError(f"Invalid file type or file does not exit ({filename})")

        return cls(name, model, ddr_components)
