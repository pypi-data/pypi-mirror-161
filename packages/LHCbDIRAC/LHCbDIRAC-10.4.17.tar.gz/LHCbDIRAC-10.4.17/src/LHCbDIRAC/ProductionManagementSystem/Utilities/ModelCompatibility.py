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
"""Functions for converting production objects to the legacy format

This module contains functions which convert the ``pydantic`` models in
:py:mod:`.Models` into dictionaries similar to those provided by the LHCb
WebApp applications.
"""
import json
from typing import Optional

from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import (
    DataProduction,
    ProductionBase,
    ProductionStep,
    SimulationProduction,
)


STEP_NAME_MAPPING = {
    "ApplicationName": "App",
    "ApplicationVersion": "Ver",
    "CONDDB": "CDb",
    "DDDB": "DDDb",
    "DQTag": "DQT",
    "ExtraPackages": "EP",
    "OptionFiles": "Opt",
    "OptionsFormat": "OptF",
    "ProcessingPass": "Pass",
    "StepId": "Step",
    "StepName": "Name",
    "Usable": "Use",
    "Visible": "Vis",
    "isMulticore": "IsM",
    "mcTCK": "mcTCK",
}

PRODUCTION_DICT_KEYS = [
    "HasSubrequest",
    "NumberOfEvents",
    "RequestPDG",
    "Comments",
    "RetentionRate",
    "RequestAuthor",
    "Description",
    "RequestType",
    "EventType",
    "SimCondDetail",
    "RequestWG",
    "SimCondID",
    "IsModel",
    "FastSimulationType",
    "RequestPriority",
    "RealNumberOfEvents",
    "RequestState",
    "Inform",
    "ProPath",
    "RequestName",
    "SimCondition",
    "ProID",
    "Extra",
    "ProDetail",
    "MasterID",
    "RequestID",
    "ParentID",
]


def make_subprod_legacy_dict(sub_production, parent_id):
    """Make a webapp-like dictionary for defining a sub-production-request"""
    data = {k: None for k in PRODUCTION_DICT_KEYS}

    data["ParentID"] = parent_id
    data.update(sub_production)

    # Junk properties, included for consistency
    data["MasterID"] = data["ParentID"]
    data["HasSubrequest"] = 0
    data["IsModel"] = 0

    return data


def step_to_legacy_dict(step: ProductionStep):
    """Make a webapp-like dictionary that can be used to search for a step in the bookkeeping"""
    result = {
        "ApplicationName": step.application.name,
        "ApplicationVersion": step.application.version,
        "ExtraPackages": ";".join(sorted(f"{p.name}.{p.version}" for p in step.data_pkgs)),
        # TODO: Support new style options
        "ProcessingPass": step.processing_pass,
        "StepName": step.name,
        "isMulticore": "Y" if step.multicore else "N",
        # TODO: Really old steps have Visible = None?
        "Visible": "Y" if step.visible else "N",
        # TODO: Appears to have never been used
        # TODO: Required for running local tests
        # 'mcTCK': self.mc_tck or '',
        # 'DQTag': step.dbtags.DQ or '',
        # TODO: Get rid of RuntimeProjects from the database
    }
    if step.id is not None:
        result["StepId"] = step.id
    if step.dbtags:
        result["CONDDB"] = step.dbtags.CondDB or ""
        result["DDDB"] = step.dbtags.DDDB or ""
        result["DQTag"] = step.dbtags.DQTag or ""
    else:
        result["CONDDB"] = "fromPreviousStep"
        result["DDDB"] = "fromPreviousStep"
        result["DQTag"] = "fromPreviousStep"

    if isinstance(step.options, dict):
        # lbexec style options
        result["OptionFiles"] = json.dumps(step.options)
    else:
        # Legacy style options
        result["OptionFiles"] = ";".join(step.options)

    if step.options_format:
        result["OptionsFormat"] = step.options_format

    result["Usable"] = "Obsolete" if step.obsolete else ("Yes" if step.ready else "Not ready")

    return result


def step_to_step_manager_dict(step: ProductionStep):
    """Make a webapp-like dictionary for creating a step in the bookkeeping"""
    result = {"Step": step_to_legacy_dict(step)}

    if step.input:
        result["InputFileTypes"] = [{"FileType": x.type, "Visible": "Y" if x.visible else "N"} for x in step.input]
    result["OutputFileTypes"] = [{"FileType": x.type, "Visible": "Y" if x.visible else "N"} for x in step.output]
    return result


def _step_to_production_manager_dict(i: int, step: ProductionStep):
    """Make a webapp-like dictionary for defining a step in the metadata of a production request"""
    legacy_dict = step_to_legacy_dict(step)

    detail = {}
    if step.input:
        detail[f"p{i}IFT"] = ",".join(x.type for x in step.input)
    if step.output:
        detail[f"p{i}OFT"] = ",".join(x.type for x in step.output)
    for key, value in legacy_dict.items():
        if key not in STEP_NAME_MAPPING:
            raise NotImplementedError(f"Found unknown {key=}")

        full_key = f"p{i}{STEP_NAME_MAPPING[key]}"
        if value is None:
            if key in ["SConf"]:
                detail[full_key] = value
        else:
            detail[full_key] = str(value)

    # TODO: This should be generated dynamically rather than living in the database
    kwargs = dict(
        i=i,
        ift=detail.get(f"p{i}IFT", ""),
        oft=detail[f"p{i}OFT"],
        textRuntimeProjects="",
        SystemConfig="",
        mcTCK="",
        OptionsFormat="",
        DQTag="",
        StepId="None",
    )
    kwargs.update({k: v or "" for k, v in legacy_dict.items()})
    detail[f"p{i}Html"] = (
        "<b>Step {i}</b> "
        "{StepName}({StepId}/{ProcessingPass}) : {ApplicationName}-{ApplicationVersion}<br/>"
        "System config: {SystemConfig} MC TCK: {mcTCK}<br/>"
        "Options: {OptionFiles} Options format: {OptionsFormat} "
        "Multicore: {isMulticore}<br/>"
        "DDDB: {DDDB} Condition DB: {CONDDB} DQTag: {DQTag}<br/>"
        "Extra: {ExtraPackages} "
        "Runtime projects: {textRuntimeProjects}<br/>"
        "Visible: {Visible} Usable:{Usable}<br/>"
        "Input file types: {ift} "
        "Output file types: {oft}<br/><br/>"
    ).format(**kwargs)

    p_all = f"{step.application.name}-{step.application.version}"

    p_dsc = None
    if step.application.name and step.processing_pass and step.visible:
        p_dsc = step.processing_pass

    return detail, p_all, p_dsc


def production_to_legacy_dict(prod: ProductionBase):
    """Make a webapp-like dictionary for creating a production request"""
    request = {
        "RequestName": prod.name,
        "RequestType": prod.type,
        "RequestAuthor": prod.author,
        "RequestPriority": prod.priority,
        "RequestState": prod.state.value,
        "RequestWG": prod.wg,
        "Comments": prod.comment,
        # MC options
        "IsModel": 0,
        "Extra": None,
        "HasSubrequest": 0,
        "NumberOfEvents": -1,
        "RealNumberOfEvents": -1,
        # Junk
        "Description": None,
        "ProID": None,
        "RequestPDG": None,
        "MasterID": None,
        "ParentID": None,
    }
    sub_productions = []

    if prod.id is not None:
        request["RequestID"] = prod.id

    if isinstance(prod, SimulationProduction):
        request["FastSimulationType"] = prod.fast_simulation_type
        request["RetentionRate"] = prod.retention_rate
        if prod.mc_config_version is not None:
            request["Extra"] = json.dumps({"mcConfigVersion": prod.mc_config_version})

        request.update(_lookup_simulation_condition(prod.sim_condition))
        sub_productions = [
            {
                "EventType": event_type.id,
                "NumberOfEvents": event_type.num_events,
                "RealNumberOfEvents": event_type.num_events,
            }
            for event_type in prod.event_types
        ]

        if len(sub_productions) > 1:
            request["EventType"] = None
            request["NumberOfEvents"] = None
            request["RealNumberOfEvents"] = 0
            request["HasSubrequest"] = 1
        else:
            request.update(sub_productions.pop(0))

    elif isinstance(prod, DataProduction):
        request["SimCondDetail"] = json.dumps(prod.input_dataset.conditions_dict)
        request["SimCondID"] = prod.input_dataset.conditions_id
        request["SimCondition"] = prod.input_dataset.conditions_description
        request["EventType"] = prod.input_dataset.event_type
    else:
        raise NotImplementedError(type(prod))

    request["Inform"] = ",".join(prod.inform)

    request["ProDetail"] = {"pAll": [], "pDsc": []}
    for i, step in enumerate(prod.steps, start=1):
        detail, p_all, p_dsc = _step_to_production_manager_dict(i, step)
        request["ProDetail"].update(detail)
        request["ProDetail"]["pAll"].append(p_all)
        if p_dsc is not None:
            request["ProDetail"]["pDsc"].append(p_dsc)

    request["ProDetail"]["pAll"] = ",".join(request["ProDetail"]["pAll"])
    if prod.override_processing_pass is None:
        request["ProDetail"]["pDsc"] = "/".join(request["ProDetail"]["pDsc"])
    else:
        request["ProDetail"]["pDsc"] = prod.override_processing_pass
    request["ProPath"] = request["ProDetail"]["pDsc"]
    if len(request["ProPath"]) >= 100:
        raise ValueError(f"ProPath is too long: {request['ProPath']!r}")
    request["ProDetail"] = json.dumps(request["ProDetail"])

    return request, sub_productions


def _lookup_simulation_condition(sim_condition: str):
    """Create a dictionary for the given simulation condition

    This method queries the bookkeeping to get full metadata of the corresponding condition.
    """
    query = {"SimDescription": sim_condition}
    conditions = retValToListOfDict(BookkeepingClient().getSimulationConditions(query))
    # getSimulationConditions queries for 'SimDescription like "%sim_condition%"'
    # so filter out any extra results
    conditions = [x for x in conditions if x["SimDescription"] == sim_condition]
    if len(conditions) == 0:
        raise NotImplementedError(
            f"{query} is not known, an expert should create it using dirac-bookkeeping-simulationconditions-insert"
        )
    elif len(conditions) != 1:
        raise NotImplementedError(conditions)
    conditions = conditions[0]
    simcond_detail = {
        "BeamEnergy": conditions["BeamEnergy"],
        "Generator": conditions["Generator"],
        "Luminosity": conditions["Luminosity"],
        "MagneticField": conditions["MagneticField"],
        "G4settings": conditions["G4settings"],
        "BeamCond": conditions["BeamCond"],
        "DetectorCond": conditions["DetectorCond"],
    }
    return {
        "SimCondDetail": json.dumps(simcond_detail),
        "SimCondID": conditions["SimId"],
        "SimCondition": conditions["SimDescription"],
    }


def find_step_id(step: ProductionStep) -> Optional[int]:
    """Query the bookkeeping for a already defined step, returning its ID or None"""
    legacy_dict = step_to_legacy_dict(step)
    # Don't query on NULL keys as the bookkeeping gets confused
    query = {k: v for k, v in legacy_dict.items() if v}
    query.pop("Usable", None)
    matches = retValToListOfDict(BookkeepingClient().getAvailableSteps(query))

    matched = []
    for match in matches:
        input_types = [
            ProductionStep.FileType(type=x["FileType"], visible={"Y": True, "N": False}[x["Visible"]])
            for x in retValToListOfDict(BookkeepingClient().getStepInputFiles(match["StepId"]))
        ]
        if step.input != input_types:
            continue
        output_types = [
            ProductionStep.FileType(type=x["FileType"], visible={"Y": True, "N": False}[x["Visible"]])
            for x in retValToListOfDict(BookkeepingClient().getStepOutputFiles(match["StepId"]))
        ]
        if step.output != output_types:
            continue
        match.pop("RuntimeProjects", None)
        break
    else:
        return None

    # Sanity check
    for key in set(legacy_dict) | set(match):
        if key in ["StepId", "Usable"]:
            continue

        actual_value = match[key]
        if actual_value == "NULL":
            actual_value = ""
        expected_value = legacy_dict.get(key, None)

        if actual_value:
            if actual_value == expected_value:
                continue
        else:
            if not actual_value and not expected_value:
                continue
        raise NotImplementedError(key, actual_value, expected_value, matched)

    return match["StepId"]


def retValToListOfDict(retVal) -> list[dict]:
    """Convert a Records-style bookkeeping response to a list of dictionaries"""
    retVal = returnValueOrRaise(retVal)
    return [dict(zip(retVal["ParameterNames"], record)) for record in retVal["Records"]]
