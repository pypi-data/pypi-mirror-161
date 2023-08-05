'''This Python code is an automatically generated wrapper
for Fortran code made by 'fmodpy'. The original documentation
for the Fortran source code follows.

! Module for matrix multiplication (absolutely crucial for APOS speed).
! Includes routines for orthogonalization, computing the SVD, and
! radializing data matrices with the SVD.
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
_shared_object_name = "matrix_operations." + platform.machine() + ".so"
_this_directory = os.path.dirname(os.path.abspath(__file__))
_path_to_lib = os.path.join(_this_directory, _shared_object_name)
_compile_options = ['-fPIC', '-shared', '-O3', '-lblas', '-llapack']
_ordered_dependencies = ['matrix_operations.f90', 'matrix_operations_c_wrapper.f90']
# 
# --------------------------------------------------------------------
#               AUTO-COMPILING
#
# Try to import the existing object. If that fails, recompile and then try.
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
    # Import the shared object file as a C library with ctypes.
    clib = ctypes.CDLL(_path_to_lib)
# --------------------------------------------------------------------


class matrix_operations:
    ''''''

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine GEMM
    
    def gemm(self, op_a, op_b, out_rows, out_cols, inner_dim, ab_mult, a, a_rows, b, b_rows, c_mult, c, c_rows):
        '''! Convenience wrapper routine for calling matrix multiply.'''
        
        # Setting up "op_a"
        if (type(op_a) is not ctypes.c_char): op_a = ctypes.c_char(op_a)
        
        # Setting up "op_b"
        if (type(op_b) is not ctypes.c_char): op_b = ctypes.c_char(op_b)
        
        # Setting up "out_rows"
        if (type(out_rows) is not ctypes.c_int): out_rows = ctypes.c_int(out_rows)
        
        # Setting up "out_cols"
        if (type(out_cols) is not ctypes.c_int): out_cols = ctypes.c_int(out_cols)
        
        # Setting up "inner_dim"
        if (type(inner_dim) is not ctypes.c_int): inner_dim = ctypes.c_int(inner_dim)
        
        # Setting up "ab_mult"
        if (type(ab_mult) is not ctypes.c_float): ab_mult = ctypes.c_float(ab_mult)
        
        # Setting up "a"
        if ((not issubclass(type(a), numpy.ndarray)) or
            (not numpy.asarray(a).flags.f_contiguous) or
            (not (a.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a = numpy.asarray(a, dtype=ctypes.c_float, order='F')
        a_dim_1 = ctypes.c_long(a.shape[0])
        a_dim_2 = ctypes.c_long(a.shape[1])
        
        # Setting up "a_rows"
        if (type(a_rows) is not ctypes.c_int): a_rows = ctypes.c_int(a_rows)
        
        # Setting up "b"
        if ((not issubclass(type(b), numpy.ndarray)) or
            (not numpy.asarray(b).flags.f_contiguous) or
            (not (b.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'b' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            b = numpy.asarray(b, dtype=ctypes.c_float, order='F')
        b_dim_1 = ctypes.c_long(b.shape[0])
        b_dim_2 = ctypes.c_long(b.shape[1])
        
        # Setting up "b_rows"
        if (type(b_rows) is not ctypes.c_int): b_rows = ctypes.c_int(b_rows)
        
        # Setting up "c_mult"
        if (type(c_mult) is not ctypes.c_float): c_mult = ctypes.c_float(c_mult)
        
        # Setting up "c"
        if ((not issubclass(type(c), numpy.ndarray)) or
            (not numpy.asarray(c).flags.f_contiguous) or
            (not (c.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'c' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            c = numpy.asarray(c, dtype=ctypes.c_float, order='F')
        c_dim_1 = ctypes.c_long(c.shape[0])
        c_dim_2 = ctypes.c_long(c.shape[1])
        
        # Setting up "c_rows"
        if (type(c_rows) is not ctypes.c_int): c_rows = ctypes.c_int(c_rows)
    
        # Call C-accessible Fortran wrapper.
        clib.c_gemm(ctypes.byref(op_a), ctypes.byref(op_b), ctypes.byref(out_rows), ctypes.byref(out_cols), ctypes.byref(inner_dim), ctypes.byref(ab_mult), ctypes.byref(a_dim_1), ctypes.byref(a_dim_2), ctypes.c_void_p(a.ctypes.data), ctypes.byref(a_rows), ctypes.byref(b_dim_1), ctypes.byref(b_dim_2), ctypes.c_void_p(b.ctypes.data), ctypes.byref(b_rows), ctypes.byref(c_mult), ctypes.byref(c_dim_1), ctypes.byref(c_dim_2), ctypes.c_void_p(c.ctypes.data), ctypes.byref(c_rows))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return c

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine RANDOM_UNIT_VECTORS
    
    def random_unit_vectors(self, column_vectors):
        '''! Generate randomly distributed vectors on the N-sphere.'''
        
        # Setting up "column_vectors"
        if ((not issubclass(type(column_vectors), numpy.ndarray)) or
            (not numpy.asarray(column_vectors).flags.f_contiguous) or
            (not (column_vectors.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'column_vectors' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            column_vectors = numpy.asarray(column_vectors, dtype=ctypes.c_float, order='F')
        column_vectors_dim_1 = ctypes.c_long(column_vectors.shape[0])
        column_vectors_dim_2 = ctypes.c_long(column_vectors.shape[1])
    
        # Call C-accessible Fortran wrapper.
        clib.c_random_unit_vectors(ctypes.byref(column_vectors_dim_1), ctypes.byref(column_vectors_dim_2), ctypes.c_void_p(column_vectors.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return column_vectors

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine ORTHOGONALIZE
    
    def orthogonalize(self, a, lengths, rank=None, order=None, multipliers=None):
        '''! Orthogonalize and normalize column vectors of A with pivoting.'''
        
        # Setting up "a"
        if ((not issubclass(type(a), numpy.ndarray)) or
            (not numpy.asarray(a).flags.f_contiguous) or
            (not (a.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a = numpy.asarray(a, dtype=ctypes.c_float, order='F')
        a_dim_1 = ctypes.c_long(a.shape[0])
        a_dim_2 = ctypes.c_long(a.shape[1])
        
        # Setting up "lengths"
        if ((not issubclass(type(lengths), numpy.ndarray)) or
            (not numpy.asarray(lengths).flags.f_contiguous) or
            (not (lengths.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'lengths' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            lengths = numpy.asarray(lengths, dtype=ctypes.c_float, order='F')
        lengths_dim_1 = ctypes.c_long(lengths.shape[0])
        
        # Setting up "rank"
        rank_present = ctypes.c_bool(True)
        if (rank is None):
            rank_present = ctypes.c_bool(False)
            rank = ctypes.c_int()
        else:
            rank = ctypes.c_int(rank)
        
        # Setting up "order"
        order_present = ctypes.c_bool(True)
        if (order is None):
            order_present = ctypes.c_bool(False)
            order = numpy.zeros(shape=(1), dtype=ctypes.c_int, order='F')
        elif (type(order) == bool) and (order):
            order = numpy.zeros(shape=(1), dtype=ctypes.c_int, order='F')
        elif ((not issubclass(type(order), numpy.ndarray)) or
              (not numpy.asarray(order).flags.f_contiguous) or
              (not (order.dtype == numpy.dtype(ctypes.c_int)))):
            import warnings
            warnings.warn("The provided argument 'order' was not an f_contiguous NumPy array of type 'ctypes.c_int' (or equivalent). Automatically converting (probably creating a full copy).")
            order = numpy.asarray(order, dtype=ctypes.c_int, order='F')
        if (order_present):
            order_dim_1 = ctypes.c_long(order.shape[0])
        else:
            order_dim_1 = ctypes.c_long()
        
        # Setting up "multipliers"
        multipliers_present = ctypes.c_bool(True)
        if (multipliers is None):
            multipliers_present = ctypes.c_bool(False)
            multipliers = numpy.zeros(shape=(1,1), dtype=ctypes.c_float, order='F')
        elif (type(multipliers) == bool) and (multipliers):
            multipliers = numpy.zeros(shape=(1,1), dtype=ctypes.c_float, order='F')
        elif ((not issubclass(type(multipliers), numpy.ndarray)) or
              (not numpy.asarray(multipliers).flags.f_contiguous) or
              (not (multipliers.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'multipliers' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            multipliers = numpy.asarray(multipliers, dtype=ctypes.c_float, order='F')
        if (multipliers_present):
            multipliers_dim_1 = ctypes.c_long(multipliers.shape[0])
            multipliers_dim_2 = ctypes.c_long(multipliers.shape[1])
        else:
            multipliers_dim_1 = ctypes.c_long()
            multipliers_dim_2 = ctypes.c_long()
    
        # Call C-accessible Fortran wrapper.
        clib.c_orthogonalize(ctypes.byref(a_dim_1), ctypes.byref(a_dim_2), ctypes.c_void_p(a.ctypes.data), ctypes.byref(lengths_dim_1), ctypes.c_void_p(lengths.ctypes.data), ctypes.byref(rank_present), ctypes.byref(rank), ctypes.byref(order_present), ctypes.byref(order_dim_1), ctypes.c_void_p(order.ctypes.data), ctypes.byref(multipliers_present), ctypes.byref(multipliers_dim_1), ctypes.byref(multipliers_dim_2), ctypes.c_void_p(multipliers.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return a, lengths, (rank.value if rank_present else None), (order if order_present else None), (multipliers if multipliers_present else None)

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine SVD
    
    def svd(self, a, s, vt, rank=None, steps=None, bias=None):
        '''! Compute the singular values and right singular vectors for matrix A.'''
        
        # Setting up "a"
        if ((not issubclass(type(a), numpy.ndarray)) or
            (not numpy.asarray(a).flags.f_contiguous) or
            (not (a.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a = numpy.asarray(a, dtype=ctypes.c_float, order='F')
        a_dim_1 = ctypes.c_long(a.shape[0])
        a_dim_2 = ctypes.c_long(a.shape[1])
        
        # Setting up "s"
        if ((not issubclass(type(s), numpy.ndarray)) or
            (not numpy.asarray(s).flags.f_contiguous) or
            (not (s.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 's' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            s = numpy.asarray(s, dtype=ctypes.c_float, order='F')
        s_dim_1 = ctypes.c_long(s.shape[0])
        
        # Setting up "vt"
        if ((not issubclass(type(vt), numpy.ndarray)) or
            (not numpy.asarray(vt).flags.f_contiguous) or
            (not (vt.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'vt' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            vt = numpy.asarray(vt, dtype=ctypes.c_float, order='F')
        vt_dim_1 = ctypes.c_long(vt.shape[0])
        vt_dim_2 = ctypes.c_long(vt.shape[1])
        
        # Setting up "rank"
        rank_present = ctypes.c_bool(True)
        if (rank is None):
            rank_present = ctypes.c_bool(False)
            rank = ctypes.c_int()
        else:
            rank = ctypes.c_int(rank)
        
        # Setting up "steps"
        steps_present = ctypes.c_bool(True)
        if (steps is None):
            steps_present = ctypes.c_bool(False)
            steps = ctypes.c_int()
        else:
            steps = ctypes.c_int(steps)
        if (type(steps) is not ctypes.c_int): steps = ctypes.c_int(steps)
        
        # Setting up "bias"
        bias_present = ctypes.c_bool(True)
        if (bias is None):
            bias_present = ctypes.c_bool(False)
            bias = ctypes.c_float()
        else:
            bias = ctypes.c_float(bias)
        if (type(bias) is not ctypes.c_float): bias = ctypes.c_float(bias)
    
        # Call C-accessible Fortran wrapper.
        clib.c_svd(ctypes.byref(a_dim_1), ctypes.byref(a_dim_2), ctypes.c_void_p(a.ctypes.data), ctypes.byref(s_dim_1), ctypes.c_void_p(s.ctypes.data), ctypes.byref(vt_dim_1), ctypes.byref(vt_dim_2), ctypes.c_void_p(vt.ctypes.data), ctypes.byref(rank_present), ctypes.byref(rank), ctypes.byref(steps_present), ctypes.byref(steps), ctypes.byref(bias_present), ctypes.byref(bias))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return s, vt, (rank.value if rank_present else None)

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine RADIALIZE
    
    def radialize(self, x, shift, vecs, invert_result=None, flatten=None, steps=None):
        '''! If there are at least as many data points as dimension, then
! compute the principal components and rescale the data by
! projecting onto those and rescaling so that each component has
! identical singular values (this makes the data more "radially
! symmetric").'''
        
        # Setting up "x"
        if ((not issubclass(type(x), numpy.ndarray)) or
            (not numpy.asarray(x).flags.f_contiguous) or
            (not (x.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'x' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            x = numpy.asarray(x, dtype=ctypes.c_float, order='F')
        x_dim_1 = ctypes.c_long(x.shape[0])
        x_dim_2 = ctypes.c_long(x.shape[1])
        
        # Setting up "shift"
        if ((not issubclass(type(shift), numpy.ndarray)) or
            (not numpy.asarray(shift).flags.f_contiguous) or
            (not (shift.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'shift' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            shift = numpy.asarray(shift, dtype=ctypes.c_float, order='F')
        shift_dim_1 = ctypes.c_long(shift.shape[0])
        
        # Setting up "vecs"
        if ((not issubclass(type(vecs), numpy.ndarray)) or
            (not numpy.asarray(vecs).flags.f_contiguous) or
            (not (vecs.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'vecs' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            vecs = numpy.asarray(vecs, dtype=ctypes.c_float, order='F')
        vecs_dim_1 = ctypes.c_long(vecs.shape[0])
        vecs_dim_2 = ctypes.c_long(vecs.shape[1])
        
        # Setting up "invert_result"
        invert_result_present = ctypes.c_bool(True)
        if (invert_result is None):
            invert_result_present = ctypes.c_bool(False)
            invert_result = ctypes.c_int()
        else:
            invert_result = ctypes.c_int(invert_result)
        if (type(invert_result) is not ctypes.c_int): invert_result = ctypes.c_int(invert_result)
        
        # Setting up "flatten"
        flatten_present = ctypes.c_bool(True)
        if (flatten is None):
            flatten_present = ctypes.c_bool(False)
            flatten = ctypes.c_int()
        else:
            flatten = ctypes.c_int(flatten)
        if (type(flatten) is not ctypes.c_int): flatten = ctypes.c_int(flatten)
        
        # Setting up "steps"
        steps_present = ctypes.c_bool(True)
        if (steps is None):
            steps_present = ctypes.c_bool(False)
            steps = ctypes.c_int()
        else:
            steps = ctypes.c_int(steps)
        if (type(steps) is not ctypes.c_int): steps = ctypes.c_int(steps)
    
        # Call C-accessible Fortran wrapper.
        clib.c_radialize(ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data), ctypes.byref(shift_dim_1), ctypes.c_void_p(shift.ctypes.data), ctypes.byref(vecs_dim_1), ctypes.byref(vecs_dim_2), ctypes.c_void_p(vecs.ctypes.data), ctypes.byref(invert_result_present), ctypes.byref(invert_result), ctypes.byref(flatten_present), ctypes.byref(flatten), ctypes.byref(steps_present), ctypes.byref(steps))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return x, shift, vecs

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine LEAST_SQUARES
    
    def least_squares(self, trans, a, b, x):
        '''! Perform least squares with LAPACK.
!
!   A is column vectors (of points) if TRANS='T', and row vectors
!     (of points) if TRANS='N'.
!   B must be COLUMN VECTORS of fit output (1 row = 1 point).
!   X always has a first dimension that is nonpoint axis size of A,
!     and the second dimension is determined by B's columns (or rank),
!     or (if smaller), then B is reduced to its principal components.'''
        
        # Setting up "trans"
        if (type(trans) is not ctypes.c_char): trans = ctypes.c_char(trans)
        
        # Setting up "a"
        if ((not issubclass(type(a), numpy.ndarray)) or
            (not numpy.asarray(a).flags.f_contiguous) or
            (not (a.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'a' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            a = numpy.asarray(a, dtype=ctypes.c_float, order='F')
        a_dim_1 = ctypes.c_long(a.shape[0])
        a_dim_2 = ctypes.c_long(a.shape[1])
        
        # Setting up "b"
        if ((not issubclass(type(b), numpy.ndarray)) or
            (not numpy.asarray(b).flags.f_contiguous) or
            (not (b.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'b' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            b = numpy.asarray(b, dtype=ctypes.c_float, order='F')
        b_dim_1 = ctypes.c_long(b.shape[0])
        b_dim_2 = ctypes.c_long(b.shape[1])
        
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
        clib.c_least_squares(ctypes.byref(trans), ctypes.byref(a_dim_1), ctypes.byref(a_dim_2), ctypes.c_void_p(a.ctypes.data), ctypes.byref(b_dim_1), ctypes.byref(b_dim_2), ctypes.c_void_p(b.ctypes.data), ctypes.byref(x_dim_1), ctypes.byref(x_dim_2), ctypes.c_void_p(x.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return a, b, x

matrix_operations = matrix_operations()

