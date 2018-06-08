# try:
#     import gwlfe_compiled
# except ImportError:
from numba.pycc import CC

cc = CC("gwlfe_compiled")
