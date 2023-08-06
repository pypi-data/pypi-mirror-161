#  Copyright (c) 2021. Institute for High Voltage Equipment and Grids, Digitalization and Power Economics (IAEW)
#  RWTH Aachen University
#  Contact: Thomas Offergeld (t.offergeld@iaew.rwth-aachen.de)
#  #
#  This module is part of PySoAL.
#  #
#  PySoAL is licensed under the BSD-3-Clause license.
#  For further information see LICENSE in the project's root directory.

from PySoAL import Gurobi


def test_create_model():
    m = Gurobi()
    m.addVar(lb=0, ub=1, obj=.5, vtype=Gurobi.BIN)
    m.update()