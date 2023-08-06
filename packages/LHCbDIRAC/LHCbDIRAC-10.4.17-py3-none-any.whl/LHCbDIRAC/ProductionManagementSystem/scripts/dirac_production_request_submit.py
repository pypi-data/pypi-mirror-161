#!/usr/bin/env python
###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Create production requests from a YAML document"""
from pathlib import Path

import yaml

from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript as Script
from DIRAC.Core.Utilities.ReturnValues import convertToReturnValue, returnValueOrRaise

from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import parse_obj, ProductionBase


def parseArgs():
    doSubmit = False

    @convertToReturnValue
    def enableSubmit(_):
        nonlocal doSubmit
        doSubmit = True

    switches = [
        ("", "submit", "Actually create steps and submit productions", enableSubmit),
    ]
    Script.registerSwitches(switches)
    Script.registerArgument("yaml_path: Path to the YAML file containing productions to submit")
    Script.parseCommandLine(ignoreErrors=False)
    (yaml_path,) = Script.getPositionalArgs()
    return Path(yaml_path), doSubmit


@Script()
def main():
    yamlPath, doSubmit = parseArgs()

    productionRequests = [parse_obj(spec) for spec in yaml.safe_load(yamlPath.read_text())]
    submitProductionRequests(productionRequests, dryRun=not doSubmit)
    if not doSubmit:
        gLogger.always(f'This was a dry run! Pass "--submit" to actually submit production requests.')


def submitProductionRequests(productionRequests: list[ProductionBase], *, dryRun=True):
    """Submit a collection of production requests

    :param productionRequests: List of production requests to submit
    :param dryRun: Set to False to actually submit the production requests
    """
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import retValToListOfDict

    # Register filetypes
    requiredFileTypes = set()
    for prod in productionRequests:
        for step in prod.steps:
            requiredFileTypes |= {x.type for x in step.input}
            requiredFileTypes |= {x.type for x in step.output}
    knownFileTypes = {x["FileType"] for x in retValToListOfDict(BookkeepingClient().getAvailableFileTypes())}
    missingFileTypes = requiredFileTypes - knownFileTypes
    if missingFileTypes:
        raise NotImplementedError(f"Unknown file types that need to be registered: {missingFileTypes!r}")

    # Create steps and submit production requests
    for i, prod in enumerate(productionRequests, start=1):
        gLogger.always("Considering production", f"{i} of {len(productionRequests)}: {prod.name}")
        _submitProductionRequests(prod, dryRun=dryRun)


def _submitProductionRequests(prod: ProductionBase, *, dryRun=True):
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
    from LHCbDIRAC.ProductionManagementSystem.Utilities.Models import ProductionStates
    from LHCbDIRAC.ProductionManagementSystem.Utilities.ModelCompatibility import (
        find_step_id,
        make_subprod_legacy_dict,
        production_to_legacy_dict,
        step_to_step_manager_dict,
    )

    prc = ProductionRequestClient()

    for j, step in enumerate(prod.steps, start=1):
        step.id = find_step_id(step)
        if step.id is not None:
            gLogger.info(f"Step {j} of {len(prod.steps)}: Found existing step with ID {step.id=}")
            continue

        step_info = step_to_step_manager_dict(step)
        gLogger.verbose("Running insertStep with", step_info)
        if not dryRun:
            step.id = returnValueOrRaise(BookkeepingClient().insertStep(step_info))
            gLogger.info(f"Step {j} of {len(prod.steps)}: Created step with ID {step.id=}")

    if prod.id is not None:
        raise RuntimeError(f"{prod.id} has already been submitted")
    request_info, sub_productions = production_to_legacy_dict(prod)
    gLogger.verbose(f"Creating production request with", request_info)
    if not dryRun:
        prod.id = returnValueOrRaise(prc.createProductionRequest(request_info))

    sub_prod_ids = []
    for sub_prod in sub_productions:
        if prod.state != ProductionStates.NEW:
            raise RuntimeError("Can only add sub productions to productions in state 'New'")
        sub_prod_info = make_subprod_legacy_dict(sub_prod, prod.id)
        gLogger.verbose(f"Creating production sub request with", request_info)
        if not dryRun:
            sub_prod_id = returnValueOrRaise(prc.createProductionRequest(sub_prod_info))
            sub_prod_ids.append(sub_prod_id)

    prod.state = ProductionStates.SUBMITTED
    if not dryRun:
        returnValueOrRaise(prc.updateProductionRequest(prod.id, {"RequestState": prod.state.value}))
        gLogger.always(f"Submitted production {prod.id} with sub productions {sub_prod_ids}")


if __name__ == "__main__":
    main()
