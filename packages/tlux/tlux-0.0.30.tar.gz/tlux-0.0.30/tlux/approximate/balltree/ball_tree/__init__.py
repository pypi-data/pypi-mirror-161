'''This Python code is an automatically generated wrapper
for Fortran code made by 'fmodpy'. The original documentation
for the Fortran source code follows.

! A nearest neighbor tree structure that picks points on the convex hull and
!  splits regions in half by the 2-norm distance to the median child.
!  Construction is parallelized for shared memory architectures with OpenMP,
!  and querying is parallelized over batched query points (but serial for
!  a single query). In addition a nearest neighbor query budget can be
!  provided to generate approximate results, with the guarantee that exact
!  nearest neighbors will be found given a budget greater than the logarithm
!  base two of the number of points in the tree.
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
_shared_object_name = "ball_tree." + platform.machine() + ".so"
_this_directory = os.path.dirname(os.path.abspath(__file__))
_path_to_lib = os.path.join(_this_directory, _shared_object_name)
_compile_options = ['-fPIC', '-shared', '-O3', '-fopenmp']
_ordered_dependencies = ['libomp.dylib', 'swap.f90', 'prune.f90', 'fast_select.f90', 'fast_sort.f90', 'ball_tree.f90', 'ball_tree_c_wrapper.f90']
_symbol_files = ['libomp.dylib']# 
# --------------------------------------------------------------------
#               AUTO-COMPILING
#
# Try to import the prerequisite symbols for the compiled code.
for _ in _symbol_files:
    _ = ctypes.CDLL(os.path.join(_this_directory, _), mode=ctypes.RTLD_GLOBAL)
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


class ball_tree:
    ''''''

    # Declare 'max_copy_bytes'
    def get_max_copy_bytes(self):
        max_copy_bytes = ctypes.c_long()
        clib.ball_tree_get_max_copy_bytes(ctypes.byref(max_copy_bytes))
        return max_copy_bytes.value
    def set_max_copy_bytes(self, max_copy_bytes):
        max_copy_bytes = ctypes.c_long(max_copy_bytes)
        clib.ball_tree_set_max_copy_bytes(ctypes.byref(max_copy_bytes))
    max_copy_bytes = property(get_max_copy_bytes, set_max_copy_bytes)

    # Declare 'number_of_threads'
    def get_number_of_threads(self):
        number_of_threads = ctypes.c_int()
        clib.ball_tree_get_number_of_threads(ctypes.byref(number_of_threads))
        return number_of_threads.value
    def set_number_of_threads(self, number_of_threads):
        number_of_threads = ctypes.c_int(number_of_threads)
        clib.ball_tree_set_number_of_threads(ctypes.byref(number_of_threads))
    number_of_threads = property(get_number_of_threads, set_number_of_threads)

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine CONFIGURE
    
    def configure(self, num_threads=None, max_levels=None, nested=None):
        '''! Configure OpenMP parallelism for this ball tree code.'''
        
        # Setting up "num_threads"
        num_threads_present = ctypes.c_bool(True)
        if (num_threads is None):
            num_threads_present = ctypes.c_bool(False)
            num_threads = ctypes.c_int()
        else:
            num_threads = ctypes.c_int(num_threads)
        if (type(num_threads) is not ctypes.c_int): num_threads = ctypes.c_int(num_threads)
        
        # Setting up "max_levels"
        max_levels_present = ctypes.c_bool(True)
        if (max_levels is None):
            max_levels_present = ctypes.c_bool(False)
            max_levels = ctypes.c_int()
        else:
            max_levels = ctypes.c_int(max_levels)
        if (type(max_levels) is not ctypes.c_int): max_levels = ctypes.c_int(max_levels)
        
        # Setting up "nested"
        nested_present = ctypes.c_bool(True)
        if (nested is None):
            nested_present = ctypes.c_bool(False)
            nested = ctypes.c_int()
        else:
            nested = ctypes.c_int(nested)
        if (type(nested) is not ctypes.c_int): nested = ctypes.c_int(nested)
    
        # Call C-accessible Fortran wrapper.
        clib.c_configure(ctypes.byref(num_threads_present), ctypes.byref(num_threads), ctypes.byref(max_levels_present), ctypes.byref(max_levels), ctypes.byref(nested_present), ctypes.byref(nested))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return (num_threads.value if num_threads_present else None), (max_levels.value if max_levels_present else None), (nested.value if nested_present else None)

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine COMPUTE_SQUARE_SUMS
    
    def compute_square_sums(self, points, sq_sums):
        '''! Compute the square sums of a bunch of points (with parallelism).'''
        
        # Setting up "points"
        if ((not issubclass(type(points), numpy.ndarray)) or
            (not numpy.asarray(points).flags.f_contiguous) or
            (not (points.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'points' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            points = numpy.asarray(points, dtype=ctypes.c_float, order='F')
        points_dim_1 = ctypes.c_long(points.shape[0])
        points_dim_2 = ctypes.c_long(points.shape[1])
        
        # Setting up "sq_sums"
        if ((not issubclass(type(sq_sums), numpy.ndarray)) or
            (not numpy.asarray(sq_sums).flags.f_contiguous) or
            (not (sq_sums.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'sq_sums' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            sq_sums = numpy.asarray(sq_sums, dtype=ctypes.c_float, order='F')
        sq_sums_dim_1 = ctypes.c_long(sq_sums.shape[0])
    
        # Call C-accessible Fortran wrapper.
        clib.c_compute_square_sums(ctypes.byref(points_dim_1), ctypes.byref(points_dim_2), ctypes.c_void_p(points.ctypes.data), ctypes.byref(sq_sums_dim_1), ctypes.c_void_p(sq_sums.ctypes.data))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return sq_sums

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine BUILD_TREE
    
    def build_tree(self, points, sq_sums, radii, medians, order, root=None, leaf_size=None):
        '''! Re-arrange elements of POINTS into a binary ball tree about medians.'''
        
        # Setting up "points"
        if ((not issubclass(type(points), numpy.ndarray)) or
            (not numpy.asarray(points).flags.f_contiguous) or
            (not (points.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'points' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            points = numpy.asarray(points, dtype=ctypes.c_float, order='F')
        points_dim_1 = ctypes.c_long(points.shape[0])
        points_dim_2 = ctypes.c_long(points.shape[1])
        
        # Setting up "sq_sums"
        if ((not issubclass(type(sq_sums), numpy.ndarray)) or
            (not numpy.asarray(sq_sums).flags.f_contiguous) or
            (not (sq_sums.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'sq_sums' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            sq_sums = numpy.asarray(sq_sums, dtype=ctypes.c_float, order='F')
        sq_sums_dim_1 = ctypes.c_long(sq_sums.shape[0])
        
        # Setting up "radii"
        if ((not issubclass(type(radii), numpy.ndarray)) or
            (not numpy.asarray(radii).flags.f_contiguous) or
            (not (radii.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'radii' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            radii = numpy.asarray(radii, dtype=ctypes.c_float, order='F')
        radii_dim_1 = ctypes.c_long(radii.shape[0])
        
        # Setting up "medians"
        if ((not issubclass(type(medians), numpy.ndarray)) or
            (not numpy.asarray(medians).flags.f_contiguous) or
            (not (medians.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'medians' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            medians = numpy.asarray(medians, dtype=ctypes.c_float, order='F')
        medians_dim_1 = ctypes.c_long(medians.shape[0])
        
        # Setting up "order"
        if ((not issubclass(type(order), numpy.ndarray)) or
            (not numpy.asarray(order).flags.f_contiguous) or
            (not (order.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'order' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            order = numpy.asarray(order, dtype=ctypes.c_long, order='F')
        order_dim_1 = ctypes.c_long(order.shape[0])
        
        # Setting up "root"
        root_present = ctypes.c_bool(True)
        if (root is None):
            root_present = ctypes.c_bool(False)
            root = ctypes.c_long()
        else:
            root = ctypes.c_long(root)
        if (type(root) is not ctypes.c_long): root = ctypes.c_long(root)
        
        # Setting up "leaf_size"
        leaf_size_present = ctypes.c_bool(True)
        if (leaf_size is None):
            leaf_size_present = ctypes.c_bool(False)
            leaf_size = ctypes.c_long()
        else:
            leaf_size = ctypes.c_long(leaf_size)
        if (type(leaf_size) is not ctypes.c_long): leaf_size = ctypes.c_long(leaf_size)
    
        # Call C-accessible Fortran wrapper.
        clib.c_build_tree(ctypes.byref(points_dim_1), ctypes.byref(points_dim_2), ctypes.c_void_p(points.ctypes.data), ctypes.byref(sq_sums_dim_1), ctypes.c_void_p(sq_sums.ctypes.data), ctypes.byref(radii_dim_1), ctypes.c_void_p(radii.ctypes.data), ctypes.byref(medians_dim_1), ctypes.c_void_p(medians.ctypes.data), ctypes.byref(order_dim_1), ctypes.c_void_p(order.ctypes.data), ctypes.byref(root_present), ctypes.byref(root), ctypes.byref(leaf_size_present), ctypes.byref(leaf_size))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return points, sq_sums, radii, medians, order

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine NEAREST
    
    def nearest(self, points, k, tree, sq_sums, radii, medians, order, leaf_size, indices, dists, iwork, rwork, to_search=None, randomness=None):
        '''! Compute the K nearest elements of TREE to each point in POINTS.'''
        
        # Setting up "points"
        if ((not issubclass(type(points), numpy.ndarray)) or
            (not numpy.asarray(points).flags.f_contiguous) or
            (not (points.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'points' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            points = numpy.asarray(points, dtype=ctypes.c_float, order='F')
        points_dim_1 = ctypes.c_long(points.shape[0])
        points_dim_2 = ctypes.c_long(points.shape[1])
        
        # Setting up "k"
        if (type(k) is not ctypes.c_long): k = ctypes.c_long(k)
        
        # Setting up "tree"
        if ((not issubclass(type(tree), numpy.ndarray)) or
            (not numpy.asarray(tree).flags.f_contiguous) or
            (not (tree.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'tree' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            tree = numpy.asarray(tree, dtype=ctypes.c_float, order='F')
        tree_dim_1 = ctypes.c_long(tree.shape[0])
        tree_dim_2 = ctypes.c_long(tree.shape[1])
        
        # Setting up "sq_sums"
        if ((not issubclass(type(sq_sums), numpy.ndarray)) or
            (not numpy.asarray(sq_sums).flags.f_contiguous) or
            (not (sq_sums.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'sq_sums' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            sq_sums = numpy.asarray(sq_sums, dtype=ctypes.c_float, order='F')
        sq_sums_dim_1 = ctypes.c_long(sq_sums.shape[0])
        
        # Setting up "radii"
        if ((not issubclass(type(radii), numpy.ndarray)) or
            (not numpy.asarray(radii).flags.f_contiguous) or
            (not (radii.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'radii' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            radii = numpy.asarray(radii, dtype=ctypes.c_float, order='F')
        radii_dim_1 = ctypes.c_long(radii.shape[0])
        
        # Setting up "medians"
        if ((not issubclass(type(medians), numpy.ndarray)) or
            (not numpy.asarray(medians).flags.f_contiguous) or
            (not (medians.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'medians' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            medians = numpy.asarray(medians, dtype=ctypes.c_float, order='F')
        medians_dim_1 = ctypes.c_long(medians.shape[0])
        
        # Setting up "order"
        if ((not issubclass(type(order), numpy.ndarray)) or
            (not numpy.asarray(order).flags.f_contiguous) or
            (not (order.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'order' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            order = numpy.asarray(order, dtype=ctypes.c_long, order='F')
        order_dim_1 = ctypes.c_long(order.shape[0])
        
        # Setting up "leaf_size"
        if (type(leaf_size) is not ctypes.c_long): leaf_size = ctypes.c_long(leaf_size)
        
        # Setting up "indices"
        if ((not issubclass(type(indices), numpy.ndarray)) or
            (not numpy.asarray(indices).flags.f_contiguous) or
            (not (indices.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'indices' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            indices = numpy.asarray(indices, dtype=ctypes.c_long, order='F')
        indices_dim_1 = ctypes.c_long(indices.shape[0])
        indices_dim_2 = ctypes.c_long(indices.shape[1])
        
        # Setting up "dists"
        if ((not issubclass(type(dists), numpy.ndarray)) or
            (not numpy.asarray(dists).flags.f_contiguous) or
            (not (dists.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'dists' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            dists = numpy.asarray(dists, dtype=ctypes.c_float, order='F')
        dists_dim_1 = ctypes.c_long(dists.shape[0])
        dists_dim_2 = ctypes.c_long(dists.shape[1])
        
        # Setting up "iwork"
        if ((not issubclass(type(iwork), numpy.ndarray)) or
            (not numpy.asarray(iwork).flags.f_contiguous) or
            (not (iwork.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'iwork' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            iwork = numpy.asarray(iwork, dtype=ctypes.c_long, order='F')
        iwork_dim_1 = ctypes.c_long(iwork.shape[0])
        iwork_dim_2 = ctypes.c_long(iwork.shape[1])
        
        # Setting up "rwork"
        if ((not issubclass(type(rwork), numpy.ndarray)) or
            (not numpy.asarray(rwork).flags.f_contiguous) or
            (not (rwork.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'rwork' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            rwork = numpy.asarray(rwork, dtype=ctypes.c_float, order='F')
        rwork_dim_1 = ctypes.c_long(rwork.shape[0])
        rwork_dim_2 = ctypes.c_long(rwork.shape[1])
        
        # Setting up "to_search"
        to_search_present = ctypes.c_bool(True)
        if (to_search is None):
            to_search_present = ctypes.c_bool(False)
            to_search = ctypes.c_long()
        else:
            to_search = ctypes.c_long(to_search)
        if (type(to_search) is not ctypes.c_long): to_search = ctypes.c_long(to_search)
        
        # Setting up "randomness"
        randomness_present = ctypes.c_bool(True)
        if (randomness is None):
            randomness_present = ctypes.c_bool(False)
            randomness = ctypes.c_float()
        else:
            randomness = ctypes.c_float(randomness)
        if (type(randomness) is not ctypes.c_float): randomness = ctypes.c_float(randomness)
    
        # Call C-accessible Fortran wrapper.
        clib.c_nearest(ctypes.byref(points_dim_1), ctypes.byref(points_dim_2), ctypes.c_void_p(points.ctypes.data), ctypes.byref(k), ctypes.byref(tree_dim_1), ctypes.byref(tree_dim_2), ctypes.c_void_p(tree.ctypes.data), ctypes.byref(sq_sums_dim_1), ctypes.c_void_p(sq_sums.ctypes.data), ctypes.byref(radii_dim_1), ctypes.c_void_p(radii.ctypes.data), ctypes.byref(medians_dim_1), ctypes.c_void_p(medians.ctypes.data), ctypes.byref(order_dim_1), ctypes.c_void_p(order.ctypes.data), ctypes.byref(leaf_size), ctypes.byref(indices_dim_1), ctypes.byref(indices_dim_2), ctypes.c_void_p(indices.ctypes.data), ctypes.byref(dists_dim_1), ctypes.byref(dists_dim_2), ctypes.c_void_p(dists.ctypes.data), ctypes.byref(iwork_dim_1), ctypes.byref(iwork_dim_2), ctypes.c_void_p(iwork.ctypes.data), ctypes.byref(rwork_dim_1), ctypes.byref(rwork_dim_2), ctypes.c_void_p(rwork.ctypes.data), ctypes.byref(to_search_present), ctypes.byref(to_search), ctypes.byref(randomness_present), ctypes.byref(randomness))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return indices, dists, iwork, rwork

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine PT_NEAREST
    
    def pt_nearest(self, point, k, tree, sq_sums, radii, medians, order, leaf_size, indices, dists, randomness, checks=None, found=None, pt_ss=None, d_root=None):
        '''! Compute the K nearest elements of TREE to each point in POINTS.'''
        
        # Setting up "point"
        if ((not issubclass(type(point), numpy.ndarray)) or
            (not numpy.asarray(point).flags.f_contiguous) or
            (not (point.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'point' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            point = numpy.asarray(point, dtype=ctypes.c_float, order='F')
        point_dim_1 = ctypes.c_long(point.shape[0])
        
        # Setting up "k"
        if (type(k) is not ctypes.c_long): k = ctypes.c_long(k)
        
        # Setting up "tree"
        if ((not issubclass(type(tree), numpy.ndarray)) or
            (not numpy.asarray(tree).flags.f_contiguous) or
            (not (tree.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'tree' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            tree = numpy.asarray(tree, dtype=ctypes.c_float, order='F')
        tree_dim_1 = ctypes.c_long(tree.shape[0])
        tree_dim_2 = ctypes.c_long(tree.shape[1])
        
        # Setting up "sq_sums"
        if ((not issubclass(type(sq_sums), numpy.ndarray)) or
            (not numpy.asarray(sq_sums).flags.f_contiguous) or
            (not (sq_sums.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'sq_sums' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            sq_sums = numpy.asarray(sq_sums, dtype=ctypes.c_float, order='F')
        sq_sums_dim_1 = ctypes.c_long(sq_sums.shape[0])
        
        # Setting up "radii"
        if ((not issubclass(type(radii), numpy.ndarray)) or
            (not numpy.asarray(radii).flags.f_contiguous) or
            (not (radii.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'radii' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            radii = numpy.asarray(radii, dtype=ctypes.c_float, order='F')
        radii_dim_1 = ctypes.c_long(radii.shape[0])
        
        # Setting up "medians"
        if ((not issubclass(type(medians), numpy.ndarray)) or
            (not numpy.asarray(medians).flags.f_contiguous) or
            (not (medians.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'medians' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            medians = numpy.asarray(medians, dtype=ctypes.c_float, order='F')
        medians_dim_1 = ctypes.c_long(medians.shape[0])
        
        # Setting up "order"
        if ((not issubclass(type(order), numpy.ndarray)) or
            (not numpy.asarray(order).flags.f_contiguous) or
            (not (order.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'order' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            order = numpy.asarray(order, dtype=ctypes.c_long, order='F')
        order_dim_1 = ctypes.c_long(order.shape[0])
        
        # Setting up "leaf_size"
        if (type(leaf_size) is not ctypes.c_long): leaf_size = ctypes.c_long(leaf_size)
        
        # Setting up "indices"
        if ((not issubclass(type(indices), numpy.ndarray)) or
            (not numpy.asarray(indices).flags.f_contiguous) or
            (not (indices.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'indices' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            indices = numpy.asarray(indices, dtype=ctypes.c_long, order='F')
        indices_dim_1 = ctypes.c_long(indices.shape[0])
        
        # Setting up "dists"
        if ((not issubclass(type(dists), numpy.ndarray)) or
            (not numpy.asarray(dists).flags.f_contiguous) or
            (not (dists.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'dists' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            dists = numpy.asarray(dists, dtype=ctypes.c_float, order='F')
        dists_dim_1 = ctypes.c_long(dists.shape[0])
        
        # Setting up "randomness"
        if (type(randomness) is not ctypes.c_float): randomness = ctypes.c_float(randomness)
        
        # Setting up "checks"
        checks_present = ctypes.c_bool(True)
        if (checks is None):
            checks_present = ctypes.c_bool(False)
            checks = ctypes.c_long()
        else:
            checks = ctypes.c_long(checks)
        if (type(checks) is not ctypes.c_long): checks = ctypes.c_long(checks)
        
        # Setting up "found"
        found_present = ctypes.c_bool(True)
        if (found is None):
            found_present = ctypes.c_bool(False)
            found = ctypes.c_long()
        else:
            found = ctypes.c_long(found)
        if (type(found) is not ctypes.c_long): found = ctypes.c_long(found)
        
        # Setting up "pt_ss"
        pt_ss_present = ctypes.c_bool(True)
        if (pt_ss is None):
            pt_ss_present = ctypes.c_bool(False)
            pt_ss = ctypes.c_float()
        else:
            pt_ss = ctypes.c_float(pt_ss)
        if (type(pt_ss) is not ctypes.c_float): pt_ss = ctypes.c_float(pt_ss)
        
        # Setting up "d_root"
        d_root_present = ctypes.c_bool(True)
        if (d_root is None):
            d_root_present = ctypes.c_bool(False)
            d_root = ctypes.c_float()
        else:
            d_root = ctypes.c_float(d_root)
        if (type(d_root) is not ctypes.c_float): d_root = ctypes.c_float(d_root)
    
        # Call C-accessible Fortran wrapper.
        clib.c_pt_nearest(ctypes.byref(point_dim_1), ctypes.c_void_p(point.ctypes.data), ctypes.byref(k), ctypes.byref(tree_dim_1), ctypes.byref(tree_dim_2), ctypes.c_void_p(tree.ctypes.data), ctypes.byref(sq_sums_dim_1), ctypes.c_void_p(sq_sums.ctypes.data), ctypes.byref(radii_dim_1), ctypes.c_void_p(radii.ctypes.data), ctypes.byref(medians_dim_1), ctypes.c_void_p(medians.ctypes.data), ctypes.byref(order_dim_1), ctypes.c_void_p(order.ctypes.data), ctypes.byref(leaf_size), ctypes.byref(indices_dim_1), ctypes.c_void_p(indices.ctypes.data), ctypes.byref(dists_dim_1), ctypes.c_void_p(dists.ctypes.data), ctypes.byref(randomness), ctypes.byref(checks_present), ctypes.byref(checks), ctypes.byref(found_present), ctypes.byref(found), ctypes.byref(pt_ss_present), ctypes.byref(pt_ss), ctypes.byref(d_root_present), ctypes.byref(d_root))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return indices, dists, (checks.value if checks_present else None), (found.value if found_present else None)

    
    # ----------------------------------------------
    # Wrapper for the Fortran subroutine FIX_ORDER
    
    def fix_order(self, points, sq_sums, radii, medians, order, copy=None):
        '''! Reorganize a built tree so that it is packed in order in memory.'''
        
        # Setting up "points"
        if ((not issubclass(type(points), numpy.ndarray)) or
            (not numpy.asarray(points).flags.f_contiguous) or
            (not (points.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'points' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            points = numpy.asarray(points, dtype=ctypes.c_float, order='F')
        points_dim_1 = ctypes.c_long(points.shape[0])
        points_dim_2 = ctypes.c_long(points.shape[1])
        
        # Setting up "sq_sums"
        if ((not issubclass(type(sq_sums), numpy.ndarray)) or
            (not numpy.asarray(sq_sums).flags.f_contiguous) or
            (not (sq_sums.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'sq_sums' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            sq_sums = numpy.asarray(sq_sums, dtype=ctypes.c_float, order='F')
        sq_sums_dim_1 = ctypes.c_long(sq_sums.shape[0])
        
        # Setting up "radii"
        if ((not issubclass(type(radii), numpy.ndarray)) or
            (not numpy.asarray(radii).flags.f_contiguous) or
            (not (radii.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'radii' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            radii = numpy.asarray(radii, dtype=ctypes.c_float, order='F')
        radii_dim_1 = ctypes.c_long(radii.shape[0])
        
        # Setting up "medians"
        if ((not issubclass(type(medians), numpy.ndarray)) or
            (not numpy.asarray(medians).flags.f_contiguous) or
            (not (medians.dtype == numpy.dtype(ctypes.c_float)))):
            import warnings
            warnings.warn("The provided argument 'medians' was not an f_contiguous NumPy array of type 'ctypes.c_float' (or equivalent). Automatically converting (probably creating a full copy).")
            medians = numpy.asarray(medians, dtype=ctypes.c_float, order='F')
        medians_dim_1 = ctypes.c_long(medians.shape[0])
        
        # Setting up "order"
        if ((not issubclass(type(order), numpy.ndarray)) or
            (not numpy.asarray(order).flags.f_contiguous) or
            (not (order.dtype == numpy.dtype(ctypes.c_long)))):
            import warnings
            warnings.warn("The provided argument 'order' was not an f_contiguous NumPy array of type 'ctypes.c_long' (or equivalent). Automatically converting (probably creating a full copy).")
            order = numpy.asarray(order, dtype=ctypes.c_long, order='F')
        order_dim_1 = ctypes.c_long(order.shape[0])
        
        # Setting up "copy"
        copy_present = ctypes.c_bool(True)
        if (copy is None):
            copy_present = ctypes.c_bool(False)
            copy = ctypes.c_int()
        else:
            copy = ctypes.c_int(copy)
        if (type(copy) is not ctypes.c_int): copy = ctypes.c_int(copy)
    
        # Call C-accessible Fortran wrapper.
        clib.c_fix_order(ctypes.byref(points_dim_1), ctypes.byref(points_dim_2), ctypes.c_void_p(points.ctypes.data), ctypes.byref(sq_sums_dim_1), ctypes.c_void_p(sq_sums.ctypes.data), ctypes.byref(radii_dim_1), ctypes.c_void_p(radii.ctypes.data), ctypes.byref(medians_dim_1), ctypes.c_void_p(medians.ctypes.data), ctypes.byref(order_dim_1), ctypes.c_void_p(order.ctypes.data), ctypes.byref(copy_present), ctypes.byref(copy))
    
        # Return final results, 'INTENT(OUT)' arguments only.
        return points, sq_sums, radii, medians, order

ball_tree = ball_tree()

