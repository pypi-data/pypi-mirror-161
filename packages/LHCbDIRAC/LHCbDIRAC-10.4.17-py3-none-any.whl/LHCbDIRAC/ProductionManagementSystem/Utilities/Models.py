###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from enum import Enum
from typing import Any, Optional, Union, Literal, Any

from pydantic import BaseModel as _BaseModel
from pydantic import Extra, constr, PositiveInt, conlist, validator, confloat


class ProductionStates(str, Enum):
    NEW = "New"
    ACTIVE = "Active"
    SUBMITTED = "Submitted"
    PPG_OK = "PPG OK"
    TECH_OK = "Tech OK"
    ACCEPTED = "Accepted"
    DONE = "Done"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"


class BaseModel(_BaseModel, extra=Extra.forbid):
    pass


class ProductionStep(BaseModel):
    id: Optional[PositiveInt]
    name: str
    processing_pass: str
    options: Union[list[str], dict]  # TODO the list of str is for legacy compatibility
    options_format: Optional[str]  # TODO This should be merged into options
    visible: bool
    multicore: bool = False
    ready: bool = True
    obsolete: bool = True

    class Application(BaseModel):
        name: str
        version: str
        nightly: Optional[str]

    application: Application

    class DataPackage(BaseModel):
        name: str
        version: str

    data_pkgs: list[DataPackage]

    class DBTags(BaseModel):
        DDDB: Optional[str] = None
        CondDB: Optional[str] = None
        DQTag: Optional[str] = None

    dbtags: Optional[DBTags]

    class FileType(BaseModel):
        type: constr(regex=r"[A-Z0-9\.]+")
        visible: bool

    input: list[FileType]
    output: conlist(FileType, min_items=1)

    @validator("application", pre=True, always=True)
    def application_default(cls, application, values):  # pylint: disable=no-self-argument
        if isinstance(application, str):
            name, version = application.rsplit("/", 2)
            application = {"name": name, "version": version}
        return application

    @validator("data_pkgs", pre=True, always=True)
    def data_pkgs_default(cls, data_pkgs, values):  # pylint: disable=no-self-argument
        cleaned_data_pkgs = []
        for data_pkg in data_pkgs:
            if isinstance(data_pkg, str):
                name, version = data_pkg.rsplit(".", 2)
                cleaned_data_pkgs.append({"name": name, "version": version})
        return cleaned_data_pkgs


class ProductionBase(BaseModel):
    id: Optional[PositiveInt]
    author: str
    priority: constr(regex=r"^[12][ab]$")
    name: str
    inform: list[constr(strip_whitespace=True, min_length=3, max_length=50)]
    # TODO: I'm inclined to hardcode the list of known working groups
    wg: str
    comment: str = ""
    state: ProductionStates = ProductionStates.NEW
    steps: conlist(ProductionStep, min_items=1)


class SimulationProduction(ProductionBase):
    type: Literal["Simulation"]
    mc_config_version: PositiveInt
    sim_condition: str
    fast_simulation_type: constr(strip_whitespace=True, min_length=4, max_length=32) = "None"
    # TODO This should move to EventType
    retention_rate: confloat(gt=0, le=1) = 1
    override_processing_pass: Optional[str]

    class EventType(BaseModel):
        id: constr(regex=r"[0-9]{8}")
        num_events: PositiveInt

    event_types: conlist(EventType, min_items=1)


class DataProduction(ProductionBase):
    class InputDataset(BaseModel):
        conditions_dict: dict[str, str]
        conditions_id: int
        conditions_description: str
        event_type: constr(regex=r"[0-9]{8}")

    input_dataset: InputDataset


def parse_obj(obj: Any) -> ProductionBase:
    if obj.get("type") == "Simulation":
        return SimulationProduction.parse_obj(obj)
    return DataProduction.parse_obj(obj)
