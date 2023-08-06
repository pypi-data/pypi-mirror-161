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
import json
import os
import shlex
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from textwrap import dedent
from typing import Optional

import yaml

from DIRAC import gLogger
from DIRAC.ConfigurationSystem.Client.Helpers import CSGlobals
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise, convertToReturnValue
from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import (
    parse_obj,
    ProductionBase,
    SimulationProduction,
    ProductionStep,
)


def parseArgs():
    useCfgOverride = True
    numEvents = 10

    @convertToReturnValue
    def disableCfgOverride(_):
        nonlocal useCfgOverride
        useCfgOverride = False

    @convertToReturnValue
    def setnumEvents(n):
        nonlocal numEvents
        numEvents = n

    switches = [
        ("", "num-events", f"Number of events to generate (Simulation only, default {numEvents})", setnumEvents),
        ("", "no-cfg-override", "Internal implementation detail", disableCfgOverride),
    ]
    Script.registerSwitches(switches)
    Script.registerArgument("yaml_path: Path to the YAML file containing productions to submit")
    Script.registerArgument("name: Name of the production to submit", mandatory=False)
    Script.registerArgument("event_type: The event type to generate (Simulation only)", mandatory=False)
    Script.parseCommandLine(ignoreErrors=False)
    yaml_path, name, eventType = Script.getPositionalArgs(group=True)

    from DIRAC.ConfigurationSystem.Client.ConfigurationClient import ConfigurationClient

    if not ConfigurationClient().ping()["OK"]:
        gLogger.fatal("Failed to contact CS, do you have a valid proxy?")
        sys.exit(1)

    return Path(yaml_path), name, eventType, useCfgOverride


def _runWithConfigOverride(argv):
    """Relaunch the process with DIRACSYSCONFIG overridden for local tests"""
    cfg_content = f"""
    DIRAC
    {{
        Setup={CSGlobals.getSetup()}
    }}
    LocalSite
    {{
        Site = DIRAC.LocalProdTest.local
        GridCE = jenkins.cern.ch
        CEQueue = jenkins-queue_not_important
        LocalSE = CERN-DST-EOS
        LocalSE += CERN-HIST-EOS
        LocalSE += CERN-RAW
        LocalSE += CERN-FREEZER-EOS
        LocalSE += CERN-SWTEST
        Architecture = x86_64-centos7
        SharedArea = /cvmfs/lhcb.cern.ch/lib
        CPUTimeLeft = 123456
    }}
    """
    with tempfile.NamedTemporaryFile(mode="wt") as tmp:
        tmp.write(dedent(cfg_content))
        tmp.flush()
        env = dict(os.environ)
        env["DIRACSYSCONFIG"] = ",".join([tmp.name] + env.get("DIRACSYSCONFIG", "").split(","))
        gLogger.always("Overriding DIRACSYSCONFIG to", env["DIRACSYSCONFIG"])
        gLogger.always("Restarting process with", argv)
        proc = subprocess.run(argv, env=env, check=False)
    sys.exit(proc.returncode)


@Script()
def main():
    yamlPath, name, eventType, useCfgOverride = parseArgs()

    if useCfgOverride:
        return _runWithConfigOverride(sys.argv + ["--no-cfg-override"])

    productionRequests = defaultdict(list)
    for spec in yaml.safe_load(yamlPath.read_text()):
        productionRequest = parse_obj(spec)
        productionRequests[productionRequest.name] += [productionRequest]

    if name is None:
        if len(productionRequests) == 1:
            name = list(productionRequests)[0]
        else:
            gLogger.fatal(
                "Multiple production requests available, please specify a name. Available options are:\n",
                "   * " + "\n    * ".join(map(shlex.quote, productionRequests)),
            )
            sys.exit(1)
    if name not in productionRequests:
        gLogger.fatal(
            "Unrecognised production request name. Available options are:\n",
            "   * " + "\n    * ".join(map(shlex.quote, productionRequests)),
        )
        sys.exit(1)
    if len(productionRequests[name]) > 1:
        gLogger.fatal("Ambiguous production requests found with identical names", shlex.quote(name))
        sys.exit(1)
    productionRequest = productionRequests[name][0]

    if isinstance(productionRequest, SimulationProduction):
        availableEventTypes = [e.id for e in productionRequest.event_types]
        if eventType is None and isinstance(productionRequest, SimulationProduction):
            if len(productionRequest.event_types) == 1:
                eventType = productionRequest.event_types[0].id
            else:
                gLogger.fatal(
                    "Multiple event types available, please specify a one.\nAvailable options are:\n",
                    "   * " + "\n    * ".join(availableEventTypes),
                )
                sys.exit(1)
        if eventType not in availableEventTypes:
            gLogger.fatal(f"Invalid event type passed ({eventType}), available options are: {availableEventTypes!r}")
            sys.exit(1)
    elif eventType is not None:
        gLogger.fatal(f"{eventType!r} but this is not a simulation production!")
        sys.exit(1)

    testProductionRequest(productionRequest, eventType=eventType)


def testProductionRequest(productionRequest: ProductionBase, eventType: Optional[str] = None):
    from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import production_to_legacy_dict
    from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequest import ProductionRequest

    pr = ProductionRequest()
    kwargs = {}
    legacy_dict, _ = production_to_legacy_dict(productionRequest)
    pr.prodGroup = json.loads(legacy_dict["ProDetail"])["pDsc"]
    if isinstance(productionRequest, SimulationProduction):
        pr.configName = "MC"
        pr.configVersion = productionRequest.mc_config_version
        pr.dataTakingConditions = productionRequest.sim_condition
        pr.eventType = eventType

        kwargs |= dict(
            events=10,
            multicore=False,
            prodType="MCSimulation" if productionRequest.fast_simulation_type == "None" else "MCFastSimulation",
        )
    else:
        raise NotImplementedError("Only simulation productions are supported at the moment")

    pr.outConfigName = "validation"
    pr.outputSEs = ["Tier1-Buffer"]

    stepsInProd = _steps_to_production_dict(productionRequest.steps)
    outputSE = {t["FileType"]: "Tier1-Buffer" for step in stepsInProd for t in step["visibilityFlag"]}

    # TODO: pr._buildProduction eats stepsInProd
    prod = pr._buildProduction(stepsInProd=stepsInProd, outputSE=outputSE, priority=0, cpu=100, **kwargs)
    return returnValueOrRaise(prod.runLocal())


def _steps_to_production_dict(steps: list[ProductionStep]) -> list[dict]:
    """Convert steps into list of dictionaries expected by ProductionRequest._buildProduction

    Normally this is handled by ProductionRequest.resolveSteps however this only
    supports reading from the bookkeeping.

    TODO: The ProductionRequest class should be refactored.
    """
    from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import step_to_step_manager_dict

    stepsInProd = []
    for i, dirac_step in enumerate(steps):
        result = step_to_step_manager_dict(dirac_step)
        step_dict = result["Step"]
        step_dict["StepId"] = step_dict.get("StepId", 12345)
        step_dict["fileTypesIn"] = [f.type for f in dirac_step.input]
        step_dict["fileTypesOut"] = [f.type for f in dirac_step.output]
        step_dict["ExtraPackages"] = ";".join([f"{d.name}.{d.version}" for d in dirac_step.data_pkgs])
        step_dict.setdefault("OptionsFormat", "")
        step_dict.setdefault("SystemConfig", "")
        step_dict.setdefault("mcTCK", "")
        step_dict["ExtraOptions"] = ""
        step_dict["visibilityFlag"] = result["OutputFileTypes"]
        # Normally ProductionRequest.resolveSteps will set these but that only supports getting IDs from the bookkeeping
        for field in ["CONDDB", "DDDB", "DQTag"]:
            if step_dict[field] == "fromPreviousStep":
                step_dict[field] = stepsInProd[i - 1][field]
        stepsInProd.append(step_dict)
    return stepsInProd
