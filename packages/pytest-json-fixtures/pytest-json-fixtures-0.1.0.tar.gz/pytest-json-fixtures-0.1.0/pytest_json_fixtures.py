# -*- coding: utf-8 -*-
import inspect
import json
from pathlib import Path
from typing import Set, Tuple

import pytest
from _pytest.compat import getlocation
from _pytest.python import _pretty_fixture_path


def pytest_addoption(parser):
    group = parser.getgroup('json-fixtures')
    group.addoption(
        '--json-fixtures',
        action='store',
        dest='filename',
        default='fixtures.json',
        help='JSON output for the --fixtures flag.'
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_collection_modifyitems(session, config):
    filename = config.getoption("filename")
    if filename:
        curdir = Path.cwd()
        verbose = config.getvalue("verbose")
        seen: Set[Tuple[str, str]] = set()
        available = []
        fixtures_from_module = {}

        for argname, fixturedefs in session._fixturemanager._arg2fixturedefs.items():
            assert fixturedefs is not None
            if not fixturedefs:
                continue
            for fixturedef in fixturedefs:
                loc = getlocation(fixturedef.func, str(curdir))
                if (fixturedef.argname, loc) in seen:
                    continue
                seen.add((fixturedef.argname, loc))
                available.append(
                    (
                        len(fixturedef.baseid),
                        fixturedef.func.__module__,
                        _pretty_fixture_path(fixturedef.func),
                        fixturedef.argname,
                        fixturedef,
                    )
                )

        available.sort()
        currentmodule = None
        fixtures = []
        for baseid, module, prettypath, argname, fixturedef in available:
            if currentmodule != module:
                if not module.startswith("_pytest."):
                    if f"fixtures defined from {currentmodule}" in fixtures_from_module:
                        fixtures.append(
                            {
                                f"fixtures defined from {currentmodule}":
                                    fixtures_from_module[f"fixtures defined from {currentmodule}"]
                            }
                        )
                    currentmodule = module
                    fixtures_from_module[f"fixtures defined from {currentmodule}"] = []
            if verbose <= 0 and argname.startswith("_"):
                continue
            fixture = {"name": argname, "scope": fixturedef.scope, "path": prettypath}
            doc = inspect.getdoc(fixturedef.func)
            if doc:
                write_docstring(fixture, doc.split("\n\n")[0] if verbose <= 0 else doc)
            else:
                fixture["docstring"] = "no docstring available"
            if not module.startswith("_pytest.") and f"fixtures defined from {currentmodule}" in fixtures_from_module:
                fixtures_from_module[f"fixtures defined from {currentmodule}"].append(fixture)
            else:
                fixtures.append(fixture)

        with open(filename, "w") as file:
            json.dump(fixtures, file, sort_keys=True, indent=4)

        outcome = yield


def write_docstring(fixture, doc):
    fixture["docstring"] = ""
    for line in doc.split("\n"):
        fixture["docstring"] = fixture["docstring"] + line
