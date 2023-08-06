#  Copyright (c) 2021. Institute for High Voltage Equipment and Grids, Digitalization and Power Economics (IAEW)
#  RWTH Aachen University
#  Contact: Thomas Offergeld (t.offergeld@iaew.rwth-aachen.de)
#  #
#  This module is part of PySoAL.
#  #
#  PySoAL is licensed under the BSD-3-Clause license.
#  For further information see LICENSE in the project's root directory.

import logging

import numpy as np

from PySoAL.Solver import Solver

try:
    import gurobipy as grb

except ImportError:
    gurobi = None
    logging.error("Gurobi is not available")

typedict = {"I": "Integer", "B": "Binary", "C": "Continuous"}


class Gurobi(Solver):
    """
    Implementations for the Gurobi solver. This solver serves as a backend to the ODS-formulations.
    """
    BIN = grb.GRB.BINARY
    INT = grb.GRB.INTEGER
    INF = grb.GRB.INFINITY
    CONT = grb.GRB.CONTINUOUS
    MIN = grb.GRB.MINIMIZE
    MAX = grb.GRB.MAXIMIZE
    FAILED = grb.GRB.INF_OR_UNBD
    INFEASIBLE = grb.GRB.INFEASIBLE
    OPTIMAL = grb.GRB.OPTIMAL
    TIME_LIMIT = grb.GRB.TIME_LIMIT
    NOIIS = grb.GRB.ERROR_IIS_NOT_INFEASIBLE

    def __init__(self, timesteps: int = 1, stepduration: float = 1.0, **kwargs):
        self._model = grb.Model()
        self._model.Params.LogFile = ""
        self._model.Params.LogToConsole = kwargs.get("logToConsole", 0)
        self._model.Params.MIPFocus = kwargs.get("mipfocus", 0)
        self._model.Params.MIPGap = kwargs.get("mipgap", 1e-3)
        self._model.Params.TimeLimit = kwargs.get("timelimit", 60)
        self._model.Params.StartNodeLimit = kwargs.get("StartNodeLimit", 2e3)
        self.vars = None
        self.timesteps = timesteps
        self.stepduration = stepduration
        self.t_tupledict = grb.tupledict  # Used for representation of variable collections.
        # Will need to be re-implemented for other solvers if external fpus are used

    def addConstr(self, *args, **kwargs):
        return self._model.addConstr(*args, **kwargs)

    def getA(self):
        return self._model.getA()

    def getAttr(self, *args, **kwargs):
        return self._model.getAttr(*args, **kwargs)

    def getConstrs(self):
        return self._model.getConstrs()

    def addMConstr(self, *args, **kwargs):
        return self._model.addMConstr(*args, **kwargs)

    def addGenConstrPWL(self, *args, **kwargs):
        return self._model.addGenConstrPWL(*args, **kwargs)

    def addConstrs(self, *args, **kwargs):
        return self._model.addConstrs(*args, **kwargs)

    def getVars(self):
        return self._model.getVars()

    def addVar(self, *args, **kwargs):
        return self._model.addVar(*args, **kwargs)

    def optimize(self, callback=None):
        return self._model.optimize(callback)

    def update(self):
        return self._model.update()

    def setObjective(self, *args, **kwargs):
        return self._model.setObjective(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self._model.write(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self._model.remove(*args, **kwargs)

    @property
    def status(self):
        return self._model.status

    def computeIIS(self):
        return self._model.computeIIS()

    def quicksum(self, *args, **kwargs):
        return grb.quicksum(*args, **kwargs)

    def abs_(self, *args, **kwargs):
        return grb.abs_(*args, **kwargs)

    def or_(self, *args, **kwargs):
        return grb.or_(*args, **kwargs)

    def and_(self, *args, **kwargs):
        return grb.and_(*args, **kwargs)

    @staticmethod
    def unpack(source):

        result = {}
        for k, v in source.items():
            if isinstance(v, dict):
                result[k] = Gurobi.unpack(v)
            else:
                try:
                    val = v.x
                except AttributeError:
                    val = "NaN"
                result[k] = {"Value": val,
                             "Name": v.VarName,
                             "LB": (str(v.LB) if "inf" in str(v.LB) else v.LB),
                             "UB": (str(v.UB) if "inf" in str(v.UB) else v.UB),
                             "OBJ": (str(v.OBJ) if "inf" in str(v.OBJ) else v.OBJ),
                             "type": typedict[v.VType]}
        return result

    def get_vars(self):
        """
        Get a dictionary of the model variables.

        :return: A serializable dictionary of the model variables.
        """
        return self.unpack(self.vars)

    def tune(self):
        _model = self._model
        _model.tune()
        for i in range(_model.tuneResultCount):
            _model.getTuneResult(i)
            _model.write('tune' + str(i) + '.prm')

    def set_objective(self, sense="min", lin=None, lincoeff=None, quad=None, quadcoeff=None,
                      indexer=None, coeff_index_selector=0, replace=True):
        """
        Set the objective function of the model.

        :param sense:
        :param lin:
        :param lincoeff:
        :param quad:
        :param quadcoeff:
        :param indexer:
        :param coeff_index_selector:
        :param replace:
        """
        # ToDo: Document attributes and add usage examples.

        # Force update to ensure consistent behaviour (sometimes variable names are unavailable)
        self._model.update()
        if not replace:
            e = self._model.getObjective()
        else:
            e = grb.QuadExpr() if quad else grb.LinExpr()
        lincoeff = np.ones(len(lin)) if lincoeff is None and lin is not None else lincoeff
        quadcoeff = np.ones(len(quad)) if quadcoeff is None and quad is not None else quadcoeff
        for idx in indexer:
            if quad:
                e.addTerms(quadcoeff[idx[coeff_index_selector]], quad[idx], quad[idx])
            elif lin:
                e.addTerms(lincoeff[idx[coeff_index_selector]], lin[idx], lin[idx])
        senses = {"min": grb.GRB.MINIMIZE,
                  "max": grb.GRB.MAXIMIZE}
        try:
            sense = senses[sense.lower()]
        except KeyError:
            raise ValueError("Optimization sense invalid. Use 'min' or 'max'.")
        self._model.setObjective(e, sense)
        self._model.update()

    def add_vars(self, indexer, lb, ub, vtype, name=None):
        _m = self._model
        _vars = _m.addVars(indexer, lb=lb, ub=ub, obj=0, vtype=vtype, name=name)
        return _vars

    @staticmethod
    def set_start(startvalues):
        for (var, value) in startvalues.items():
            var.Start = value
