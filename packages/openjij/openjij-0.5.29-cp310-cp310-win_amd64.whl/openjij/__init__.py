

""""""# start delvewheel patch
def _delvewheel_init_patch_0_0_22():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'openjij.libs'))
    if sys.version_info[:2] >= (3, 8):
        conda_workaround = os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')) and (sys.version_info[:3] < (3, 8, 13) or (3, 9, 0) <= sys.version_info[:3] < (3, 9, 9))
        if conda_workaround:
            # backup the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            conda_dll_search_modification_enable = os.environ.get('CONDA_DLL_SEARCH_MODIFICATION_ENABLE')
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = '1'
        os.add_dll_directory(libs_dir)
        if conda_workaround:
            # restore the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            if conda_dll_search_modification_enable is None:
                os.environ.pop('CONDA_DLL_SEARCH_MODIFICATION_ENABLE', None)
            else:
                os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = conda_dll_search_modification_enable
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-openjij-0.5.29')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_22()
del _delvewheel_init_patch_0_0_22
# end delvewheel patch

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

from openjij.model.model import BinaryPolynomialModel, BinaryQuadraticModel
from openjij.sampler.csqa_sampler import CSQASampler
from openjij.sampler.response import Response
from openjij.sampler.sa_sampler import SASampler
from openjij.sampler.sqa_sampler import SQASampler
from openjij.utils.benchmark import solver_benchmark
from openjij.utils.res_convertor import convert_response
from openjij.variable_type import BINARY, SPIN, Vartype, cast_vartype

__all__ = [
    "SPIN",
    "BINARY",
    "Vartype",
    "cast_vartype",
    "Response",
    "SASampler",
    "SQASampler",
    "CSQASampler",
    "BinaryQuadraticModel",
    "BinaryPolynomialModel",
    "solver_benchmark",
    "convert_response",
]
