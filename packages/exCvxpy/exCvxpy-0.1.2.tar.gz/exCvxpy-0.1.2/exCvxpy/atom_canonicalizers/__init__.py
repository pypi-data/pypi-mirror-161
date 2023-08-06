
from exCvxpy.atoms import *
from exCvxpy.atom_canonicalizers.tr_inv_canon import *
from cvxpy.reductions.dcp2cone.atom_canonicalizers import CANON_METHODS
CANON_METHODS[tr_inv]=tr_inv_canon