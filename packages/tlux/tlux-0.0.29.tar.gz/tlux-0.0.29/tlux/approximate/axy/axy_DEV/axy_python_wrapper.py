'''This Python code is an automatically generated wrapper
for Fortran code made by 'fmodpy'. The original documentation
for the Fortran source code follows.

! TODO:
!
! - Update FIT code to allow specifying a subset of points to be evaluated
!   at a time (i.e., support batched evaluation).
! - Rotate out the points that have the lowest expected change in error.
!
! - Add (PAIRWISE_AGGREGATION, MAX_PAIRS) functionality to the aggregator model input,
!   where a nonrepeating random number generator is used in conjunction with a mapping
!   from the integer line to pairs of points. When MAX_PAIRS is less than the total
!   number of pairs, then do greedy rotation of points identically to above.
!
! - Handle NaN and Infinity in the data normalization process, as well
!   as in model evaluation (controlled through some logical setting).
!   Replace NaN/Inf inputs with means, ignore NaN/Inf outputs in gardient.
!
! - Update CONDITION_MODEL to:
!    multiply the 2-norm of output weights by values before orthogonalization
!    compress basis weights with linear regression when rank deficiency is detected
!    reinitialize basis functions randomly at first, metric PCA best
!    sum the number of times a component had no rank across threads
!    swap weights for the no-rank components to the back
!    swap no-rank state component values into contiguous memory at back
!    linearly regress the kept-components onto the next-layer dropped difference
!    compute the first no-rank principal components of the gradient, store in droped slots
!    regress previous layer onto the gradient components
!    fill any remaining nodes (if not enough from gradient) with "uncaptured" principal components
!    set new shift terms as the best of 5 well spaced values in [-1,1], or random given no order
! - Run some tests to determine how weights should be updated on conditioning
!   to not change the output of the model *at all*, and similarly update the
!   gradient estimates to reflect those changes as well.
!
! - Update Python testing code to test all combinations of AX, AXI, AY, X, XI, and Y.
! - Update Python testing code to attempt different edge-case model sizes
!    (linear regression, no aggregator, no model).
! - Start writing a test-case suite that tests all of the basic operations.
!   Start with end-to-end tests that include "bad" input and output scaling.
! - Verify that the *condition model* operation correctly updates the gradient
!   related variables (mean and curvature).
! - Make sure that the print time actually adheres to the 3-second guidance.
!   Or optionally write updates to a designated file instead.
!
! - Make data normalization use the same work space as the fit procedure
!   (since these are not needed at the same time).
! - Make model conditioning use the same work space as evaluation (where possible).
! - Pull normalization code out and have it be called separately from 'FIT'.
!   Goal is to achieve near-zero inefficiencies for doing a few steps at a time in
!   Python (allowing for easier cancellation, progress updates, checkpoints, ...).
!
! - Use LAPACK to do linear regression, implement simple SVD + gradient descent method
!   in MATRIX_OPERATIONS, compare speed of both methodologies.
! - Implement and test Fortran native version of matrix multiplication (manual DO loop).
! - Implement and test Fortran native version of SSYRK (manual DO loop).
!
! ---------------------------------------------------------------------------
!
! NOTES:
!
! - When conditioning the model, the multipliers applied to the weight matrices
!   can affect the model gradient in nonlinear (difficult to predict) ways.
!
! - When taking adaptive optimization steps, the current architecture takes steps
!   and then projects back onto the feasible region (of the optimization space).
!   The projection is not incorporated directly into the steps, so it is possible
!   for these two operations to "fight" each other. This is ignored.
!

! An aggregator and fixed piecewise linear regression model.
'''

import os
import ctypes
import platform
import numpy

# --------------------------------------------------------------------
#               CONFIGURATION
# 
_verbose = True
_fort_compiler = "gfortran"
_shared_object_name = "axy." + platform.machine() + ".so"
_this_directory = os.path.dirname(os.path.abspath(__file__))
_path_to_lib = os.path.join(_this_directory, _shared_object_name)
_compile_options = ['-fPIC', '-shared', '-O3', '-fopenmp'] # '-fcheck=bounds', '-lblas', '-llapack', 
_ordered_dependencies = ['random.f90', 'matrix_operations.f90', 'sort_and_select.f90', 'axy.f90', 'axy_c_wrapper.f90',
                         '/Users/thomaslux/Library/Python/3.8/lib/python/site-packages/numpy/core/lib/libnpymath.a']
# 
# --------------------------------------------------------------------
#               AUTO-COMPILING
#
# Try to import the existing object. If that fails, recompile and then try.
import numpy as np
print()
print(np.show_config())
print(np.get_include())
print("Parent of include:", )
np_dir = os.path.dirname(np.get_include())
for p in os.listdir(np_dir):
    if (p[-3:] == ".a") and ("_tests" not in p):
        _ordered_dependencies.append( os.path.join(np_dir, p) )
print()
print(_ordered_dependencies)
# nplib = os.path.join(os.path.dirname(np.get_include()), "_multiarray_umath.cpython-38-darwin.so")
# nplib = "/opt/homebrew/Cellar/openblas/0.3.20/lib/libopenblas.dylib"
# nplib = ctypes.CDLL(nplib, mode=ctypes.RTLD_GLOBAL)
# print("nplib: ", nplib)
# print("os.path.exists(nplib): ", os.path.exists(nplib))
# print(dir(nplib))
# print("nplib._name: ", nplib._name)
# print("nplib._FuncPtr: ", nplib._FuncPtr)
# print("nplib._handle: ", nplib._handle)
# print("nplib._func_restype_: ", nplib._func_restype_)

# def describe_symtable(st, recursive=True, indent=0):
#     import symtable
#     def print_d(s, *args):
#         prefix = ' ' * indent
#         print(prefix + s, *args)

#     assert isinstance(st, symtable.SymbolTable)
#     print_d('Symtable: type=%s, id=%s, name=%s' % (
#                 st.get_type(), st.get_id(), st.get_name()))
#     print_d('  nested:', st.is_nested())
#     print_d('  has children:', st.has_children())
#     print_d('  identifiers:', list(st.get_identifiers()))

#     if recursive:
#         for child_st in st.get_children():
#             describe_symtable(child_st, recursive, indent + 5)

# describe_symtable(np.matmul)

# import inspect
# print("-"*70)
# print(inspect.getmodule(np.matmul))
# print(inspect.getsourcefile(np.matmul))
# exit()

# def describe_symbol(obj, compile_mode='exec'):
#     import inspect, symtable
#     symtab = symtable.symtable(inspect.getsource(obj), inspect.getsourcefile(obj), compile_mode)
#     symbols = symtab.get_symbols()
#     for sym in symbols:
#         assert type(sym) == symtable.Symbol
#         print("Symbol:", sym.get_name())
#         for prop in [
#                 'referenced', 'imported', 'parameter',
#                 'global', 'declared_global', 'local',
#                 'free', 'assigned', 'namespace']:
#             if getattr(sym, 'is_' + prop)():
#                 print('    is', prop)


# describe_symbol(np)
# exit()

try:
    clib = ctypes.CDLL(_path_to_lib)
except:
    # Remove the shared object if it exists, because it is faulty.
    if os.path.exists(_shared_object_name):
        os.remove(_shared_object_name)
    # Compile a new shared object.
    _command = " ".join([_fort_compiler] + _compile_options + ["-o", _shared_object_name] + _ordered_dependencies)
    if _verbose:
        print("Running system command with arguments")
        print("  ", _command)
    # Run the compilation command.
    import subprocess
    subprocess.run(_command, shell=True, cwd=_this_directory)
    print(' done.')
    # Import the shared object file as a C library with ctypes.
    clib = ctypes.CDLL(_path_to_lib)
# --------------------------------------------------------------------


class axy:
    ''''''
    
    # This defines a C structure that can be used to hold this defined type.
    class MODEL_CONFIG(ctypes.Structure):
        # (name, ctype) fields for this structure.
        _fields_ = [("adn", ctypes.c_int), ("ade", ctypes.c_int), ("ane", ctypes.c_int), ("ads", ctypes.c_int), ("ans", ctypes.c_int), ("ado", ctypes.c_int), ("adi", ctypes.c_int), ("adso", ctypes.c_int), ("mdn", ctypes.c_int), ("mde", ctypes.c_int), ("mne", ctypes.c_int), ("mds", ctypes.c_int), ("mns", ctypes.c_int), ("mdo", ctypes.c_int), ("mdi", ctypes.c_int), ("mdso", ctypes.c_int), ("total_size", ctypes.c_int), ("num_vars", ctypes.c_int), ("asiv", ctypes.c_int), ("aeiv", ctypes.c_int), ("asis", ctypes.c_int), ("aeis", ctypes.c_int), ("assv", ctypes.c_int), ("aesv", ctypes.c_int), ("asss", ctypes.c_int), ("aess", ctypes.c_int), ("asov", ctypes.c_int), ("aeov", ctypes.c_int), ("asev", ctypes.c_int), ("aeev", ctypes.c_int), ("msiv", ctypes.c_int), ("meiv", ctypes.c_int), ("msis", ctypes.c_int), ("meis", ctypes.c_int), ("mssv", ctypes.c_int), ("mesv", ctypes.c_int), ("msss", ctypes.c_int), ("mess", ctypes.c_int), ("msov", ctypes.c_int), ("meov", ctypes.c_int), ("msev", ctypes.c_int), ("meev", ctypes.c_int), ("aiss", ctypes.c_int), ("aise", ctypes.c_int), ("aoss", ctypes.c_int), ("aose", ctypes.c_int), ("miss", ctypes.c_int), ("mise", ctypes.c_int), ("moss", ctypes.c_int), ("mose", ctypes.c_int), ("discontinuity", ctypes.c_float), ("initial_shift_range", ctypes.c_float), ("initial_output_scale", ctypes.c_float), ("step_factor", ctypes.c_float), ("step_mean_change", ctypes.c_float), ("step_curv_change", ctypes.c_float), ("step_ay_change", ctypes.c_float), ("faster_rate", ctypes.c_float), ("slower_rate", ctypes.c_float), ("min_update_ratio", ctypes.c_float), ("min_steps_to_stability", ctypes.c_int), ("num_threads", ctypes.c_int), ("print_delay_sec", ctypes.c_int), ("steps_taken", ctypes.c_int), ("logging_step_frequency", ctypes.c_int), ("rank_check_frequency", ctypes.c_int), ("num_to_update", ctypes.c_int), ("ax_normalized", ctypes.c_bool), ("axi_normalized", ctypes.c_bool), ("ay_normalized", ctypes.c_bool), ("x_normalized", ctypes.c_bool), ("xi_normalized", ctypes.c_bool), ("y_normalized", ctypes.c_bool), ("equalize_y", ctypes.c_bool), ("encode_normalization", ctypes.c_bool), ("apply_shift", ctypes.c_bool), ("keep_best", ctypes.c_bool), ("early_stop", ctypes.c_bool), ("basis_replacement", ctypes.c_bool), ("rwork_size", ctypes.c_long), ("iwork_size", ctypes.c_long), ("na", ctypes.c_long), ("nm", ctypes.c_long), ("smg", ctypes.c_long), ("emg", ctypes.c_long), ("smgm", ctypes.c_long), ("emgm", ctypes.c_long), ("smgc", ctypes.c_long), ("emgc", ctypes.c_long), ("sbm", ctypes.c_long), ("ebm", ctypes.c_long), ("saxs", ctypes.c_long), ("eaxs", ctypes.c_long), ("saxg", ctypes.c_long), ("eaxg", ctypes.c_long), ("say", ctypes.c_long), ("eay", ctypes.c_long), ("sayg", ctypes.c_long), ("eayg", ctypes.c_long), ("smxs", ctypes.c_long), ("emxs", ctypes.c_long), ("smxg", ctypes.c_long), ("emxg", ctypes.c_long), ("syg", ctypes.c_long), ("eyg", ctypes.c_long), ("saxr", ctypes.c_long), ("eaxr", ctypes.c_long), ("saxis", ctypes.c_long), ("eaxis", ctypes.c_long), ("saxir", ctypes.c_long), ("eaxir", ctypes.c_long), ("sayr", ctypes.c_long), ("eayr", ctypes.c_long), ("smxr", ctypes.c_long), ("emxr", ctypes.c_long), ("smxis", ctypes.c_long), ("emxis", ctypes.c_long), ("smxir", ctypes.c_long), ("emxir", ctypes.c_long), ("syr", ctypes.c_long), ("eyr", ctypes.c_long), ("sal", ctypes.c_long), ("eal", ctypes.c_long), ("sml", ctypes.c_long), ("eml", ctypes.c_long), ("sast", ctypes.c_long), ("east", ctypes.c_long), ("smst", ctypes.c_long), ("emst", ctypes.c_long), ("sui", ctypes.c_long), ("eui", ctypes.c_long), ("sbas", ctypes.c_long), ("ebas", ctypes.c_long), ("sbae", ctypes.c_long), ("ebae", ctypes.c_long), ("sbms", ctypes.c_long), ("ebms", ctypes.c_long), ("sbme", ctypes.c_long), ("ebme", ctypes.c_long), ("sao", ctypes.c_long), ("eao", ctypes.c_long), ("smo", ctypes.c_long), ("emo", ctypes.c_long)]
        # Define an "__init__" that can take a class or keyword arguments as input.
        def __init__(self, value=0, **kwargs):
            # From whatever object (or dictionary) was given, assign internal values.
            self.adn = kwargs.get("adn", getattr(value, "adn", value))
            self.ade = kwargs.get("ade", getattr(value, "ade", value))
            self.ane = kwargs.get("ane", getattr(value, "ane", value))
            self.ads = kwargs.get("ads", getattr(value, "ads", value))
            self.ans = kwargs.get("ans", getattr(value, "ans", value))
            self.ado = kwargs.get("ado", getattr(value, "ado", value))
            self.adi = kwargs.get("adi", getattr(value, "adi", value))
            self.adso = kwargs.get("adso", getattr(value, "adso", value))
            self.mdn = kwargs.get("mdn", getattr(value, "mdn", value))
            self.mde = kwargs.get("mde", getattr(value, "mde", value))
            self.mne = kwargs.get("mne", getattr(value, "mne", value))
            self.mds = kwargs.get("mds", getattr(value, "mds", value))
            self.mns = kwargs.get("mns", getattr(value, "mns", value))
            self.mdo = kwargs.get("mdo", getattr(value, "mdo", value))
            self.mdi = kwargs.get("mdi", getattr(value, "mdi", value))
            self.mdso = kwargs.get("mdso", getattr(value, "mdso", value))
            self.total_size = kwargs.get("total_size", getattr(value, "total_size", value))
            self.num_vars = kwargs.get("num_vars", getattr(value, "num_vars", value))
            self.asiv = kwargs.get("asiv", getattr(value, "asiv", value))
            self.aeiv = kwargs.get("aeiv", getattr(value, "aeiv", value))
            self.asis = kwargs.get("asis", getattr(value, "asis", value))
            self.aeis = kwargs.get("aeis", getattr(value, "aeis", value))
            self.assv = kwargs.get("assv", getattr(value, "assv", value))
            self.aesv = kwargs.get("aesv", getattr(value, "aesv", value))
            self.asss = kwargs.get("asss", getattr(value, "asss", value))
            self.aess = kwargs.get("aess", getattr(value, "aess", value))
            self.asov = kwargs.get("asov", getattr(value, "asov", value))
            self.aeov = kwargs.get("aeov", getattr(value, "aeov", value))
            self.asev = kwargs.get("asev", getattr(value, "asev", value))
            self.aeev = kwargs.get("aeev", getattr(value, "aeev", value))
            self.msiv = kwargs.get("msiv", getattr(value, "msiv", value))
            self.meiv = kwargs.get("meiv", getattr(value, "meiv", value))
            self.msis = kwargs.get("msis", getattr(value, "msis", value))
            self.meis = kwargs.get("meis", getattr(value, "meis", value))
            self.mssv = kwargs.get("mssv", getattr(value, "mssv", value))
            self.mesv = kwargs.get("mesv", getattr(value, "mesv", value))
            self.msss = kwargs.get("msss", getattr(value, "msss", value))
            self.mess = kwargs.get("mess", getattr(value, "mess", value))
            self.msov = kwargs.get("msov", getattr(value, "msov", value))
            self.meov = kwargs.get("meov", getattr(value, "meov", value))
            self.msev = kwargs.get("msev", getattr(value, "msev", value))
            self.meev = kwargs.get("meev", getattr(value, "meev", value))
            self.aiss = kwargs.get("aiss", getattr(value, "aiss", value))
            self.aise = kwargs.get("aise", getattr(value, "aise", value))
            self.aoss = kwargs.get("aoss", getattr(value, "aoss", value))
            self.aose = kwargs.get("aose", getattr(value, "aose", value))
            self.miss = kwargs.get("miss", getattr(value, "miss", value))
            self.mise = kwargs.get("mise", getattr(value, "mise", value))
            self.moss = kwargs.get("moss", getattr(value, "moss", value))
            self.mose = kwargs.get("mose", getattr(value, "mose", value))
            self.discontinuity = kwargs.get("discontinuity", getattr(value, "discontinuity", value))
            self.initial_shift_range = kwargs.get("initial_shift_range", getattr(value, "initial_shift_range", value))
            self.initial_output_scale = kwargs.get("initial_output_scale", getattr(value, "initial_output_scale", value))
            self.step_factor = kwargs.get("step_factor", getattr(value, "step_factor", value))
            self.step_mean_change = kwargs.get("step_mean_change", getattr(value, "step_mean_change", value))
            self.step_curv_change = kwargs.get("step_curv_change", getattr(value, "step_curv_change", value))
            self.step_ay_change = kwargs.get("step_ay_change", getattr(value, "step_ay_change", value))
            self.faster_rate = kwargs.get("faster_rate", getattr(value, "faster_rate", value))
            self.slower_rate = kwargs.get("slower_rate", getattr(value, "slower_rate", value))
            self.min_update_ratio = kwargs.get("min_update_ratio", getattr(value, "min_update_ratio", value))
            self.min_steps_to_stability = kwargs.get("min_steps_to_stability", getattr(value, "min_steps_to_stability", value))
            self.num_threads = kwargs.get("num_threads", getattr(value, "num_threads", value))
            self.print_delay_sec = kwargs.get("print_delay_sec", getattr(value, "print_delay_sec", value))
            self.steps_taken = kwargs.get("steps_taken", getattr(value, "steps_taken", value))
            self.logging_step_frequency = kwargs.get("logging_step_frequency", getattr(value, "logging_step_frequency", value))
            self.rank_check_frequency = kwargs.get("rank_check_frequency", getattr(value, "rank_check_frequency", value))
            self.num_to_update = kwargs.get("num_to_update", getattr(value, "num_to_update", value))
            self.ax_normalized = kwargs.get("ax_normalized", getattr(value, "ax_normalized", value))
            self.axi_normalized = kwargs.get("axi_normalized", getattr(value, "axi_normalized", value))
            self.ay_normalized = kwargs.get("ay_normalized", getattr(value, "ay_normalized", value))
            self.x_normalized = kwargs.get("x_normalized", getattr(value, "x_normalized", value))
            self.xi_normalized = kwargs.get("xi_normalized", getattr(value, "xi_normalized", value))
            self.y_normalized = kwargs.get("y_normalized", getattr(value, "y_normalized", value))
            self.equalize_y = kwargs.get("equalize_y", getattr(value, "equalize_y", value))
            self.encode_normalization = kwargs.get("encode_normalization", getattr(value, "encode_normalization", value))
            self.apply_shift = kwargs.get("apply_shift", getattr(value, "apply_shift", value))
            self.keep_best = kwargs.get("keep_best", getattr(value, "keep_best", value))
            self.early_stop = kwargs.get("early_stop", getattr(value, "early_stop", value))
            self.basis_replacement = kwargs.get("basis_replacement", getattr(value, "basis_replacement", value))
            self.rwork_size = kwargs.get("rwork_size", getattr(value, "rwork_size", value))
            self.iwork_size = kwargs.get("iwork_size", getattr(value, "iwork_size", value))
            self.na = kwargs.get("na", getattr(value, "na", value))
            self.nm = kwargs.get("nm", getattr(value, "nm", value))
            self.smg = kwargs.get("smg", getattr(value, "smg", value))
            self.emg = kwargs.get("emg", getattr(value, "emg", value))
            self.smgm = kwargs.get("smgm", getattr(value, "smgm", value))
            self.emgm = kwargs.get("emgm", getattr(value, "emgm", value))
            self.smgc = kwargs.get("smgc", getattr(value, "smgc", value))
            self.emgc = kwargs.get("emgc", getattr(value, "emgc", value))
            self.sbm = kwargs.get("sbm", getattr(value, "sbm", value))
            self.ebm = kwargs.get("ebm", getattr(value, "ebm", value))
            self.saxs = kwargs.get("saxs", getattr(value, "saxs", value))
            self.eaxs = kwargs.get("eaxs", getattr(value, "eaxs", value))
            self.saxg = kwargs.get("saxg", getattr(value, "saxg", value))
            self.eaxg = kwargs.get("eaxg", getattr(value, "eaxg", value))
            self.say = kwargs.get("say", getattr(value, "say", value))
            self.eay = kwargs.get("eay", getattr(value, "eay", value))
            self.sayg = kwargs.get("sayg", getattr(value, "sayg", value))
            self.eayg = kwargs.get("eayg", getattr(value, "eayg", value))
            self.smxs = kwargs.get("smxs", getattr(value, "smxs", value))
            self.emxs = kwargs.get("emxs", getattr(value, "emxs", value))
            self.smxg = kwargs.get("smxg", getattr(value, "smxg", value))
            self.emxg = kwargs.get("emxg", getattr(value, "emxg", value))
            self.syg = kwargs.get("syg", getattr(value, "syg", value))
            self.eyg = kwargs.get("eyg", getattr(value, "eyg", value))
            self.saxr = kwargs.get("saxr", getattr(value, "saxr", value))
            self.eaxr = kwargs.get("eaxr", getattr(value, "eaxr", value))
            self.saxis = kwargs.get("saxis", getattr(value, "saxis", value))
            self.eaxis = kwargs.get("eaxis", getattr(value, "eaxis", value))
            self.saxir = kwargs.get("saxir", getattr(value, "saxir", value))
            self.eaxir = kwargs.get("eaxir", getattr(value, "eaxir", value))
            self.sayr = kwargs.get("sayr", getattr(value, "sayr", value))
            self.eayr = kwargs.get("eayr", getattr(value, "eayr", value))
            self.smxr = kwargs.get("smxr", getattr(value, "smxr", value))
            self.emxr = kwargs.get("emxr", getattr(value, "emxr", value))
            self.smxis = kwargs.get("smxis", getattr(value, "smxis", value))
            self.emxis = kwargs.get("emxis", getattr(value, "emxis", value))
            self.smxir = kwargs.get("smxir", getattr(value, "smxir", value))
            self.emxir = kwargs.get("emxir", getattr(value, "emxir", value))
            self.syr = kwargs.get("syr", getattr(value, "syr", value))
            self.eyr = kwargs.get("eyr", getattr(value, "eyr", value))
            self.sal = kwargs.get("sal", getattr(value, "sal", value))
            self.eal = kwargs.get("eal", getattr(value, "eal", value))
            self.sml = kwargs.get("sml", getattr(value, "sml", value))
            self.eml = kwargs.get("eml", getattr(value, "eml", value))
            self.sast = kwargs.get("sast", getattr(value, "sast", value))
            self.east = kwargs.get("east", getattr(value, "east", value))
            self.smst = kwargs.get("smst", getattr(value, "smst", value))
            self.emst = kwargs.get("emst", getattr(value, "emst", value))
            self.sui = kwargs.get("sui", getattr(value, "sui", value))
            self.eui = kwargs.get("eui", getattr(value, "eui", value))
            self.sbas = kwargs.get("sbas", getattr(value, "sbas", value))
            self.ebas = kwargs.get("ebas", getattr(value, "ebas", value))
            self.sbae = kwargs.get("sbae", getattr(value, "sbae", value))
            self.ebae = kwargs.get("ebae", getattr(value, "ebae", value))
            self.sbms = kwargs.get("sbms", getattr(value, "sbms", value))
            self.ebms = kwargs.get("ebms", getattr(value, "ebms", value))
            self.sbme = kwargs.get("sbme", getattr(value, "sbme", value))
            self.ebme = kwargs.get("ebme", getattr(value, "ebme", value))
            self.sao = kwargs.get("sao", getattr(value, "sao", value))
            self.eao = kwargs.get("eao", getattr(value, "eao", value))
            self.smo = kwargs.get("smo", getattr(value, "smo", value))
            self.emo = kwargs.get("emo", getattr(value, "emo", value))
        # Define a "__str__" that produces a legible summary of this type.
        def __str__(self):
            s = []
            for (n, t) in self._fields_:
                s.append( n + "=" + str(getattr(self,n)) )
            return "MODEL_CONFIG[" + ", ".join(s) + "]"
        # Define an "__eq__" method that checks equality of all fields.
        def __eq__(self, other):
            for (n, t) in self._fields_:
                if (getattr(self, n) != getattr(other, n, None)):
                    return False
            return True
    

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine NEW_MODEL_CONFIG
    
    def new_model_config(self, adn, mdn, mdo, ade=None, ane=None, ads=None, ans=None, ado=None, mde=None, mne=None, mds=None, mns=None, num_threads=None):
        '''! Generate a model configuration given state parameters for the model.
! Size related parameters.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "adn"
        if (type(adn) is not ctypes.c_int): adn = ctypes.c_int(adn)
        
        # Setting up "ade"
        ade_present = ctypes.c_bool(True)
        if (ade is None):
            ade_present = ctypes.c_bool(False)
            ade = ctypes.c_int()
        else:
            ade = ctypes.c_int(ade)
        if (type(ade) is not ctypes.c_int): ade = ctypes.c_int(ade)
        
        # Setting up "ane"
        ane_present = ctypes.c_bool(True)
        if (ane is None):
            ane_present = ctypes.c_bool(False)
            ane = ctypes.c_int()
        else:
            ane = ctypes.c_int(ane)
        if (type(ane) is not ctypes.c_int): ane = ctypes.c_int(ane)
        
        # Setting up "ads"
        ads_present = ctypes.c_bool(True)
        if (ads is None):
            ads_present = ctypes.c_bool(False)
            ads = ctypes.c_int()
        else:
            ads = ctypes.c_int(ads)
        if (type(ads) is not ctypes.c_int): ads = ctypes.c_int(ads)
        
        # Setting up "ans"
        ans_present = ctypes.c_bool(True)
        if (ans is None):
            ans_present = ctypes.c_bool(False)
            ans = ctypes.c_int()
        else:
            ans = ctypes.c_int(ans)
        if (type(ans) is not ctypes.c_int): ans = ctypes.c_int(ans)
        
        # Setting up "ado"
        ado_present = ctypes.c_bool(True)
        if (ado is None):
            ado_present = ctypes.c_bool(False)
            ado = ctypes.c_int()
        else:
            ado = ctypes.c_int(ado)
        if (type(ado) is not ctypes.c_int): ado = ctypes.c_int(ado)
        
        # Setting up "mdn"
        if (type(mdn) is not ctypes.c_int): mdn = ctypes.c_int(mdn)
        
        # Setting up "mde"
        mde_present = ctypes.c_bool(True)
        if (mde is None):
            mde_present = ctypes.c_bool(False)
            mde = ctypes.c_int()
        else:
            mde = ctypes.c_int(mde)
        if (type(mde) is not ctypes.c_int): mde = ctypes.c_int(mde)
        
        # Setting up "mne"
        mne_present = ctypes.c_bool(True)
        if (mne is None):
            mne_present = ctypes.c_bool(False)
            mne = ctypes.c_int()
        else:
            mne = ctypes.c_int(mne)
        if (type(mne) is not ctypes.c_int): mne = ctypes.c_int(mne)
        
        # Setting up "mds"
        mds_present = ctypes.c_bool(True)
        if (mds is None):
            mds_present = ctypes.c_bool(False)
            mds = ctypes.c_int()
        else:
            mds = ctypes.c_int(mds)
        if (type(mds) is not ctypes.c_int): mds = ctypes.c_int(mds)
        
        # Setting up "mns"
        mns_present = ctypes.c_bool(True)
        if (mns is None):
            mns_present = ctypes.c_bool(False)
            mns = ctypes.c_int()
        else:
            mns = ctypes.c_int(mns)
        if (type(mns) is not ctypes.c_int): mns = ctypes.c_int(mns)
        
        # Setting up "mdo"
        if (type(mdo) is not ctypes.c_int): mdo = ctypes.c_int(mdo)
        
        # Setting up "num_threads"
        num_threads_present = ctypes.c_bool(True)
        if (num_threads is None):
            num_threads_present = ctypes.c_bool(False)
            num_threads = ctypes.c_int()
        else:
            num_threads = ctypes.c_int(num_threads)
        if (type(num_threads) is not ctypes.c_int): num_threads = ctypes.c_int(num_threads)
        
        # Setting up "config"
        config = MODEL_CONFIG()
    
        # Call C-accessible Fortran wrapper.
        clib.c_new_model_config(ctypes.byref(adn), ctypes.byref(ade_present), ctypes.byref(ade), ctypes.byref(ane_present), ctypes.byref(ane), ctypes.byref(ads_present), ctypes.byref(ads), ctypes.byref(ans_present), ctypes.byref(ans), ctypes.byref(ado_present), ctypes.byref(ado), ctypes.byref(mdn), ctypes.byref(mde_present), ctypes.byref(mde), ctypes.byref(mne_present), ctypes.byref(mne), ctypes.byref(mds_present), ctypes.byref(mds), ctypes.byref(mns_present), ctypes.byref(mns), ctypes.byref(mdo), ctypes.byref(num_threads_present), ctypes.byref(num_threads), ctypes.byref(config))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return config

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine NEW_FIT_CONFIG
    
    def new_fit_config(self, nm, na, config):
        '''! Given a number of X points "NM", and a number of aggregator X points
! "NA", update the "RWORK_SIZE" and "IWORK_SIZE" attributes in "CONFIG"
! as well as all related work indices for that size data.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "nm"
        if (type(nm) is not ctypes.c_int): nm = ctypes.c_int(nm)
        
        # Setting up "na"
        if (type(na) is not ctypes.c_int): na = ctypes.c_int(na)
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
    
        # Call C-accessible Fortran wrapper.
        clib.c_new_fit_config(ctypes.byref(nm), ctypes.byref(na), ctypes.byref(config))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return config

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine INIT_MODEL
    
    def init_model(self, config, model, seed=None):
        '''! Initialize the weights for a model, optionally provide a random seed.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "seed"
        seed_present = ctypes.c_bool(True)
        if (seed is None):
            seed_present = ctypes.c_bool(False)
            seed = ctypes.c_int()
        else:
            seed = ctypes.c_int(seed)
        if (type(seed) is not ctypes.c_int): seed = ctypes.c_int(seed)
    
        # Call C-accessible Fortran wrapper.
        clib.c_init_model(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(seed_present), ctypes.byref(seed))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return model

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine CHECK_SHAPE
    
    def check_shape(self, config, model, ax, axi, sizes, x, xi, y):
        '''! Returnn nonzero INFO if any shapes or values do not match expectations.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "axi"
        if ((not issubclass(type(axi), numpy.ndarray)) or
            (not numpy.asarray(axi).flags.f_contiguous) or
            (not (axi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'axi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            axi = numpy.asarray(axi, dtype=ctypes.c_int, order='F')
        axi_dim_1 = ctypes.c_long(axi.shape[0])
        axi_dim_2 = ctypes.c_long(axi.shape[1])
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "xi"
        if ((not issubclass(type(xi), numpy.ndarray)) or
            (not numpy.asarray(xi).flags.f_contiguous) or
            (not (xi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'xi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            xi = numpy.asarray(xi, dtype=ctypes.c_int, order='F')
        xi_dim_1 = ctypes.c_long(xi.shape[0])
        xi_dim_2 = ctypes.c_long(xi.shape[1])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "info"
        info = ctypes.c_int()
    
        # Call C-accessible Fortran wrapper.
        clib.c_check_shape(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(axi_dim_1), ctypes.byref(axi_dim_2), ctypes.c_void_p(axi.ctypes.data), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(xi_dim_1), ctypes.byref(xi_dim_2), ctypes.c_void_p(xi.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(info))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return info.value

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine COMPUTE_BATCHES
    
    def compute_batches(self, num_batches, na, nm, sizes, batcha_starts, batcha_ends, batchm_starts, batchm_ends, info):
        '''! Given a number of batches, compute the batch start and ends for
!  the aggregator and positional inputs. Store in (2,_) arrays.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "num_batches"
        if (type(num_batches) is not ctypes.c_int): num_batches = ctypes.c_int(num_batches)
        
        # Setting up "na"
        if (type(na) is not ctypes.c_long): na = ctypes.c_long(na)
        
        # Setting up "nm"
        if (type(nm) is not ctypes.c_long): nm = ctypes.c_long(nm)
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "batcha_starts"
        if ((not issubclass(type(batcha_starts), numpy.ndarray)) or
            (not numpy.asarray(batcha_starts).flags.f_contiguous) or
            (not (batcha_starts.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'batcha_starts' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            batcha_starts = numpy.asarray(batcha_starts, dtype=ctypes.c_int, order='F')
        batcha_starts_dim_1 = ctypes.c_long(batcha_starts.shape[0])
        
        # Setting up "batcha_ends"
        if ((not issubclass(type(batcha_ends), numpy.ndarray)) or
            (not numpy.asarray(batcha_ends).flags.f_contiguous) or
            (not (batcha_ends.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'batcha_ends' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            batcha_ends = numpy.asarray(batcha_ends, dtype=ctypes.c_int, order='F')
        batcha_ends_dim_1 = ctypes.c_long(batcha_ends.shape[0])
        
        # Setting up "batchm_starts"
        if ((not issubclass(type(batchm_starts), numpy.ndarray)) or
            (not numpy.asarray(batchm_starts).flags.f_contiguous) or
            (not (batchm_starts.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'batchm_starts' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            batchm_starts = numpy.asarray(batchm_starts, dtype=ctypes.c_int, order='F')
        batchm_starts_dim_1 = ctypes.c_long(batchm_starts.shape[0])
        
        # Setting up "batchm_ends"
        if ((not issubclass(type(batchm_ends), numpy.ndarray)) or
            (not numpy.asarray(batchm_ends).flags.f_contiguous) or
            (not (batchm_ends.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'batchm_ends' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            batchm_ends = numpy.asarray(batchm_ends, dtype=ctypes.c_int, order='F')
        batchm_ends_dim_1 = ctypes.c_long(batchm_ends.shape[0])
        
        # Setting up "info"
        if (type(info) is not ctypes.c_int): info = ctypes.c_int(info)
    
        # Call C-accessible Fortran wrapper.
        clib.c_compute_batches(ctypes.byref(num_batches), ctypes.byref(na), ctypes.byref(nm), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(batcha_starts_dim_1), ctypes.c_void_p(batcha_starts.ctypes.data), ctypes.byref(batcha_ends_dim_1), ctypes.c_void_p(batcha_ends.ctypes.data), ctypes.byref(batchm_starts_dim_1), ctypes.c_void_p(batchm_starts.ctypes.data), ctypes.byref(batchm_ends_dim_1), ctypes.c_void_p(batchm_ends.ctypes.data), ctypes.byref(info))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return batcha_starts, batcha_ends, batchm_starts, batchm_ends, info.value

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine EMBED
    
    def embed(self, config, model, axi, xi, ax, x):
        '''! Given a model and mixed real and integer inputs, embed the integer
!  inputs into their appropriate real-value-only formats.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "axi"
        if ((not issubclass(type(axi), numpy.ndarray)) or
            (not numpy.asarray(axi).flags.f_contiguous) or
            (not (axi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'axi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            axi = numpy.asarray(axi, dtype=ctypes.c_int, order='F')
        axi_dim_1 = ctypes.c_long(axi.shape[0])
        axi_dim_2 = ctypes.c_long(axi.shape[1])
        
        # Setting up "xi"
        if ((not issubclass(type(xi), numpy.ndarray)) or
            (not numpy.asarray(xi).flags.f_contiguous) or
            (not (xi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'xi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            xi = numpy.asarray(xi, dtype=ctypes.c_int, order='F')
        xi_dim_1 = ctypes.c_long(xi.shape[0])
        xi_dim_2 = ctypes.c_long(xi.shape[1])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
    
        # Call C-accessible Fortran wrapper.
        clib.c_embed(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(axi_dim_1), ctypes.byref(axi_dim_2), ctypes.c_void_p(axi.ctypes.data), ctypes.byref(xi_dim_1), ctypes.byref(xi_dim_2), ctypes.c_void_p(xi.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return ax, x

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine EVALUATE
    
    def evaluate(self, config, model, ax, ay, sizes, x, y, a_states, m_states, info):
        '''! Evaluate the piecewise linear regression model, assume already-embedded inputs.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "ay"
        if ((not issubclass(type(ay), numpy.ndarray)) or
            (not numpy.asarray(ay).flags.f_contiguous) or
            (not (ay.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay = numpy.asarray(ay, dtype=ctypes.c_float, order='F')
        ay_dim_1 = ctypes.c_long(ay.shape[0])
        ay_dim_2 = ctypes.c_long(ay.shape[1])
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "a_states"
        if ((not issubclass(type(a_states), numpy.ndarray)) or
            (not numpy.asarray(a_states).flags.f_contiguous) or
            (not (a_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_states = numpy.asarray(a_states, dtype=ctypes.c_float, order='F')
        a_states_dim_1 = ctypes.c_long(a_states.shape[0])
        a_states_dim_2 = ctypes.c_long(a_states.shape[1])
        a_states_dim_3 = ctypes.c_long(a_states.shape[2])
        
        # Setting up "m_states"
        if ((not issubclass(type(m_states), numpy.ndarray)) or
            (not numpy.asarray(m_states).flags.f_contiguous) or
            (not (m_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_states = numpy.asarray(m_states, dtype=ctypes.c_float, order='F')
        m_states_dim_1 = ctypes.c_long(m_states.shape[0])
        m_states_dim_2 = ctypes.c_long(m_states.shape[1])
        m_states_dim_3 = ctypes.c_long(m_states.shape[2])
        
        # Setting up "info"
        if (type(info) is not ctypes.c_int): info = ctypes.c_int(info)
    
        # Call C-accessible Fortran wrapper.
        clib.c_evaluate(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(ay_dim_1), ctypes.byref(ay_dim_2), ctypes.c_void_p(ay.ctypes.data), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(a_states_dim_1), ctypes.byref(a_states_dim_2), ctypes.byref(a_states_dim_3), ctypes.c_void_p(a_states.ctypes.data), ctypes.byref(m_states_dim_1), ctypes.byref(m_states_dim_2), ctypes.byref(m_states_dim_3), ctypes.c_void_p(m_states.ctypes.data), ctypes.byref(info))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return ax, ay, x, y, a_states, m_states, info.value

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine BASIS_GRADIENT
    
    def basis_gradient(self, config, model, y, x, ax, sizes, m_states, a_states, ay, grad):
        '''! Given the values at all internal states in the model and an output
!  gradient, propogate the output gradient through the model and
!  return the gradient of all basis functions.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "m_states"
        if ((not issubclass(type(m_states), numpy.ndarray)) or
            (not numpy.asarray(m_states).flags.f_contiguous) or
            (not (m_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_states = numpy.asarray(m_states, dtype=ctypes.c_float, order='F')
        m_states_dim_1 = ctypes.c_long(m_states.shape[0])
        m_states_dim_2 = ctypes.c_long(m_states.shape[1])
        m_states_dim_3 = ctypes.c_long(m_states.shape[2])
        
        # Setting up "a_states"
        if ((not issubclass(type(a_states), numpy.ndarray)) or
            (not numpy.asarray(a_states).flags.f_contiguous) or
            (not (a_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_states = numpy.asarray(a_states, dtype=ctypes.c_float, order='F')
        a_states_dim_1 = ctypes.c_long(a_states.shape[0])
        a_states_dim_2 = ctypes.c_long(a_states.shape[1])
        a_states_dim_3 = ctypes.c_long(a_states.shape[2])
        
        # Setting up "ay"
        if ((not issubclass(type(ay), numpy.ndarray)) or
            (not numpy.asarray(ay).flags.f_contiguous) or
            (not (ay.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay = numpy.asarray(ay, dtype=ctypes.c_float, order='F')
        ay_dim_1 = ctypes.c_long(ay.shape[0])
        ay_dim_2 = ctypes.c_long(ay.shape[1])
        
        # Setting up "grad"
        if ((not issubclass(type(grad), numpy.ndarray)) or
            (not numpy.asarray(grad).flags.f_contiguous) or
            (not (grad.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'grad' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            grad = numpy.asarray(grad, dtype=ctypes.c_float, order='F')
        grad_dim_1 = ctypes.c_long(grad.shape[0])
    
        # Call C-accessible Fortran wrapper.
        clib.c_basis_gradient(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(m_states_dim_1), ctypes.byref(m_states_dim_2), ctypes.byref(m_states_dim_3), ctypes.c_void_p(m_states.ctypes.data), ctypes.byref(a_states_dim_1), ctypes.byref(a_states_dim_2), ctypes.byref(a_states_dim_3), ctypes.c_void_p(a_states.ctypes.data), ctypes.byref(ay_dim_1), ctypes.byref(ay_dim_2), ctypes.c_void_p(ay.ctypes.data), ctypes.byref(grad_dim_1), ctypes.c_void_p(grad.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return x, ax, m_states, a_states, ay, grad

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine EMBEDDING_GRADIENT
    
    def embedding_gradient(self, mde, mne, int_inputs, grad, embedding_grad):
        '''! Compute the gradient with respect to embeddings given the input
!  gradient by aggregating over the repeated occurrences of the embedding.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "mde"
        if (type(mde) is not ctypes.c_int): mde = ctypes.c_int(mde)
        
        # Setting up "mne"
        if (type(mne) is not ctypes.c_int): mne = ctypes.c_int(mne)
        
        # Setting up "int_inputs"
        if ((not issubclass(type(int_inputs), numpy.ndarray)) or
            (not numpy.asarray(int_inputs).flags.f_contiguous) or
            (not (int_inputs.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'int_inputs' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            int_inputs = numpy.asarray(int_inputs, dtype=ctypes.c_int, order='F')
        int_inputs_dim_1 = ctypes.c_long(int_inputs.shape[0])
        int_inputs_dim_2 = ctypes.c_long(int_inputs.shape[1])
        
        # Setting up "grad"
        if ((not issubclass(type(grad), numpy.ndarray)) or
            (not numpy.asarray(grad).flags.f_contiguous) or
            (not (grad.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'grad' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            grad = numpy.asarray(grad, dtype=ctypes.c_float, order='F')
        grad_dim_1 = ctypes.c_long(grad.shape[0])
        grad_dim_2 = ctypes.c_long(grad.shape[1])
        
        # Setting up "embedding_grad"
        if ((not issubclass(type(embedding_grad), numpy.ndarray)) or
            (not numpy.asarray(embedding_grad).flags.f_contiguous) or
            (not (embedding_grad.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'embedding_grad' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            embedding_grad = numpy.asarray(embedding_grad, dtype=ctypes.c_float, order='F')
        embedding_grad_dim_1 = ctypes.c_long(embedding_grad.shape[0])
        embedding_grad_dim_2 = ctypes.c_long(embedding_grad.shape[1])
    
        # Call C-accessible Fortran wrapper.
        clib.c_embedding_gradient(ctypes.byref(mde), ctypes.byref(mne), ctypes.byref(int_inputs_dim_1), ctypes.byref(int_inputs_dim_2), ctypes.c_void_p(int_inputs.ctypes.data), ctypes.byref(grad_dim_1), ctypes.byref(grad_dim_2), ctypes.c_void_p(grad.ctypes.data), ctypes.byref(embedding_grad_dim_1), ctypes.byref(embedding_grad_dim_2), ctypes.c_void_p(embedding_grad.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return embedding_grad

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine MODEL_GRADIENT
    
    def model_gradient(self, config, model, ax, axi, ay, sizes, x, xi, y, yw, sum_squared_gradient, model_grad, info, ay_gradient, y_gradient, a_grads, m_grads, a_states=None, m_states=None):
        '''! Compute the gradient of the sum of squared error of this regression
! model with respect to its variables given input and output pairs.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "axi"
        if ((not issubclass(type(axi), numpy.ndarray)) or
            (not numpy.asarray(axi).flags.f_contiguous) or
            (not (axi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'axi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            axi = numpy.asarray(axi, dtype=ctypes.c_int, order='F')
        axi_dim_1 = ctypes.c_long(axi.shape[0])
        axi_dim_2 = ctypes.c_long(axi.shape[1])
        
        # Setting up "ay"
        if ((not issubclass(type(ay), numpy.ndarray)) or
            (not numpy.asarray(ay).flags.f_contiguous) or
            (not (ay.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay = numpy.asarray(ay, dtype=ctypes.c_float, order='F')
        ay_dim_1 = ctypes.c_long(ay.shape[0])
        ay_dim_2 = ctypes.c_long(ay.shape[1])
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "xi"
        if ((not issubclass(type(xi), numpy.ndarray)) or
            (not numpy.asarray(xi).flags.f_contiguous) or
            (not (xi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'xi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            xi = numpy.asarray(xi, dtype=ctypes.c_int, order='F')
        xi_dim_1 = ctypes.c_long(xi.shape[0])
        xi_dim_2 = ctypes.c_long(xi.shape[1])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "yw"
        if ((not issubclass(type(yw), numpy.ndarray)) or
            (not numpy.asarray(yw).flags.f_contiguous) or
            (not (yw.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'yw' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            yw = numpy.asarray(yw, dtype=ctypes.c_float, order='F')
        yw_dim_1 = ctypes.c_long(yw.shape[0])
        yw_dim_2 = ctypes.c_long(yw.shape[1])
        
        # Setting up "sum_squared_gradient"
        if (type(sum_squared_gradient) is not ctypes.c_float): sum_squared_gradient = ctypes.c_float(sum_squared_gradient)
        
        # Setting up "model_grad"
        if ((not issubclass(type(model_grad), numpy.ndarray)) or
            (not numpy.asarray(model_grad).flags.f_contiguous) or
            (not (model_grad.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model_grad' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model_grad = numpy.asarray(model_grad, dtype=ctypes.c_float, order='F')
        model_grad_dim_1 = ctypes.c_long(model_grad.shape[0])
        
        # Setting up "info"
        if (type(info) is not ctypes.c_int): info = ctypes.c_int(info)
        
        # Setting up "ay_gradient"
        if ((not issubclass(type(ay_gradient), numpy.ndarray)) or
            (not numpy.asarray(ay_gradient).flags.f_contiguous) or
            (not (ay_gradient.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay_gradient' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay_gradient = numpy.asarray(ay_gradient, dtype=ctypes.c_float, order='F')
        ay_gradient_dim_1 = ctypes.c_long(ay_gradient.shape[0])
        ay_gradient_dim_2 = ctypes.c_long(ay_gradient.shape[1])
        
        # Setting up "y_gradient"
        if ((not issubclass(type(y_gradient), numpy.ndarray)) or
            (not numpy.asarray(y_gradient).flags.f_contiguous) or
            (not (y_gradient.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y_gradient' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y_gradient = numpy.asarray(y_gradient, dtype=ctypes.c_float, order='F')
        y_gradient_dim_1 = ctypes.c_long(y_gradient.shape[0])
        y_gradient_dim_2 = ctypes.c_long(y_gradient.shape[1])
        
        # Setting up "a_grads"
        if ((not issubclass(type(a_grads), numpy.ndarray)) or
            (not numpy.asarray(a_grads).flags.f_contiguous) or
            (not (a_grads.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_grads' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_grads = numpy.asarray(a_grads, dtype=ctypes.c_float, order='F')
        a_grads_dim_1 = ctypes.c_long(a_grads.shape[0])
        a_grads_dim_2 = ctypes.c_long(a_grads.shape[1])
        a_grads_dim_3 = ctypes.c_long(a_grads.shape[2])
        
        # Setting up "m_grads"
        if ((not issubclass(type(m_grads), numpy.ndarray)) or
            (not numpy.asarray(m_grads).flags.f_contiguous) or
            (not (m_grads.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_grads' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_grads = numpy.asarray(m_grads, dtype=ctypes.c_float, order='F')
        m_grads_dim_1 = ctypes.c_long(m_grads.shape[0])
        m_grads_dim_2 = ctypes.c_long(m_grads.shape[1])
        m_grads_dim_3 = ctypes.c_long(m_grads.shape[2])
        
        # Setting up "a_states"
        a_states_present = ctypes.c_bool(True)
        if (a_states is None):
            a_states_present = ctypes.c_bool(False)
            a_states = numpy.zeros(shape=(1,1,1), dtype=ctypes.c_float, order='F')
        elif (type(a_states) == bool) and (a_states):
            a_states = numpy.zeros(shape=(1,1,1), dtype=ctypes.c_float, order='F')
        elif ((not issubclass(type(a_states), numpy.ndarray)) or
              (not numpy.asarray(a_states).flags.f_contiguous) or
              (not (a_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_states = numpy.asarray(a_states, dtype=ctypes.c_float, order='F')
        if (a_states_present):
            a_states_dim_1 = ctypes.c_long(a_states.shape[0])
            a_states_dim_2 = ctypes.c_long(a_states.shape[1])
            a_states_dim_3 = ctypes.c_long(a_states.shape[2])
        else:
            a_states_dim_1 = ctypes.c_long()
            a_states_dim_2 = ctypes.c_long()
            a_states_dim_3 = ctypes.c_long()
        
        # Setting up "m_states"
        m_states_present = ctypes.c_bool(True)
        if (m_states is None):
            m_states_present = ctypes.c_bool(False)
            m_states = numpy.zeros(shape=(1,1,1), dtype=ctypes.c_float, order='F')
        elif (type(m_states) == bool) and (m_states):
            m_states = numpy.zeros(shape=(1,1,1), dtype=ctypes.c_float, order='F')
        elif ((not issubclass(type(m_states), numpy.ndarray)) or
              (not numpy.asarray(m_states).flags.f_contiguous) or
              (not (m_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_states = numpy.asarray(m_states, dtype=ctypes.c_float, order='F')
        if (m_states_present):
            m_states_dim_1 = ctypes.c_long(m_states.shape[0])
            m_states_dim_2 = ctypes.c_long(m_states.shape[1])
            m_states_dim_3 = ctypes.c_long(m_states.shape[2])
        else:
            m_states_dim_1 = ctypes.c_long()
            m_states_dim_2 = ctypes.c_long()
            m_states_dim_3 = ctypes.c_long()
    
        # Call C-accessible Fortran wrapper.
        clib.c_model_gradient(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(axi_dim_1), ctypes.byref(axi_dim_2), ctypes.c_void_p(axi.ctypes.data), ctypes.byref(ay_dim_1), ctypes.byref(ay_dim_2), ctypes.c_void_p(ay.ctypes.data), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(xi_dim_1), ctypes.byref(xi_dim_2), ctypes.c_void_p(xi.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(yw_dim_1), ctypes.byref(yw_dim_2), ctypes.c_void_p(yw.ctypes.data), ctypes.byref(sum_squared_gradient), ctypes.byref(model_grad_dim_1), ctypes.c_void_p(model_grad.ctypes.data), ctypes.byref(info), ctypes.byref(ay_gradient_dim_1), ctypes.byref(ay_gradient_dim_2), ctypes.c_void_p(ay_gradient.ctypes.data), ctypes.byref(y_gradient_dim_1), ctypes.byref(y_gradient_dim_2), ctypes.c_void_p(y_gradient.ctypes.data), ctypes.byref(a_grads_dim_1), ctypes.byref(a_grads_dim_2), ctypes.byref(a_grads_dim_3), ctypes.c_void_p(a_grads.ctypes.data), ctypes.byref(m_grads_dim_1), ctypes.byref(m_grads_dim_2), ctypes.byref(m_grads_dim_3), ctypes.c_void_p(m_grads.ctypes.data), ctypes.byref(a_states_present), ctypes.byref(a_states_dim_1), ctypes.byref(a_states_dim_2), ctypes.byref(a_states_dim_3), ctypes.c_void_p(a_states.ctypes.data), ctypes.byref(m_states_present), ctypes.byref(m_states_dim_1), ctypes.byref(m_states_dim_2), ctypes.byref(m_states_dim_3), ctypes.c_void_p(m_states.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return ax, ay, x, sum_squared_gradient.value, model_grad, info.value, ay_gradient, y_gradient, a_grads, m_grads, (a_states if a_states_present else None), (m_states if m_states_present else None)

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine NORMALIZE_DATA
    
    def normalize_data(self, config, model, ax, axi, ay, sizes, x, xi, y, yw, ax_rescale, axi_shift, axi_rescale, ay_rescale, x_rescale, xi_shift, xi_rescale, y_rescale, a_states, a_emb_vecs, m_emb_vecs, a_out_vecs, info):
        '''! Make inputs and outputs radially symmetric (to make initialization
!  more well spaced and lower the curvature of the error gradient).'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "axi"
        if ((not issubclass(type(axi), numpy.ndarray)) or
            (not numpy.asarray(axi).flags.f_contiguous) or
            (not (axi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'axi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            axi = numpy.asarray(axi, dtype=ctypes.c_int, order='F')
        axi_dim_1 = ctypes.c_long(axi.shape[0])
        axi_dim_2 = ctypes.c_long(axi.shape[1])
        
        # Setting up "ay"
        if ((not issubclass(type(ay), numpy.ndarray)) or
            (not numpy.asarray(ay).flags.f_contiguous) or
            (not (ay.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay = numpy.asarray(ay, dtype=ctypes.c_float, order='F')
        ay_dim_1 = ctypes.c_long(ay.shape[0])
        ay_dim_2 = ctypes.c_long(ay.shape[1])
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "xi"
        if ((not issubclass(type(xi), numpy.ndarray)) or
            (not numpy.asarray(xi).flags.f_contiguous) or
            (not (xi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'xi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            xi = numpy.asarray(xi, dtype=ctypes.c_int, order='F')
        xi_dim_1 = ctypes.c_long(xi.shape[0])
        xi_dim_2 = ctypes.c_long(xi.shape[1])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "yw"
        if ((not issubclass(type(yw), numpy.ndarray)) or
            (not numpy.asarray(yw).flags.f_contiguous) or
            (not (yw.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'yw' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            yw = numpy.asarray(yw, dtype=ctypes.c_float, order='F')
        yw_dim_1 = ctypes.c_long(yw.shape[0])
        yw_dim_2 = ctypes.c_long(yw.shape[1])
        
        # Setting up "ax_rescale"
        if ((not issubclass(type(ax_rescale), numpy.ndarray)) or
            (not numpy.asarray(ax_rescale).flags.f_contiguous) or
            (not (ax_rescale.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax_rescale' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax_rescale = numpy.asarray(ax_rescale, dtype=ctypes.c_float, order='F')
        ax_rescale_dim_1 = ctypes.c_long(ax_rescale.shape[0])
        ax_rescale_dim_2 = ctypes.c_long(ax_rescale.shape[1])
        
        # Setting up "axi_shift"
        if ((not issubclass(type(axi_shift), numpy.ndarray)) or
            (not numpy.asarray(axi_shift).flags.f_contiguous) or
            (not (axi_shift.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'axi_shift' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            axi_shift = numpy.asarray(axi_shift, dtype=ctypes.c_float, order='F')
        axi_shift_dim_1 = ctypes.c_long(axi_shift.shape[0])
        
        # Setting up "axi_rescale"
        if ((not issubclass(type(axi_rescale), numpy.ndarray)) or
            (not numpy.asarray(axi_rescale).flags.f_contiguous) or
            (not (axi_rescale.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'axi_rescale' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            axi_rescale = numpy.asarray(axi_rescale, dtype=ctypes.c_float, order='F')
        axi_rescale_dim_1 = ctypes.c_long(axi_rescale.shape[0])
        axi_rescale_dim_2 = ctypes.c_long(axi_rescale.shape[1])
        
        # Setting up "ay_rescale"
        if ((not issubclass(type(ay_rescale), numpy.ndarray)) or
            (not numpy.asarray(ay_rescale).flags.f_contiguous) or
            (not (ay_rescale.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay_rescale' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay_rescale = numpy.asarray(ay_rescale, dtype=ctypes.c_float, order='F')
        ay_rescale_dim_1 = ctypes.c_long(ay_rescale.shape[0])
        
        # Setting up "x_rescale"
        if ((not issubclass(type(x_rescale), numpy.ndarray)) or
            (not numpy.asarray(x_rescale).flags.f_contiguous) or
            (not (x_rescale.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x_rescale' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x_rescale = numpy.asarray(x_rescale, dtype=ctypes.c_float, order='F')
        x_rescale_dim_1 = ctypes.c_long(x_rescale.shape[0])
        x_rescale_dim_2 = ctypes.c_long(x_rescale.shape[1])
        
        # Setting up "xi_shift"
        if ((not issubclass(type(xi_shift), numpy.ndarray)) or
            (not numpy.asarray(xi_shift).flags.f_contiguous) or
            (not (xi_shift.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'xi_shift' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            xi_shift = numpy.asarray(xi_shift, dtype=ctypes.c_float, order='F')
        xi_shift_dim_1 = ctypes.c_long(xi_shift.shape[0])
        
        # Setting up "xi_rescale"
        if ((not issubclass(type(xi_rescale), numpy.ndarray)) or
            (not numpy.asarray(xi_rescale).flags.f_contiguous) or
            (not (xi_rescale.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'xi_rescale' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            xi_rescale = numpy.asarray(xi_rescale, dtype=ctypes.c_float, order='F')
        xi_rescale_dim_1 = ctypes.c_long(xi_rescale.shape[0])
        xi_rescale_dim_2 = ctypes.c_long(xi_rescale.shape[1])
        
        # Setting up "y_rescale"
        if ((not issubclass(type(y_rescale), numpy.ndarray)) or
            (not numpy.asarray(y_rescale).flags.f_contiguous) or
            (not (y_rescale.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y_rescale' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y_rescale = numpy.asarray(y_rescale, dtype=ctypes.c_float, order='F')
        y_rescale_dim_1 = ctypes.c_long(y_rescale.shape[0])
        y_rescale_dim_2 = ctypes.c_long(y_rescale.shape[1])
        
        # Setting up "a_states"
        if ((not issubclass(type(a_states), numpy.ndarray)) or
            (not numpy.asarray(a_states).flags.f_contiguous) or
            (not (a_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_states = numpy.asarray(a_states, dtype=ctypes.c_float, order='F')
        a_states_dim_1 = ctypes.c_long(a_states.shape[0])
        a_states_dim_2 = ctypes.c_long(a_states.shape[1])
        a_states_dim_3 = ctypes.c_long(a_states.shape[2])
        
        # Setting up "a_emb_vecs"
        if ((not issubclass(type(a_emb_vecs), numpy.ndarray)) or
            (not numpy.asarray(a_emb_vecs).flags.f_contiguous) or
            (not (a_emb_vecs.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_emb_vecs' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_emb_vecs = numpy.asarray(a_emb_vecs, dtype=ctypes.c_float, order='F')
        a_emb_vecs_dim_1 = ctypes.c_long(a_emb_vecs.shape[0])
        a_emb_vecs_dim_2 = ctypes.c_long(a_emb_vecs.shape[1])
        
        # Setting up "m_emb_vecs"
        if ((not issubclass(type(m_emb_vecs), numpy.ndarray)) or
            (not numpy.asarray(m_emb_vecs).flags.f_contiguous) or
            (not (m_emb_vecs.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_emb_vecs' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_emb_vecs = numpy.asarray(m_emb_vecs, dtype=ctypes.c_float, order='F')
        m_emb_vecs_dim_1 = ctypes.c_long(m_emb_vecs.shape[0])
        m_emb_vecs_dim_2 = ctypes.c_long(m_emb_vecs.shape[1])
        
        # Setting up "a_out_vecs"
        if ((not issubclass(type(a_out_vecs), numpy.ndarray)) or
            (not numpy.asarray(a_out_vecs).flags.f_contiguous) or
            (not (a_out_vecs.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_out_vecs' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_out_vecs = numpy.asarray(a_out_vecs, dtype=ctypes.c_float, order='F')
        a_out_vecs_dim_1 = ctypes.c_long(a_out_vecs.shape[0])
        a_out_vecs_dim_2 = ctypes.c_long(a_out_vecs.shape[1])
        
        # Setting up "info"
        if (type(info) is not ctypes.c_int): info = ctypes.c_int(info)
    
        # Call C-accessible Fortran wrapper.
        clib.c_normalize_data(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(axi_dim_1), ctypes.byref(axi_dim_2), ctypes.c_void_p(axi.ctypes.data), ctypes.byref(ay_dim_1), ctypes.byref(ay_dim_2), ctypes.c_void_p(ay.ctypes.data), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(xi_dim_1), ctypes.byref(xi_dim_2), ctypes.c_void_p(xi.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(yw_dim_1), ctypes.byref(yw_dim_2), ctypes.c_void_p(yw.ctypes.data), ctypes.byref(ax_rescale_dim_1), ctypes.byref(ax_rescale_dim_2), ctypes.c_void_p(ax_rescale.ctypes.data), ctypes.byref(axi_shift_dim_1), ctypes.c_void_p(axi_shift.ctypes.data), ctypes.byref(axi_rescale_dim_1), ctypes.byref(axi_rescale_dim_2), ctypes.c_void_p(axi_rescale.ctypes.data), ctypes.byref(ay_rescale_dim_1), ctypes.c_void_p(ay_rescale.ctypes.data), ctypes.byref(x_rescale_dim_1), ctypes.byref(x_rescale_dim_2), ctypes.c_void_p(x_rescale.ctypes.data), ctypes.byref(xi_shift_dim_1), ctypes.c_void_p(xi_shift.ctypes.data), ctypes.byref(xi_rescale_dim_1), ctypes.byref(xi_rescale_dim_2), ctypes.c_void_p(xi_rescale.ctypes.data), ctypes.byref(y_rescale_dim_1), ctypes.byref(y_rescale_dim_2), ctypes.c_void_p(y_rescale.ctypes.data), ctypes.byref(a_states_dim_1), ctypes.byref(a_states_dim_2), ctypes.byref(a_states_dim_3), ctypes.c_void_p(a_states.ctypes.data), ctypes.byref(a_emb_vecs_dim_1), ctypes.byref(a_emb_vecs_dim_2), ctypes.c_void_p(a_emb_vecs.ctypes.data), ctypes.byref(m_emb_vecs_dim_1), ctypes.byref(m_emb_vecs_dim_2), ctypes.c_void_p(m_emb_vecs.ctypes.data), ctypes.byref(a_out_vecs_dim_1), ctypes.byref(a_out_vecs_dim_2), ctypes.c_void_p(a_out_vecs.ctypes.data), ctypes.byref(info))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return config, model, ax, ay, x, y, yw, ax_rescale, axi_shift, axi_rescale, ay_rescale, x_rescale, xi_shift, xi_rescale, y_rescale, a_states, a_emb_vecs, m_emb_vecs, a_out_vecs, info.value

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine CONDITION_MODEL
    
    def condition_model(self, config, model, model_grad_mean, model_grad_curv, ax, axi, ay, ay_gradient, x, xi, y, y_gradient, num_threads, fit_step, a_states, m_states, a_grads, m_grads, a_lengths, m_lengths, a_state_temp, m_state_temp, a_order, m_order, total_eval_rank, total_grad_rank):
        '''! Performing conditioning related operations on this model
!  (ensure that mean squared error is effectively reduced).'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "model_grad_mean"
        if ((not issubclass(type(model_grad_mean), numpy.ndarray)) or
            (not numpy.asarray(model_grad_mean).flags.f_contiguous) or
            (not (model_grad_mean.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model_grad_mean' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model_grad_mean = numpy.asarray(model_grad_mean, dtype=ctypes.c_float, order='F')
        model_grad_mean_dim_1 = ctypes.c_long(model_grad_mean.shape[0])
        
        # Setting up "model_grad_curv"
        if ((not issubclass(type(model_grad_curv), numpy.ndarray)) or
            (not numpy.asarray(model_grad_curv).flags.f_contiguous) or
            (not (model_grad_curv.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model_grad_curv' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model_grad_curv = numpy.asarray(model_grad_curv, dtype=ctypes.c_float, order='F')
        model_grad_curv_dim_1 = ctypes.c_long(model_grad_curv.shape[0])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "axi"
        if ((not issubclass(type(axi), numpy.ndarray)) or
            (not numpy.asarray(axi).flags.f_contiguous) or
            (not (axi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'axi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            axi = numpy.asarray(axi, dtype=ctypes.c_int, order='F')
        axi_dim_1 = ctypes.c_long(axi.shape[0])
        axi_dim_2 = ctypes.c_long(axi.shape[1])
        
        # Setting up "ay"
        if ((not issubclass(type(ay), numpy.ndarray)) or
            (not numpy.asarray(ay).flags.f_contiguous) or
            (not (ay.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay = numpy.asarray(ay, dtype=ctypes.c_float, order='F')
        ay_dim_1 = ctypes.c_long(ay.shape[0])
        ay_dim_2 = ctypes.c_long(ay.shape[1])
        
        # Setting up "ay_gradient"
        if ((not issubclass(type(ay_gradient), numpy.ndarray)) or
            (not numpy.asarray(ay_gradient).flags.f_contiguous) or
            (not (ay_gradient.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ay_gradient' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ay_gradient = numpy.asarray(ay_gradient, dtype=ctypes.c_float, order='F')
        ay_gradient_dim_1 = ctypes.c_long(ay_gradient.shape[0])
        ay_gradient_dim_2 = ctypes.c_long(ay_gradient.shape[1])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "xi"
        if ((not issubclass(type(xi), numpy.ndarray)) or
            (not numpy.asarray(xi).flags.f_contiguous) or
            (not (xi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'xi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            xi = numpy.asarray(xi, dtype=ctypes.c_int, order='F')
        xi_dim_1 = ctypes.c_long(xi.shape[0])
        xi_dim_2 = ctypes.c_long(xi.shape[1])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "y_gradient"
        if ((not issubclass(type(y_gradient), numpy.ndarray)) or
            (not numpy.asarray(y_gradient).flags.f_contiguous) or
            (not (y_gradient.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y_gradient' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y_gradient = numpy.asarray(y_gradient, dtype=ctypes.c_float, order='F')
        y_gradient_dim_1 = ctypes.c_long(y_gradient.shape[0])
        y_gradient_dim_2 = ctypes.c_long(y_gradient.shape[1])
        
        # Setting up "num_threads"
        if (type(num_threads) is not ctypes.c_int): num_threads = ctypes.c_int(num_threads)
        
        # Setting up "fit_step"
        if (type(fit_step) is not ctypes.c_int): fit_step = ctypes.c_int(fit_step)
        
        # Setting up "a_states"
        if ((not issubclass(type(a_states), numpy.ndarray)) or
            (not numpy.asarray(a_states).flags.f_contiguous) or
            (not (a_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_states = numpy.asarray(a_states, dtype=ctypes.c_float, order='F')
        a_states_dim_1 = ctypes.c_long(a_states.shape[0])
        a_states_dim_2 = ctypes.c_long(a_states.shape[1])
        a_states_dim_3 = ctypes.c_long(a_states.shape[2])
        
        # Setting up "m_states"
        if ((not issubclass(type(m_states), numpy.ndarray)) or
            (not numpy.asarray(m_states).flags.f_contiguous) or
            (not (m_states.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_states' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_states = numpy.asarray(m_states, dtype=ctypes.c_float, order='F')
        m_states_dim_1 = ctypes.c_long(m_states.shape[0])
        m_states_dim_2 = ctypes.c_long(m_states.shape[1])
        m_states_dim_3 = ctypes.c_long(m_states.shape[2])
        
        # Setting up "a_grads"
        if ((not issubclass(type(a_grads), numpy.ndarray)) or
            (not numpy.asarray(a_grads).flags.f_contiguous) or
            (not (a_grads.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_grads' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_grads = numpy.asarray(a_grads, dtype=ctypes.c_float, order='F')
        a_grads_dim_1 = ctypes.c_long(a_grads.shape[0])
        a_grads_dim_2 = ctypes.c_long(a_grads.shape[1])
        a_grads_dim_3 = ctypes.c_long(a_grads.shape[2])
        
        # Setting up "m_grads"
        if ((not issubclass(type(m_grads), numpy.ndarray)) or
            (not numpy.asarray(m_grads).flags.f_contiguous) or
            (not (m_grads.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_grads' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_grads = numpy.asarray(m_grads, dtype=ctypes.c_float, order='F')
        m_grads_dim_1 = ctypes.c_long(m_grads.shape[0])
        m_grads_dim_2 = ctypes.c_long(m_grads.shape[1])
        m_grads_dim_3 = ctypes.c_long(m_grads.shape[2])
        
        # Setting up "a_lengths"
        if ((not issubclass(type(a_lengths), numpy.ndarray)) or
            (not numpy.asarray(a_lengths).flags.f_contiguous) or
            (not (a_lengths.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_lengths' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_lengths = numpy.asarray(a_lengths, dtype=ctypes.c_float, order='F')
        a_lengths_dim_1 = ctypes.c_long(a_lengths.shape[0])
        a_lengths_dim_2 = ctypes.c_long(a_lengths.shape[1])
        
        # Setting up "m_lengths"
        if ((not issubclass(type(m_lengths), numpy.ndarray)) or
            (not numpy.asarray(m_lengths).flags.f_contiguous) or
            (not (m_lengths.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_lengths' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_lengths = numpy.asarray(m_lengths, dtype=ctypes.c_float, order='F')
        m_lengths_dim_1 = ctypes.c_long(m_lengths.shape[0])
        m_lengths_dim_2 = ctypes.c_long(m_lengths.shape[1])
        
        # Setting up "a_state_temp"
        if ((not issubclass(type(a_state_temp), numpy.ndarray)) or
            (not numpy.asarray(a_state_temp).flags.f_contiguous) or
            (not (a_state_temp.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a_state_temp' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a_state_temp = numpy.asarray(a_state_temp, dtype=ctypes.c_float, order='F')
        a_state_temp_dim_1 = ctypes.c_long(a_state_temp.shape[0])
        a_state_temp_dim_2 = ctypes.c_long(a_state_temp.shape[1])
        
        # Setting up "m_state_temp"
        if ((not issubclass(type(m_state_temp), numpy.ndarray)) or
            (not numpy.asarray(m_state_temp).flags.f_contiguous) or
            (not (m_state_temp.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'm_state_temp' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            m_state_temp = numpy.asarray(m_state_temp, dtype=ctypes.c_float, order='F')
        m_state_temp_dim_1 = ctypes.c_long(m_state_temp.shape[0])
        m_state_temp_dim_2 = ctypes.c_long(m_state_temp.shape[1])
        
        # Setting up "a_order"
        if ((not issubclass(type(a_order), numpy.ndarray)) or
            (not numpy.asarray(a_order).flags.f_contiguous) or
            (not (a_order.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'a_order' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            a_order = numpy.asarray(a_order, dtype=ctypes.c_int, order='F')
        a_order_dim_1 = ctypes.c_long(a_order.shape[0])
        a_order_dim_2 = ctypes.c_long(a_order.shape[1])
        
        # Setting up "m_order"
        if ((not issubclass(type(m_order), numpy.ndarray)) or
            (not numpy.asarray(m_order).flags.f_contiguous) or
            (not (m_order.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'm_order' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            m_order = numpy.asarray(m_order, dtype=ctypes.c_int, order='F')
        m_order_dim_1 = ctypes.c_long(m_order.shape[0])
        m_order_dim_2 = ctypes.c_long(m_order.shape[1])
        
        # Setting up "total_eval_rank"
        if (type(total_eval_rank) is not ctypes.c_int): total_eval_rank = ctypes.c_int(total_eval_rank)
        
        # Setting up "total_grad_rank"
        if (type(total_grad_rank) is not ctypes.c_int): total_grad_rank = ctypes.c_int(total_grad_rank)
    
        # Call C-accessible Fortran wrapper.
        clib.c_condition_model(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(model_grad_mean_dim_1), ctypes.c_void_p(model_grad_mean.ctypes.data), ctypes.byref(model_grad_curv_dim_1), ctypes.c_void_p(model_grad_curv.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(axi_dim_1), ctypes.byref(axi_dim_2), ctypes.c_void_p(axi.ctypes.data), ctypes.byref(ay_dim_1), ctypes.byref(ay_dim_2), ctypes.c_void_p(ay.ctypes.data), ctypes.byref(ay_gradient_dim_1), ctypes.byref(ay_gradient_dim_2), ctypes.c_void_p(ay_gradient.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(xi_dim_1), ctypes.byref(xi_dim_2), ctypes.c_void_p(xi.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(y_gradient_dim_1), ctypes.byref(y_gradient_dim_2), ctypes.c_void_p(y_gradient.ctypes.data), ctypes.byref(num_threads), ctypes.byref(fit_step), ctypes.byref(a_states_dim_1), ctypes.byref(a_states_dim_2), ctypes.byref(a_states_dim_3), ctypes.c_void_p(a_states.ctypes.data), ctypes.byref(m_states_dim_1), ctypes.byref(m_states_dim_2), ctypes.byref(m_states_dim_3), ctypes.c_void_p(m_states.ctypes.data), ctypes.byref(a_grads_dim_1), ctypes.byref(a_grads_dim_2), ctypes.byref(a_grads_dim_3), ctypes.c_void_p(a_grads.ctypes.data), ctypes.byref(m_grads_dim_1), ctypes.byref(m_grads_dim_2), ctypes.byref(m_grads_dim_3), ctypes.c_void_p(m_grads.ctypes.data), ctypes.byref(a_lengths_dim_1), ctypes.byref(a_lengths_dim_2), ctypes.c_void_p(a_lengths.ctypes.data), ctypes.byref(m_lengths_dim_1), ctypes.byref(m_lengths_dim_2), ctypes.c_void_p(m_lengths.ctypes.data), ctypes.byref(a_state_temp_dim_1), ctypes.byref(a_state_temp_dim_2), ctypes.c_void_p(a_state_temp.ctypes.data), ctypes.byref(m_state_temp_dim_1), ctypes.byref(m_state_temp_dim_2), ctypes.c_void_p(m_state_temp.ctypes.data), ctypes.byref(a_order_dim_1), ctypes.byref(a_order_dim_2), ctypes.c_void_p(a_order.ctypes.data), ctypes.byref(m_order_dim_1), ctypes.byref(m_order_dim_2), ctypes.c_void_p(m_order.ctypes.data), ctypes.byref(total_eval_rank), ctypes.byref(total_grad_rank))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return model, model_grad_mean, model_grad_curv, ax, x, a_states, m_states, a_grads, m_grads, a_lengths, m_lengths, a_state_temp, m_state_temp, a_order, m_order, total_eval_rank.value, total_grad_rank.value

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine MINIMIZE_MSE
    
    def minimize_mse(self, config, model, rwork, iwork, ax, axi, sizes, x, xi, y, yw, steps, record=None):
        '''! Fit input / output pairs by minimizing mean squared error.'''
        MODEL_CONFIG = axy.MODEL_CONFIG
        
        # Setting up "config"
        if (type(config) is not MODEL_CONFIG): config = MODEL_CONFIG(config)
        
        # Setting up "model"
        if ((not issubclass(type(model), numpy.ndarray)) or
            (not numpy.asarray(model).flags.f_contiguous) or
            (not (model.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'model' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            model = numpy.asarray(model, dtype=ctypes.c_float, order='F')
        model_dim_1 = ctypes.c_long(model.shape[0])
        
        # Setting up "rwork"
        if ((not issubclass(type(rwork), numpy.ndarray)) or
            (not numpy.asarray(rwork).flags.f_contiguous) or
            (not (rwork.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'rwork' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            rwork = numpy.asarray(rwork, dtype=ctypes.c_float, order='F')
        rwork_dim_1 = ctypes.c_long(rwork.shape[0])
        
        # Setting up "iwork"
        if ((not issubclass(type(iwork), numpy.ndarray)) or
            (not numpy.asarray(iwork).flags.f_contiguous) or
            (not (iwork.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'iwork' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            iwork = numpy.asarray(iwork, dtype=ctypes.c_int, order='F')
        iwork_dim_1 = ctypes.c_long(iwork.shape[0])
        
        # Setting up "ax"
        if ((not issubclass(type(ax), numpy.ndarray)) or
            (not numpy.asarray(ax).flags.f_contiguous) or
            (not (ax.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'ax' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            ax = numpy.asarray(ax, dtype=ctypes.c_float, order='F')
        ax_dim_1 = ctypes.c_long(ax.shape[0])
        ax_dim_2 = ctypes.c_long(ax.shape[1])
        
        # Setting up "axi"
        if ((not issubclass(type(axi), numpy.ndarray)) or
            (not numpy.asarray(axi).flags.f_contiguous) or
            (not (axi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'axi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            axi = numpy.asarray(axi, dtype=ctypes.c_int, order='F')
        axi_dim_1 = ctypes.c_long(axi.shape[0])
        axi_dim_2 = ctypes.c_long(axi.shape[1])
        
        # Setting up "sizes"
        if ((not issubclass(type(sizes), numpy.ndarray)) or
            (not numpy.asarray(sizes).flags.f_contiguous) or
            (not (sizes.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'sizes' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            sizes = numpy.asarray(sizes, dtype=ctypes.c_int, order='F')
        sizes_dim_1 = ctypes.c_long(sizes.shape[0])
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "xi"
        if ((not issubclass(type(xi), numpy.ndarray)) or
            (not numpy.asarray(xi).flags.f_contiguous) or
            (not (xi.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'xi' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            xi = numpy.asarray(xi, dtype=ctypes.c_int, order='F')
        xi_dim_1 = ctypes.c_long(xi.shape[0])
        xi_dim_2 = ctypes.c_long(xi.shape[1])
        
        # Setting up "y"
        if ((not issubclass(type(y), numpy.ndarray)) or
            (not numpy.asarray(y).flags.f_contiguous) or
            (not (y.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'y' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            y = numpy.asarray(y, dtype=ctypes.c_float, order='F')
        y_dim_1 = ctypes.c_long(y.shape[0])
        y_dim_2 = ctypes.c_long(y.shape[1])
        
        # Setting up "yw"
        if ((not issubclass(type(yw), numpy.ndarray)) or
            (not numpy.asarray(yw).flags.f_contiguous) or
            (not (yw.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'yw' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            yw = numpy.asarray(yw, dtype=ctypes.c_float, order='F')
        yw_dim_1 = ctypes.c_long(yw.shape[0])
        yw_dim_2 = ctypes.c_long(yw.shape[1])
        
        # Setting up "steps"
        if (type(steps) is not ctypes.c_int): steps = ctypes.c_int(steps)
        
        # Setting up "record"
        record_present = ctypes.c_bool(True)
        if (record is None):
            record_present = ctypes.c_bool(False)
            record = numpy.zeros(shape=(1,1), dtype=ctypes.c_float, order='F')
        elif (type(record) == bool) and (record):
            record = numpy.zeros(shape=(6, steps), dtype=ctypes.c_float, order='F')
        elif ((not issubclass(type(record), numpy.ndarray)) or
              (not numpy.asarray(record).flags.f_contiguous) or
              (not (record.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'record' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            record = numpy.asarray(record, dtype=ctypes.c_float, order='F')
        if (record_present):
            record_dim_1 = ctypes.c_long(record.shape[0])
            record_dim_2 = ctypes.c_long(record.shape[1])
        else:
            record_dim_1 = ctypes.c_long()
            record_dim_2 = ctypes.c_long()
        
        # Setting up "sum_squared_error"
        sum_squared_error = ctypes.c_float()
        
        # Setting up "info"
        info = ctypes.c_int()
    
        # Call C-accessible Fortran wrapper.
        clib.c_minimize_mse(ctypes.byref(config), ctypes.byref(model_dim_1), ctypes.c_void_p(model.ctypes.data), ctypes.byref(rwork_dim_1), ctypes.c_void_p(rwork.ctypes.data), ctypes.byref(iwork_dim_1), ctypes.c_void_p(iwork.ctypes.data), ctypes.byref(ax_dim_1), ctypes.byref(ax_dim_2), ctypes.c_void_p(ax.ctypes.data), ctypes.byref(axi_dim_1), ctypes.byref(axi_dim_2), ctypes.c_void_p(axi.ctypes.data), ctypes.byref(sizes_dim_1), ctypes.c_void_p(sizes.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(xi_dim_1), ctypes.byref(xi_dim_2), ctypes.c_void_p(xi.ctypes.data), ctypes.byref(y_dim_1), ctypes.byref(y_dim_2), ctypes.c_void_p(y.ctypes.data), ctypes.byref(yw_dim_1), ctypes.byref(yw_dim_2), ctypes.c_void_p(yw.ctypes.data), ctypes.byref(steps), ctypes.byref(record_present), ctypes.byref(record_dim_1), ctypes.byref(record_dim_2), ctypes.c_void_p(record.ctypes.data), ctypes.byref(sum_squared_error), ctypes.byref(info))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return config, model, rwork, iwork, ax, x, y, yw, (record if record_present else None), sum_squared_error.value, info.value

axy = axy()

