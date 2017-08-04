# Copyright (C) 2015-2017 by the RBniCS authors
#
# This file is part of RBniCS.
#
# RBniCS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RBniCS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RBniCS. If not, see <http://www.gnu.org/licenses/>.
#

from dolfin import *
set_log_level(PROGRESS)
from rbnics.backends.dolfin import SeparatedParametrizedForm

assert MPI.size(mpi_comm_world()) == 1, "Numbering of functions changes in parallel"

mesh = UnitSquareMesh(10, 10)

V = VectorFunctionSpace(mesh, "Lagrange", 2)

expr1 = Expression("x[0]", mu_0=0., degree=1, cell=mesh.ufl_cell()) # f_4
expr2 = Expression(("x[0]", "x[1]"), mu_0=0., degree=1, cell=mesh.ufl_cell()) # f_5
expr3 = Expression((("1*x[0]", "2*x[1]"), ("3*x[0]", "4*x[1]")), mu_0=0., degree=1, cell=mesh.ufl_cell()) # f_6
expr4 = Expression((("4*x[0]", "3*x[1]"), ("2*x[0]", "1*x[1]")), mu_0=0., degree=1, cell=mesh.ufl_cell()) # f_7
expr5 = Expression("x[0]", degree=1, cell=mesh.ufl_cell()) # f_8
expr6 = Expression(("x[0]", "x[1]"), degree=1, cell=mesh.ufl_cell()) # f_9
expr7 = Expression((("1*x[0]", "2*x[1]"), ("3*x[0]", "4*x[1]")), degree=1, cell=mesh.ufl_cell()) # f_10
expr8 = Expression((("4*x[0]", "3*x[1]"), ("2*x[0]", "1*x[1]")), degree=1, cell=mesh.ufl_cell()) # f_11
expr9 = Constant(((1, 2), (3, 4))) # f_12

scalar_V = FunctionSpace(mesh, "Lagrange", 3)
tensor_V = TensorFunctionSpace(mesh, "Lagrange", 1)
expr10 = Function(scalar_V) # f_17
expr11 = Function(V) # f_20
expr12 = Function(tensor_V) # f_23

u = TrialFunction(V)
v = TestFunction(V)

log(PROGRESS, "*** ### @@@       VECTOR FORMS      @@@ ### ***")

a1 = inner(expr3*grad(u), grad(v))*dx + inner(grad(u)*expr2, v)*dx + expr1*inner(u, v)*dx
a1_sep = SeparatedParametrizedForm(a1)
log(PROGRESS, "*** ###              FORM 1             ### ***")
log(PROGRESS, "This is a basic vector advection-diffusion-reaction parametrized form, with all parametrized coefficients")
a1_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a1_sep.coefficients)) + "\n"
)
assert 3 == len(a1_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a1_sep.coefficients[0])) + "\n" +
    "\t\t" + str(len(a1_sep.coefficients[1])) + "\n" +
    "\t\t" + str(len(a1_sep.coefficients[2])) + "\n"
)
assert 1 == len(a1_sep.coefficients[0])
assert 1 == len(a1_sep.coefficients[1])
assert 1 == len(a1_sep.coefficients[2])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a1_sep.coefficients[0][0]) + "\n" +
    "\t\t" + str(a1_sep.coefficients[1][0]) + "\n" +
    "\t\t" + str(a1_sep.coefficients[2][0]) + "\n"
)
assert "f_6" == str(a1_sep.coefficients[0][0])
assert "f_5" == str(a1_sep.coefficients[1][0])
assert "f_4" == str(a1_sep.coefficients[2][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a1_sep._placeholders[0][0]) + "\n" +
    "\t\t" + str(a1_sep._placeholders[1][0]) + "\n" +
    "\t\t" + str(a1_sep._placeholders[2][0]) + "\n"
)
assert "f_26" == str(a1_sep._placeholders[0][0])
assert "f_27" == str(a1_sep._placeholders[1][0])
assert "f_28" == str(a1_sep._placeholders[2][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a1_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a1_sep._form_with_placeholders[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a1_sep._form_with_placeholders[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{14}} sum_{i_{13}} ({ A | A_{i_8, i_9} = sum_{i_{10}} f_26[i_8, i_{10}] * (grad(v_1))[i_{10}, i_9]  })[i_{13}, i_{14}] * (grad(v_0))[i_{13}, i_{14}]  " == str(a1_sep._form_with_placeholders[0].integrals()[0].integrand())
assert "sum_{i_{15}} ({ A | A_{i_{11}} = sum_{i_{12}} f_27[i_{12}] * (grad(v_1))[i_{11}, i_{12}]  })[i_{15}] * v_0[i_{15}] " == str(a1_sep._form_with_placeholders[1].integrals()[0].integrand())
assert "f_28 * (sum_{i_{16}} v_0[i_{16}] * v_1[i_{16}] )" == str(a1_sep._form_with_placeholders[2].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a1_sep._form_unchanged)) + "\n"
)
assert 0 == len(a1_sep._form_unchanged)

a2 = inner(expr3*expr4*grad(u), grad(v))*dx + inner(grad(u)*expr2, v)*dx + expr1*inner(u, v)*dx
a2_sep = SeparatedParametrizedForm(a2)
log(PROGRESS, "*** ###              FORM 2             ### ***")
log(PROGRESS, "In this case the diffusivity tensor is given by the product of two expressions")
a2_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a2_sep.coefficients)) + "\n"
)
assert 3 == len(a2_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a2_sep.coefficients[0])) + "\n" +
    "\t\t" + str(len(a2_sep.coefficients[1])) + "\n" +
    "\t\t" + str(len(a2_sep.coefficients[2])) + "\n"
)
assert 1 == len(a2_sep.coefficients[0])
assert 1 == len(a2_sep.coefficients[1])
assert 1 == len(a2_sep.coefficients[2])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a2_sep.coefficients[0][0]) + "\n" +
    "\t\t" + str(a2_sep.coefficients[1][0]) + "\n" +
    "\t\t" + str(a2_sep.coefficients[2][0]) + "\n"
)
assert "{ A | A_{i_{17}, i_{18}} = sum_{i_{19}} f_6[i_{17}, i_{19}] * f_7[i_{19}, i_{18}]  }" == str(a2_sep.coefficients[0][0])
assert "f_5" == str(a2_sep.coefficients[1][0])
assert "f_4" == str(a2_sep.coefficients[2][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a2_sep._placeholders[0][0]) + "\n" +
    "\t\t" + str(a2_sep._placeholders[1][0]) + "\n" +
    "\t\t" + str(a2_sep._placeholders[2][0]) + "\n"
)
assert "f_29" == str(a2_sep._placeholders[0][0])
assert "f_30" == str(a2_sep._placeholders[1][0])
assert "f_31" == str(a2_sep._placeholders[2][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a2_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a2_sep._form_with_placeholders[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a2_sep._form_with_placeholders[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{26}} sum_{i_{25}} ({ A | A_{i_{20}, i_{21}} = sum_{i_{22}} f_29[i_{20}, i_{22}] * (grad(v_1))[i_{22}, i_{21}]  })[i_{25}, i_{26}] * (grad(v_0))[i_{25}, i_{26}]  " == str(a2_sep._form_with_placeholders[0].integrals()[0].integrand())
assert "sum_{i_{27}} ({ A | A_{i_{23}} = sum_{i_{24}} f_30[i_{24}] * (grad(v_1))[i_{23}, i_{24}]  })[i_{27}] * v_0[i_{27}] " == str(a2_sep._form_with_placeholders[1].integrals()[0].integrand())
assert "f_31 * (sum_{i_{28}} v_0[i_{28}] * v_1[i_{28}] )" == str(a2_sep._form_with_placeholders[2].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a2_sep._form_unchanged)) + "\n"
)
assert 0 == len(a2_sep._form_unchanged)

a3 = inner(det(expr3)*(expr4 + expr3*expr3)*expr1, grad(v))*dx + inner(grad(u)*expr2, v)*dx + expr1*inner(u, v)*dx
a3_sep = SeparatedParametrizedForm(a3)
log(PROGRESS, "*** ###              FORM 3             ### ***")
log(PROGRESS, "We try now with a more complex expression of for each coefficient")
a3_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a3_sep.coefficients)) + "\n"
)
assert 3 == len(a3_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a3_sep.coefficients[0])) + "\n" +
    "\t\t" + str(len(a3_sep.coefficients[1])) + "\n" +
    "\t\t" + str(len(a3_sep.coefficients[2])) + "\n"
)
assert 1 == len(a3_sep.coefficients[0])
assert 1 == len(a3_sep.coefficients[1])
assert 1 == len(a3_sep.coefficients[2])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a3_sep.coefficients[0][0]) + "\n" +
    "\t\t" + str(a3_sep.coefficients[1][0]) + "\n" +
    "\t\t" + str(a3_sep.coefficients[2][0]) + "\n"
)
assert "{ A | A_{i_{34}, i_{35}} = ({ A | A_{i_{32}, i_{33}} = (({ A | A_{i_{29}, i_{30}} = sum_{i_{31}} f_6[i_{29}, i_{31}] * f_6[i_{31}, i_{30}]  }) + f_7)[i_{32}, i_{33}] * (f_6[0, 0] * f_6[1, 1] + -1 * f_6[0, 1] * f_6[1, 0]) })[i_{34}, i_{35}] * f_4 }" == str(a3_sep.coefficients[0][0])
assert "f_5" == str(a3_sep.coefficients[1][0])
assert "f_4" == str(a3_sep.coefficients[2][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a3_sep._placeholders[0][0]) + "\n" +
    "\t\t" + str(a3_sep._placeholders[1][0]) + "\n" +
    "\t\t" + str(a3_sep._placeholders[2][0]) + "\n"
)
assert "f_32" == str(a3_sep._placeholders[0][0])
assert "f_33" == str(a3_sep._placeholders[1][0])
assert "f_34" == str(a3_sep._placeholders[2][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a3_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a3_sep._form_with_placeholders[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a3_sep._form_with_placeholders[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{39}} sum_{i_{38}} f_32[i_{38}, i_{39}] * (grad(v_0))[i_{38}, i_{39}]  " == str(a3_sep._form_with_placeholders[0].integrals()[0].integrand())
assert "sum_{i_{40}} ({ A | A_{i_{36}} = sum_{i_{37}} f_33[i_{37}] * (grad(v_1))[i_{36}, i_{37}]  })[i_{40}] * v_0[i_{40}] " == str(a3_sep._form_with_placeholders[1].integrals()[0].integrand())
assert "f_34 * (sum_{i_{41}} v_0[i_{41}] * v_1[i_{41}] )" == str(a3_sep._form_with_placeholders[2].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a3_sep._form_unchanged)) + "\n"
)
assert 0 == len(a3_sep._form_unchanged)

h = CellSize(mesh)
a4 = inner(expr3*h*grad(u), grad(v))*dx + inner(grad(u)*expr2*h, v)*dx + expr1*h*inner(u, v)*dx
a4_sep = SeparatedParametrizedForm(a4)
log(PROGRESS, "*** ###              FORM 4             ### ***")
log(PROGRESS, "We add a term depending on the mesh size. The extracted coefficients may retain the mesh size factor depending on the UFL tree")
a4_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a4_sep.coefficients)) + "\n"
)
assert 3 == len(a4_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a4_sep.coefficients[0])) + "\n" +
    "\t\t" + str(len(a4_sep.coefficients[1])) + "\n" +
    "\t\t" + str(len(a4_sep.coefficients[2])) + "\n"
)
assert 1 == len(a4_sep.coefficients[0])
assert 1 == len(a4_sep.coefficients[1])
assert 1 == len(a4_sep.coefficients[2])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a4_sep.coefficients[0][0]) + "\n" +
    "\t\t" + str(a4_sep.coefficients[1][0]) + "\n" +
    "\t\t" + str(a4_sep.coefficients[2][0]) + "\n"
)
assert "{ A | A_{i_{42}, i_{43}} = f_6[i_{42}, i_{43}] * 2.0 * circumradius }" == str(a4_sep.coefficients[0][0])
assert "f_5" == str(a4_sep.coefficients[1][0])
assert "f_4 * 2.0 * circumradius" == str(a4_sep.coefficients[2][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a4_sep._placeholders[0][0]) + "\n" +
    "\t\t" + str(a4_sep._placeholders[1][0]) + "\n" +
    "\t\t" + str(a4_sep._placeholders[2][0]) + "\n"
)
assert "f_35" == str(a4_sep._placeholders[0][0])
assert "f_36" == str(a4_sep._placeholders[1][0])
assert "f_37" == str(a4_sep._placeholders[2][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a4_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a4_sep._form_with_placeholders[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a4_sep._form_with_placeholders[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{51}} sum_{i_{50}} ({ A | A_{i_{44}, i_{45}} = sum_{i_{46}} f_35[i_{44}, i_{46}] * (grad(v_1))[i_{46}, i_{45}]  })[i_{50}, i_{51}] * (grad(v_0))[i_{50}, i_{51}]  " == str(a4_sep._form_with_placeholders[0].integrals()[0].integrand())
assert "sum_{i_{52}} ({ A | A_{i_{49}} = ({ A | A_{i_{47}} = sum_{i_{48}} f_36[i_{48}] * (grad(v_1))[i_{47}, i_{48}]  })[i_{49}] * 2.0 * circumradius })[i_{52}] * v_0[i_{52}] " == str(a4_sep._form_with_placeholders[1].integrals()[0].integrand())
assert "f_37 * (sum_{i_{53}} v_0[i_{53}] * v_1[i_{53}] )" == str(a4_sep._form_with_placeholders[2].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a4_sep._form_unchanged)) + "\n"
)
assert 0 == len(a4_sep._form_unchanged)

a5 = inner((expr3*h)*grad(u), grad(v))*dx + inner(grad(u)*(expr2*h), v)*dx + (expr1*h)*inner(u, v)*dx
a5_sep = SeparatedParametrizedForm(a5)
log(PROGRESS, "*** ###              FORM 5             ### ***")
log(PROGRESS, "Starting from form 4, use parenthesis to make sure that the extracted coefficients retain the mesh size factor")
a5_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a5_sep.coefficients)) + "\n"
)
assert 3 == len(a5_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a5_sep.coefficients[0])) + "\n" +
    "\t\t" + str(len(a5_sep.coefficients[1])) + "\n" +
    "\t\t" + str(len(a5_sep.coefficients[2])) + "\n"
)
assert 1 == len(a5_sep.coefficients[0])
assert 1 == len(a5_sep.coefficients[1])
assert 1 == len(a5_sep.coefficients[2])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a5_sep.coefficients[0][0]) + "\n" +
    "\t\t" + str(a5_sep.coefficients[1][0]) + "\n" +
    "\t\t" + str(a5_sep.coefficients[2][0]) + "\n"
)
assert "{ A | A_{i_{54}, i_{55}} = f_6[i_{54}, i_{55}] * 2.0 * circumradius }" == str(a5_sep.coefficients[0][0])
assert "{ A | A_{i_{59}} = f_5[i_{59}] * 2.0 * circumradius }" == str(a5_sep.coefficients[1][0])
assert "f_4 * 2.0 * circumradius" == str(a5_sep.coefficients[2][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a5_sep._placeholders[0][0]) + "\n" +
    "\t\t" + str(a5_sep._placeholders[1][0]) + "\n" +
    "\t\t" + str(a5_sep._placeholders[2][0]) + "\n"
)
assert "f_38" == str(a5_sep._placeholders[0][0])
assert "f_39" == str(a5_sep._placeholders[1][0])
assert "f_40" == str(a5_sep._placeholders[2][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a5_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a5_sep._form_with_placeholders[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a5_sep._form_with_placeholders[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{63}} sum_{i_{62}} ({ A | A_{i_{56}, i_{57}} = sum_{i_{58}} f_38[i_{56}, i_{58}] * (grad(v_1))[i_{58}, i_{57}]  })[i_{62}, i_{63}] * (grad(v_0))[i_{62}, i_{63}]  " == str(a5_sep._form_with_placeholders[0].integrals()[0].integrand())
assert "sum_{i_{64}} ({ A | A_{i_{60}} = sum_{i_{61}} f_39[i_{61}] * (grad(v_1))[i_{60}, i_{61}]  })[i_{64}] * v_0[i_{64}] " == str(a5_sep._form_with_placeholders[1].integrals()[0].integrand())
assert "f_40 * (sum_{i_{65}} v_0[i_{65}] * v_1[i_{65}] )" == str(a5_sep._form_with_placeholders[2].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a5_sep._form_unchanged)) + "\n"
)
assert 0 == len(a5_sep._form_unchanged)

a6 = inner(expr7*grad(u), grad(v))*dx + inner(grad(u)*expr6, v)*dx + expr5*inner(u, v)*dx
a6_sep = SeparatedParametrizedForm(a6)
log(PROGRESS, "*** ###              FORM 6             ### ***")
log(PROGRESS, "We change the coefficients to be non-parametrized. No (parametrized) coefficients are extracted this time")
a6_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a6_sep.coefficients)) + "\n"
)
assert 0 == len(a6_sep.coefficients)
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a6_sep._form_unchanged)) + "\n"
)
assert 3 == len(a6_sep._form_unchanged)
log(PROGRESS, "\tUnchanged forms:\n" +
    "\t\t" + str(a6_sep._form_unchanged[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a6_sep._form_unchanged[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a6_sep._form_unchanged[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{72}} sum_{i_{71}} ({ A | A_{i_{66}, i_{67}} = sum_{i_{68}} f_10[i_{66}, i_{68}] * (grad(v_1))[i_{68}, i_{67}]  })[i_{71}, i_{72}] * (grad(v_0))[i_{71}, i_{72}]  " == str(a6_sep._form_unchanged[0].integrals()[0].integrand())
assert "sum_{i_{73}} ({ A | A_{i_{69}} = sum_{i_{70}} f_9[i_{70}] * (grad(v_1))[i_{69}, i_{70}]  })[i_{73}] * v_0[i_{73}] " == str(a6_sep._form_unchanged[1].integrals()[0].integrand())
assert "f_8 * (sum_{i_{74}} v_0[i_{74}] * v_1[i_{74}] )" == str(a6_sep._form_unchanged[2].integrals()[0].integrand())

a7 = inner(expr7*(expr3*expr4)*grad(u), grad(v))*dx + inner(grad(u)*expr6, v)*dx + expr5*inner(u, v)*dx
a7_sep = SeparatedParametrizedForm(a7)
log(PROGRESS, "*** ###              FORM 7             ### ***")
log(PROGRESS, "A part of the diffusion coefficient is parametrized (advection-reaction are not parametrized). Only the parametrized part is extracted.")
a7_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a7_sep.coefficients)) + "\n"
)
assert 1 == len(a7_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a7_sep.coefficients[0])) + "\n"
)
assert 1 == len(a7_sep.coefficients[0])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a7_sep.coefficients[0][0]) + "\n"
)
assert "{ A | A_{i_{75}, i_{76}} = sum_{i_{77}} f_6[i_{75}, i_{77}] * f_7[i_{77}, i_{76}]  }" == str(a7_sep.coefficients[0][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a7_sep._placeholders[0][0]) + "\n"
)
assert "f_41" == str(a7_sep._placeholders[0][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a7_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{87}} sum_{i_{86}} ({ A | A_{i_{81}, i_{82}} = sum_{i_{83}} ({ A | A_{i_{78}, i_{79}} = sum_{i_{80}} f_10[i_{78}, i_{80}] * f_41[i_{80}, i_{79}]  })[i_{81}, i_{83}] * (grad(v_1))[i_{83}, i_{82}]  })[i_{86}, i_{87}] * (grad(v_0))[i_{86}, i_{87}]  " == str(a7_sep._form_with_placeholders[0].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a7_sep._form_unchanged)) + "\n"
)
assert 2 == len(a7_sep._form_unchanged)
log(PROGRESS, "\tUnchanged forms:\n" +
    "\t\t" + str(a7_sep._form_unchanged[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a7_sep._form_unchanged[1].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{88}} ({ A | A_{i_{84}} = sum_{i_{85}} f_9[i_{85}] * (grad(v_1))[i_{84}, i_{85}]  })[i_{88}] * v_0[i_{88}] " == str(a7_sep._form_unchanged[0].integrals()[0].integrand())
assert "f_8 * (sum_{i_{89}} v_0[i_{89}] * v_1[i_{89}] )" == str(a7_sep._form_unchanged[1].integrals()[0].integrand())

a8 = inner(expr3*expr7*expr4*grad(u), grad(v))*dx + inner(grad(u)*expr6, v)*dx + expr5*inner(u, v)*dx
a8_sep = SeparatedParametrizedForm(a8)
log(PROGRESS, "*** ###              FORM 8             ### ***")
log(PROGRESS, "This case is similar to form 7, but the order of the matrix multiplication is different. In order not to extract separately f_6 and f_7, the whole product (even with the non-parametrized part) is extracted.")
a8_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a8_sep.coefficients)) + "\n"
)
assert 1 == len(a8_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a8_sep.coefficients[0])) + "\n"
)
assert 1 == len(a8_sep.coefficients[0])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a8_sep.coefficients[0][0]) + "\n"
)
assert "{ A | A_{i_{93}, i_{94}} = sum_{i_{95}} ({ A | A_{i_{90}, i_{91}} = sum_{i_{92}} f_6[i_{90}, i_{92}] * f_10[i_{92}, i_{91}]  })[i_{93}, i_{95}] * f_7[i_{95}, i_{94}]  }" == str(a8_sep.coefficients[0][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a8_sep._placeholders[0][0]) + "\n"
)
assert "f_42" == str(a8_sep._placeholders[0][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a8_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{102}} sum_{i_{101}} ({ A | A_{i_{96}, i_{97}} = sum_{i_{98}} f_42[i_{96}, i_{98}] * (grad(v_1))[i_{98}, i_{97}]  })[i_{101}, i_{102}] * (grad(v_0))[i_{101}, i_{102}]  " == str(a8_sep._form_with_placeholders[0].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a8_sep._form_unchanged)) + "\n"
)
assert 2 == len(a8_sep._form_unchanged)
log(PROGRESS, "\tUnchanged forms:\n" +
    "\t\t" + str(a8_sep._form_unchanged[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a8_sep._form_unchanged[1].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{103}} ({ A | A_{i_{99}} = sum_{i_{100}} f_9[i_{100}] * (grad(v_1))[i_{99}, i_{100}]  })[i_{103}] * v_0[i_{103}] " == str(a8_sep._form_unchanged[0].integrals()[0].integrand())
assert "f_8 * (sum_{i_{104}} v_0[i_{104}] * v_1[i_{104}] )" == str(a8_sep._form_unchanged[1].integrals()[0].integrand())

a9 = inner(expr9*(expr3*expr4)*grad(u), grad(v))*dx + inner(grad(u)*expr6, v)*dx + expr5*inner(u, v)*dx
a9_sep = SeparatedParametrizedForm(a9)
log(PROGRESS, "*** ###              FORM 9             ### ***")
log(PROGRESS, "This is similar to form 7, showing the trivial constants can be factored out")
a9_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a9_sep.coefficients)) + "\n"
)
assert 1 == len(a9_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a9_sep.coefficients[0])) + "\n"
)
assert 1 == len(a9_sep.coefficients[0])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a9_sep.coefficients[0][0]) + "\n"
)
assert "{ A | A_{i_{105}, i_{106}} = sum_{i_{107}} f_6[i_{105}, i_{107}] * f_7[i_{107}, i_{106}]  }" == str(a9_sep.coefficients[0][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a9_sep._placeholders[0][0]) + "\n"
)
assert "f_43" == str(a9_sep._placeholders[0][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a9_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{117}} sum_{i_{116}} ({ A | A_{i_{111}, i_{112}} = sum_{i_{113}} ({ A | A_{i_{108}, i_{109}} = sum_{i_{110}} f_12[i_{108}, i_{110}] * f_43[i_{110}, i_{109}]  })[i_{111}, i_{113}] * (grad(v_1))[i_{113}, i_{112}]  })[i_{116}, i_{117}] * (grad(v_0))[i_{116}, i_{117}]  " == str(a9_sep._form_with_placeholders[0].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a9_sep._form_unchanged)) + "\n"
)
assert 2 == len(a9_sep._form_unchanged)
log(PROGRESS, "\tUnchanged forms:\n" +
    "\t\t" + str(a9_sep._form_unchanged[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a9_sep._form_unchanged[1].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{118}} ({ A | A_{i_{114}} = sum_{i_{115}} f_9[i_{115}] * (grad(v_1))[i_{114}, i_{115}]  })[i_{118}] * v_0[i_{118}] " == str(a9_sep._form_unchanged[0].integrals()[0].integrand())
assert "f_8 * (sum_{i_{119}} v_0[i_{119}] * v_1[i_{119}] )" == str(a9_sep._form_unchanged[1].integrals()[0].integrand())

a10 = inner(expr3*expr9*expr4*grad(u), grad(v))*dx + inner(grad(u)*expr6, v)*dx + expr5*inner(u, v)*dx
a10_sep = SeparatedParametrizedForm(a10)
log(PROGRESS, "*** ###              FORM 10             ### ***")
log(PROGRESS, "This is similar to form 8, showing a case where constants cannot be factored out")
a10_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a10_sep.coefficients)) + "\n"
)
assert 1 == len(a10_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a10_sep.coefficients[0])) + "\n"
)
assert 1 == len(a10_sep.coefficients[0])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a10_sep.coefficients[0][0]) + "\n"
)
assert "{ A | A_{i_{123}, i_{124}} = sum_{i_{125}} ({ A | A_{i_{120}, i_{121}} = sum_{i_{122}} f_6[i_{120}, i_{122}] * f_12[i_{122}, i_{121}]  })[i_{123}, i_{125}] * f_7[i_{125}, i_{124}]  }" == str(a10_sep.coefficients[0][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a10_sep._placeholders[0][0]) + "\n"
)
assert "f_44" == str(a10_sep._placeholders[0][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a10_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{132}} sum_{i_{131}} ({ A | A_{i_{126}, i_{127}} = sum_{i_{128}} f_44[i_{126}, i_{128}] * (grad(v_1))[i_{128}, i_{127}]  })[i_{131}, i_{132}] * (grad(v_0))[i_{131}, i_{132}]  " == str(a10_sep._form_with_placeholders[0].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a10_sep._form_unchanged)) + "\n"
)
assert 2 == len(a10_sep._form_unchanged)
log(PROGRESS, "\tUnchanged forms:\n" +
    "\t\t" + str(a10_sep._form_unchanged[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a10_sep._form_unchanged[1].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{133}} ({ A | A_{i_{129}} = sum_{i_{130}} f_9[i_{130}] * (grad(v_1))[i_{129}, i_{130}]  })[i_{133}] * v_0[i_{133}] " == str(a10_sep._form_unchanged[0].integrals()[0].integrand())
assert "f_8 * (sum_{i_{134}} v_0[i_{134}] * v_1[i_{134}] )" == str(a10_sep._form_unchanged[1].integrals()[0].integrand())

a11 = inner(expr12*grad(u), grad(v))*dx + inner(grad(u)*expr11, v)*dx + expr10*inner(u, v)*dx
a11_sep = SeparatedParametrizedForm(a11)
log(PROGRESS, "*** ###              FORM 11             ### ***")
log(PROGRESS, "This form is similar to form 1, but each term is multiplied by a Function, which could result from a nonlinear problem")
a11_sep.separate()
log(PROGRESS, "\tLen coefficients:\n" +
    "\t\t" + str(len(a11_sep.coefficients)) + "\n"
)
assert 3 == len(a11_sep.coefficients)
log(PROGRESS, "\tSublen coefficients:\n" +
    "\t\t" + str(len(a11_sep.coefficients[0])) + "\n" +
    "\t\t" + str(len(a11_sep.coefficients[1])) + "\n" +
    "\t\t" + str(len(a11_sep.coefficients[2])) + "\n"
)
assert 1 == len(a11_sep.coefficients[0])
assert 1 == len(a11_sep.coefficients[1])
assert 1 == len(a11_sep.coefficients[2])
log(PROGRESS, "\tCoefficients:\n" +
    "\t\t" + str(a11_sep.coefficients[0][0]) + "\n" +
    "\t\t" + str(a11_sep.coefficients[1][0]) + "\n" +
    "\t\t" + str(a11_sep.coefficients[2][0]) + "\n"
)
assert "f_23" == str(a11_sep.coefficients[0][0])
assert "f_20" == str(a11_sep.coefficients[1][0])
assert "f_17" == str(a11_sep.coefficients[2][0])
log(PROGRESS, "\tPlaceholders:\n" +
    "\t\t" + str(a11_sep._placeholders[0][0]) + "\n" +
    "\t\t" + str(a11_sep._placeholders[1][0]) + "\n" +
    "\t\t" + str(a11_sep._placeholders[2][0]) + "\n"
)
assert "f_45" == str(a11_sep._placeholders[0][0])
assert "f_46" == str(a11_sep._placeholders[1][0])
assert "f_47" == str(a11_sep._placeholders[2][0])
log(PROGRESS, "\tForms with placeholders:\n" +
    "\t\t" + str(a11_sep._form_with_placeholders[0].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a11_sep._form_with_placeholders[1].integrals()[0].integrand()) + "\n" +
    "\t\t" + str(a11_sep._form_with_placeholders[2].integrals()[0].integrand()) + "\n"
)
assert "sum_{i_{141}} sum_{i_{140}} ({ A | A_{i_{135}, i_{136}} = sum_{i_{137}} f_45[i_{135}, i_{137}] * (grad(v_1))[i_{137}, i_{136}]  })[i_{140}, i_{141}] * (grad(v_0))[i_{140}, i_{141}]  " == str(a11_sep._form_with_placeholders[0].integrals()[0].integrand())
assert "sum_{i_{142}} ({ A | A_{i_{138}} = sum_{i_{139}} f_46[i_{139}] * (grad(v_1))[i_{138}, i_{139}]  })[i_{142}] * v_0[i_{142}] " == str(a11_sep._form_with_placeholders[1].integrals()[0].integrand())
assert "f_47 * (sum_{i_{143}} v_0[i_{143}] * v_1[i_{143}] )" == str(a11_sep._form_with_placeholders[2].integrals()[0].integrand())
log(PROGRESS, "\tLen unchanged forms:\n" +
    "\t\t" + str(len(a11_sep._form_unchanged)) + "\n"
)
assert 0 == len(a11_sep._form_unchanged)
