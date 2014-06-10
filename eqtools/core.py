# This program is distributed under the terms of the GNU General Purpose License (GPL).
# Refer to http://www.gnu.org/licenses/gpl.txt
#
# This file is part of eqtools.
#
# eqtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eqtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with eqtools.  If not, see <http://www.gnu.org/licenses/>.

"""This module provides the core classes for :py:mod:`eqtools`, including the
base :py:class:`Equilibrium` class.
"""

import filewriter

import scipy
import scipy.interpolate
import scipy.integrate
import re
import warnings

class ModuleWarning(Warning):
    """Warning class to notify the user of unavailable modules.
    """
    pass

try:
    import trispline
    _has_trispline = True
except ImportError:
    warnings.warn("trispline module could not be loaded -- tricubic spline "
                  "interpolation will not be available.",
                  ModuleWarning)
    _has_trispline = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.widgets as mplw
    import matplotlib.gridspec as mplgs
    import matplotlib.patches as mpatches
    import matplotlib.path as mpath
except Exception:
    warnings.warn("matplotlib modules could not be loaded -- plotting will not "
                  "be available.",
                  ModuleWarning)


class PropertyAccessMixin(object):
    """Mixin to implement access of getter methods through a property-type
    interface without the need to apply a decorator to every property.
    
    For any getter `obj.getSomething()`, the call `obj.Something` will do the
    same thing.
    
    This is accomplished by overriding :py:meth:`__getattribute__` such that if
    an attribute `ATTR` does not exist it then attempts to call `self.getATTR()`.
    If `self.getATTR()` does not exist, an :py:class:`AttributeError` will be
    raised as usual.
    
    Also overrides :py:meth:`__setattr__` such that it will raise an
    :py:class:`AttributeError` when attempting to write an attribute `ATTR` for
    which there is already a method `getATTR`.
    """
    def __getattribute__(self, name):
        """Get an attribute.
        
        Tries to get attribute as-written. If this fails, tries to call the
        method `get<name>` with no arguments. If this fails, raises
        :py:class:`AttributeError`. This effectively generates a Python
        'property' for each getter method.
        
        Args:
            name (String): Name of the attribute to retrieve. If the instance
                has an attribute with this name, the attribute is returned. If
                the instance does not have an attribute with this name but does
                have a method called 'get'+name, this method is called and the
                result is returned.
        
        Returns:
            The value of the attribute requested.
        
        Raises:
            AttributeError: If neither attribute name or method 'get'+name exist.
        """
        try:
            return super(Equilibrium, self).__getattribute__(name)
        except AttributeError:
            try:
                return super(Equilibrium, self).__getattribute__('get'+name)()
            except AttributeError:
                raise AttributeError(
                    "%(class)s object has no attribute '%(n)s' or method 'get%(n)s'"
                    % {'class': self.__class__.__name__, 'n': name}
                )

    def __setattr__(self, name, value):
        """Set an attribute.
        
        Raises :py:class:`AttributeError` if the object already has a method
        'get'+name, as creation of such an attribute would interfere with the
        automatic property generation in :py:meth:`__getattribute__`.
        
        Args:
            name (String): Name of the attribute to set.
            value (Object): Value to set the attribute to.
        
        Raises:
            AttributeError: If a method called 'get'+name already exists.
        """
        if hasattr(self, 'get'+name):
            raise AttributeError(
                "%(class)s object already has getter method 'get%(n)s', creating "
                "attribute '%(n)s' will conflict with automatic property "
                "generation." % {'class': self.__class__.__name__, 'n': name}
            )
        else:
            super(Equilibrium, self).__setattr__(name, value)

"""The following is a dictionary to implement length unit conversions. The first
key is the unit are converting FROM, the second the unit you are converting TO.
Supports: m, cm, mm, in, ft, yd, smoot, cubit, hand
"""
_length_conversion = {'m': {'m': 1.0,
                            'cm': 100.0,
                            'mm': 1000.0,
                            'in': 39.37,
                            'ft': 39.37 / 12.0,
                            'yd': 39.37 / (12.0 * 3.0),
                            'smoot': 39.37 / 67.0,
                            'cubit': 39.37 / 18.0,
                            'hand': 39.37 / 4.0},
                      'cm': {'m': 0.01,
                             'cm': 1.0,
                             'mm': 10.0,
                             'in': 39.37 / 100.0,
                             'ft': 39.37 / (100.0 * 12.0),
                             'yd': 39.37 / (100.0 * 12.0 * 3.0),
                             'smoot': 39.37 / (100.0 * 67.0),
                             'cubit': 39.37 / (100.0 * 18.0),
                             'hand': 39.37 / (100.0 * 4.0)},
                      'mm': {'m': 0.001,
                             'cm': 0.1,
                             'mm': 1.0,
                             'in': 39.37 / 1000.0,
                             'ft': 39.37 / (1000.0 * 12.0),
                             'yd': 39.37 / (1000.0 * 12.0 * 3.0),
                             'smoot': 39.37 / (1000.0 * 67.0),
                             'cubit': 39.37 / (1000.0 * 18.0),
                             'hand': 39.37 / (1000.0 * 4.0)},
                      'in': {'m': 1.0 / 39.37,
                             'cm': 100.0 / 39.37,
                             'mm': 1000.0 / 39.37,
                             'in': 1.0,
                             'ft': 1.0 / 12.0,
                             'yd': 1.0 / (12.0 * 3.0),
                             'smoot': 1.0 / 67.0,
                             'cubit': 1.0 / 18.0,
                             'hand': 1.0 / 4.0},
                      'ft': {'m': 12.0 / 39.37,
                             'cm': 12.0 * 100.0 / 39.37,
                             'mm': 12.0 * 1000.0 / 39.37,
                             'in': 12.0,
                             'ft': 1.0,
                             'yd': 1.0 / 3.0,
                             'smoot': 12.0 / 67.0,
                             'cubit': 12.0 / 18.0,
                             'hand': 12.0 / 4.0},
                      'yd': {'m': 3.0 * 12.0 / 39.37,
                             'cm': 3.0 * 12.0 * 100.0 / 39.37,
                             'mm': 3.0 * 12.0 * 1000.0 / 39.37,
                             'in': 3.0 * 12.0,
                             'ft': 3.0,
                             'yd': 1.0,
                             'smoot': 3.0 * 12.0 / 67.0,
                             'cubit': 3.0 * 12.0 / 18.0,
                             'hand': 3.0 * 12.0 / 4.0},
                      'smoot': {'m': 67.0 / 39.37,
                                'cm': 67.0 * 100.0 / 39.37,
                                'mm': 67.0 * 1000.0 / 39.37,
                                'in': 67.0,
                                'ft': 67.0 / 12.0,
                                'yd': 67.0 / (12.0 * 3.0),
                                'smoot': 1.0,
                                'cubit': 67.0 / 18.0,
                                'hand': 67.0 / 4.0},
                      'cubit': {'m': 18.0 / 39.37,
                                'cm': 18.0 * 100.0 / 39.37,
                                'mm': 18.0 * 1000.0 / 39.37,
                                'in': 18.0,
                                'ft': 18.0 / 12.0,
                                'yd': 18.0 / (12.0 * 3.0),
                                'smoot': 18.0 / 67.0,
                                'cubit': 1.0,
                                'hand': 18.0 / 4.0},
                      'hand': {'m': 4.0 / 39.37,
                               'cm': 4.0 * 100.0 / 39.37,
                               'mm': 4.0 * 1000.0 / 39.37,
                               'in': 4.0,
                               'ft': 4.0 / 12.0,
                               'yd': 4.0 / (12.0 * 3.0),
                               'smoot': 4.0 / 67.0,
                               'cubit': 4.0 / 18.0,
                               'hand': 1.0}}


def inPolygon(polyx, polyy, pointx, pointy):
    """Function calculating whether a given point is within a 2D polygon.

    Given an array of X,Y coordinates describing a 2D polygon, checks whether a
    point given by x,y coordinates lies within the polygon. Operates via a
    ray-casting approach - the function projects a semi-infinite ray parallel to
    the positive horizontal axis, and counts how many edges of the polygon this
    ray intersects. For a simply-connected polygon, this determines whether the
    point is inside (even number of crossings) or outside (odd number of
    crossings) the polygon, by the Jordan Curve Theorem.

    Args:
        polyx (Array-like): Array of x-coordinates of the vertices of the polygon.
        polyy (Array-like): Array of y-coordinates of the vertices of the polygon.
        pointx (Int or float): x-coordinate of test point.
        pointy (Int or float): y-coordinate of test point.

    Returns:
        result (Boolean): True/False result for whether the point is contained within the polygon.
    """
    #generator function for "lines" - pairs of (x,y) coords describing each edge of the polygon.
    def lines():
        p0x = polyx[-1]
        p0y = polyy[-1]
        p0 = (p0x,p0y)
        for i,x in enumerate(polyx):
            y = polyy[i]
            p1 = (x,y)
            yield p0,p1
            p0 = p1

    result = False
    for p0,p1 in lines():
        if ((p0[1] > pointy) != (p1[1] > pointy)) and (pointx < ((p1[0]-p0[0])*(pointy-p0[1])/(p1[1]-p0[1]) + p0[0])):
                result = not result

    return result


class Equilibrium(object):
    """Abstract class of data handling object for magnetic reconstruction outputs.
    
    Defines the mapping routines and method fingerprints necessary. Each
    variable or set of variables is recovered with a corresponding getter method.
    Essential data for mapping are pulled on initialization (psirz grid, for
    example) to frontload overhead. Additional data are pulled at the first
    request and stored for subsequent usage.

    .. note:: This abstract class should not be used directly. Device- and code-
        specific subclasses are set up to account for inter-device/-code
        differences in data storage.
    
    Keyword Args:
        length_unit (String): Sets the base unit used for any quantity whose
            dimensions are length to any power. Valid options are:
            
                ===========  ===========================================================================================
                'm'          meters
                'cm'         centimeters
                'mm'         millimeters
                'in'         inches
                'ft'         feet
                'yd'         yards
                'smoot'      smoots
                'cubit'      cubits
                'hand'       hands
                'default'    whatever the default in the tree is (no conversion is performed, units may be inconsistent)
                ===========  ===========================================================================================
            
            Default is 'm' (all units taken and returned in meters).
        tspline (Boolean): Sets whether or not interpolation in time is
            performed using a tricubic spline or nearest-neighbor interpolation.
            Tricubic spline interpolation requires at least four complete
            equilibria at different times. It is also assumed that they are
            functionally correlated, and that parameters do not vary out of
            their boundaries (derivative = 0 boundary condition). Default is
            False (use nearest-neighbor interpolation).
        monotonic (Boolean): Sets whether or not the "monotonic" form of time
            window finding is used. If True, the timebase must be monotonically
            increasing. Default is False (use slower, safer method).
        verbose (Boolean): Allows or blocks console readout during operation.
            Defaults to True, displaying useful information for the user. Set to
            False for quiet usage or to avoid console clutter for multiple
            instances.
    
    Raises:
        ValueError: If `length_unit` is not a valid unit specifier.
        ValueError: If `tspline` is True but module trispline did not load
            successfully.
    """
    def __init__(self, length_unit='m', tspline=False, monotonic=False, verbose=True):
        if length_unit != 'default' and not (length_unit in _length_conversion):
            raise ValueError("Unit '%s' not a valid unit specifier!" % length_unit)
        else:
            self._length_unit = length_unit
        
        self._tricubic = bool(tspline)
        self._monotonic = bool(monotonic)
        self._verbose = bool(verbose)
            
        # These are indexes of splines, and become higher dimensional splines
        # with the setting of the tspline keyword.
        self._psiOfRZSpline = {}
        self._phiNormSpline = {}
        self._volNormSpline = {}
        self._RmidSpline = {}
        self._magRSpline = {}
        self._magZSpline = {}
        self._RmidOutSpline = {}
        self._psiOfPsi0Spline = {}
        self._psiOfLCFSSpline = {}
        self._RmidToPsiNormSpline = {}
        self._phiNormToPsiNormSpline = {}
        self._volNormToPsiNormSpline = {}
    
    def __str__(self):
        """String representation of this instance.
        
        Returns:
            string (String): String describing this object.
        """
        return 'This is an abstract class. Please use machine-specific subclass.'
    
    ####################
    # Mapping routines #
    ####################
    
    def rho2rho(self, origin, destination, *args, **kwargs):
        """Convert from one coordinate to another.
        
        Args:
            origin (String): Indicates which coordinates the data are given in.
                Valid options are:
                
                    ======= ========================
                    RZ      R,Z coordinates
                    psinorm Normalized poloidal flux
                    phinorm Normalized toroidal flux
                    volnorm Normalized volume
                    Rmid    Midplane major radius
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            destination (String): Indicates which coordinates to convert to.
                Valid options are:
                
                    ======= ========================
                    psinorm Normalized poloidal flux
                    phinorm Normalized toroidal flux
                    volnorm Normalized volume
                    Rmid    Midplane major radius
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            rho (Array-like or scalar float): Values of the starting coordinate
                to map to the new coordinate. Will be two arguments `R`, `Z` if
                `origin` is 'RZ'.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `rho`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `rho` (or the meshgrid of `R`
                and `Z` if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of `rho`. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `rho` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `rho` or be
                a scalar. Default is True (evaluate ALL `rho` at EACH element in
                `t`).
            make_grid (Boolean): Only applicable if `origin` is 'RZ'. Set to
                True to pass `R` and `Z` through :py:func:`scipy.meshgrid`
                before evaluating. If this is set to True, `R` and `Z` must each
                only have a single dimension, but can have different lengths.
                Default is False (do not form meshgrid).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid when `destination` is Rmid. Default is False
                (return major radius, Rmid).            
            length_unit (String or 1): Length unit that quantities are
                given/returned in, as applicable. If a string is given, it must
                be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid/phinorm/volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Raises:
            ValueError: If `origin` is not one of the supported values.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.
            
            Find single psinorm value at r/a=0.6, t=0.26s::
            
                psi_val = Eq_instance.rho2rho('r/a', 'psinorm', 0.6, 0.26)
            
            Find psinorm values at r/a points 0.6 and 0.8 at the
            single time t=0.26s::
            
                psi_arr = Eq_instance.rho2rho('r/a', 'psinorm', [0.6, 0.8], 0.26)
            
            Find psinorm values at r/a of 0.6 at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.rho2rho('r/a', 'psinorm', 0.6, [0.2, 0.3])
            
            Find psinorm values at (r/a, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                psi_arr = Eq_instance.rho2rho('r/a', 'psinorm', [0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        
        if origin.startswith('sqrt'):
            args[0] == scipy.asarray(args[0])**2
            origin = origin[4:]
        
        if destination.startswith('sqrt'):
            kwargs['sqrt'] = True
            destination = destination[4:]
        
        if origin == 'RZ':
            return self.rz2rho(destination, *args, **kwargs)
        elif origin == 'Rmid':
            return self.rmid2rho(destination, *args, **kwargs)
        elif origin == 'r/a':
            return self.roa2rho(destination, *args, **kwargs)
        elif origin == 'psinorm':
            return self.psinorm2rho(destination, *args, **kwargs)
        elif origin == 'phinorm':
            return self.phinorm2rho(destination, *args, **kwargs)
        elif origin == 'volnorm':
            return self.volnorm2rho(destination, *args, **kwargs)
        else:
            raise ValueError("rho2rho: Unsupported origin coordinate method '%s'!" % origin)
    
    def rz2psi(self, R, Z, t, return_t=False, make_grid=False, each_t=True, length_unit=1):
        """Converts the passed R, Z, t arrays to psi (unnormalized poloidal flux) values.
        
        Args:
            R (Array-like or scalar float): Values of the radial coordinate to
                map to poloidal flux. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to poloidal flux. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            length_unit (String or 1): Length unit that `R`, `Z` are given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `psi` or (`psi`, `time_idxs`)
            
            * **psi** (`Array or scalar float`) - The unnormalized poloidal
              flux. If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned. If `R` and `Z`
              both have the same shape then `psi` has this shape as well,
              unless the `make_grid` keyword was True, in which case `psi` has
              shape (len(`Z`), len(`R`)).
            * **time_idxs** (Array with same shape as `psi`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psi value at R=0.6m, Z=0.0m, t=0.26s::
            
                psi_val = Eq_instance.rz2psi(0.6, 0, 0.26)

            Find psi values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the `Z` vector must be fully
            specified, even if the values are all the same::
            
                psi_arr = Eq_instance.rz2psi([0.6, 0.8], [0, 0], 0.26)

            Find psi values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.rz2psi(0.6, 0, [0.2, 0.3])

            Find psi values at (R, Z, t) points (0.6m, 0m, 0.2s) and
            (0.5m, 0.2m, 0.3s)::
            
                psi_arr = Eq_instance.rz2psi([0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find psi values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                psi_mat = Eq_instance.rz2psi(R, Z, 0.2, make_grid=True)
        """
        
        # Check inputs and process into flat arrays with units of meters:
        (R,
         Z,
         t,
         time_idxs,
         original_shape,
         single_val,
         single_time) = self._processRZt(R, Z, t,
                                         make_grid=make_grid,
                                         each_t=each_t,
                                         length_unit=length_unit)
 
        # Optimized form for single t value case:
        if not self._tricubic:
            if single_time:
                out_vals = self._getFluxBiSpline(time_idxs[0]).ev(Z, R)
            else:
                out_vals = scipy.zeros(t.shape)
                # Need to loop over time_idxs
                for k in xrange(0, len(t)):
                    out_vals[k] = self._getFluxBiSpline(time_idxs[k]).ev(Z[k], R[k])
        else:
            out_vals = self._getFluxTriSpline().ev(time_idxs,Z,R)

        # Correct for current sign:
        out_vals = -1 * out_vals * self.getCurrentSign()

        # Restore correct shape:
        out_vals = scipy.reshape(out_vals, original_shape)

        # Unwrap back into single value to match input form, if necessary:
        if single_val:
            out = out_vals[0]
        else:
            out = out_vals

        if return_t:
            # will reshape time_idxs only if it is utilized (otherwise set to None)
            if not self._tricubic:
                time_idxs = scipy.reshape(time_idxs, original_shape)
            else:
                #there is no easy way around this, this is a product of the time_idxs reliance
                time_idxs = scipy.reshape(t, original_shape)

            return (out, time_idxs)
        else:
            return out

    def rz2psinorm(self, R, Z, t, return_t=False, sqrt=False, make_grid=False,
                   each_t=True, length_unit=1):
        r"""Calculates the normalized poloidal flux at the given (R, Z, t).
        
        Uses the definition:
        
        .. math::
        
            \texttt{psi\_norm} = \frac{\psi - \psi(0)}{\psi(a) - \psi(0)}

        Args:
            R (Array-like or scalar float): Values of the radial coordinate to
                map to psinorm. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to psinorm. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of psinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            length_unit (String or 1): Length unit that `R`, `Z` are given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `psinorm` or (`psinorm`, `time_idxs`)
            
            * **psinorm** (`Array or scalar float`) - The normalized poloidal
              flux. If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned. If `R` and `Z`
              both have the same shape then `psinorm` has this shape as well,
              unless the `make_grid` keyword was True, in which case `psinorm`
              has shape (len(`Z`), len(`R`)).
            * **time_idxs** (Array with same shape as `psinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
       
        Examples:
            All assume that `Eq_instance` is a valid instance of the
            appropriate extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at R=0.6m, Z=0.0m, t=0.26s::
            
                psi_val = Eq_instance.rz2psinorm(0.6, 0, 0.26)

            Find psinorm values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the `Z` vector must be fully specified,
            even if the values are all the same::
            
                psi_arr = Eq_instance.rz2psinorm([0.6, 0.8], [0, 0], 0.26)

            Find psinorm values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::

                psi_arr = Eq_instance.rz2psinorm(0.6, 0, [0.2, 0.3])

            Find psinorm values at (R, Z, t) points (0.6m, 0m, 0.2s) and (0.5m, 0.2m, 0.3s)::
            
                psi_arr = Eq_instance.rz2psinorm([0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find psinorm values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                psi_mat = Eq_instance.rz2psinorm(R, Z, 0.2, make_grid=True)
        """
        psi, time_idxs = self.rz2psi(R, Z, t, return_t=True,
                                     make_grid=make_grid,
                                     each_t=each_t,
                                     length_unit=length_unit)
       
        if not self._tricubic:
            psi_boundary = self.getFluxLCFS()[time_idxs]
            psi_0 = self.getFluxAxis()[time_idxs]
        else:
            # use 1d spline to generate the psi at the core and at boundary.
            #psi = psi.squeeze(psi)
            psi_boundary = scipy.array(self._getLCFSPsiSpline()(time_idxs)).reshape(time_idxs.shape)
            psi_0 = scipy.array(self._getPsi0Spline()(time_idxs)).reshape(time_idxs.shape)

        psi_norm = (psi - psi_0) / (psi_boundary - psi_0)
       
        if sqrt:
            scipy.place(psi_norm, psi_norm < 0, 0)
            out = scipy.sqrt(psi_norm)
        else:
            out = psi_norm
        
        # Unwrap single values to ensure least surprise:
        try:
            iter(psi)
        except TypeError:
            out = out[0]
            time_idxs = time_idxs[0]

        if return_t:
            return (out, time_idxs)
        else:
            return out

    def rz2phinorm(self, *args, **kwargs):
        r"""Calculates the normalized toroidal flux.
        
        Uses the definitions:
        
        .. math::
        
            \texttt{phi} &= \int q(\psi)\,d\psi
            
            \texttt{phi\_norm} &= \frac{\phi}{\phi(a)}
            
        This is based on the IDL version efit_rz2rho.pro by Steve Wolfe.
        
        Args:
            R (Array-like or scalar float): Values of the radial coordinate to
                map to phinorm. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to phinorm. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of phinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            length_unit (String or 1): Length unit that `R`, `Z` are given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `phinorm` or (`phinorm`, `time_idxs`)
            
            * **phinorm** (`Array or scalar float`) - The normalized toroidal
              flux. If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned. If `R` and `Z`
              both have the same shape then `phinorm` has this shape as well,
              unless the `make_grid` keyword was True, in which case `phinorm`
              has shape (len(`Z`), len(`R`)).
            * **time_idxs** (Array with same shape as `phinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.

        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single phinorm value at R=0.6m, Z=0.0m, t=0.26s::
            
                phi_val = Eq_instance.rz2phinorm(0.6, 0, 0.26)
        
            Find phinorm values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the `Z` vector must be fully specified,
            even if the values are all the same::
            
                phi_arr = Eq_instance.rz2phinorm([0.6, 0.8], [0, 0], 0.26)

            Find phinorm values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::
            
                phi_arr = Eq_instance.rz2phinorm(0.6, 0, [0.2, 0.3])

            Find phinorm values at (R, Z, t) points (0.6m, 0m, 0.2s) and (0.5m, 0.2m, 0.3s)::
            
                phi_arr = Eq_instance.rz2phinorm([0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find phinorm values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                phi_mat = Eq_instance.rz2phinorm(R, Z, 0.2, make_grid=True)
        """
        return self._RZ2Quan(self._getPhiNormSpline, *args, **kwargs)

    def rz2volnorm(self, *args, **kwargs):
        """Calculates the normalized flux surface volume.
        
        Based on the IDL version efit_rz2rho.pro by Steve Wolfe.
        
        Args:
            R (Array-like or scalar float): Values of the radial coordinate to
                map to volnorm. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to volnorm. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of volnorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            length_unit (String or 1): Length unit that `R`, `Z` are given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `volnorm` or (`volnorm`, `time_idxs`)
            
            * **volnorm** (`Array or scalar float`) - The normalized volume.
              If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned. If `R` and `Z`
              both have the same shape then `volnorm` has this shape as well,
              unless the `make_grid` keyword was True, in which case `volnorm`
              has shape (len(`Z`), len(`R`)).
            * **time_idxs** (Array with same shape as `volnorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single volnorm value at R=0.6m, Z=0.0m, t=0.26s::
            
                psi_val = Eq_instance.rz2volnorm(0.6, 0, 0.26)

            Find volnorm values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the `Z` vector must be fully specified,
            even if the values are all the same::
            
                vol_arr = Eq_instance.rz2volnorm([0.6, 0.8], [0, 0], 0.26)

            Find volnorm values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::
            
                vol_arr = Eq_instance.rz2volnorm(0.6, 0, [0.2, 0.3])

            Find volnorm values at (R, Z, t) points (0.6m, 0m, 0.2s) and (0.5m, 0.2m, 0.3s)::
            
                vol_arr = Eq_instance.rz2volnorm([0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find volnorm values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                vol_mat = Eq_instance.rz2volnorm(R, Z, 0.2, make_grid=True)
        """

        return self._RZ2Quan(self._getVolNormSpline, *args, **kwargs)

    def rz2rmid(self, *args, **kwargs):
        """Maps the given points to the outboard midplane major radius, Rmid.
        
        Based on the IDL version efit_rz2rmid.pro by Steve Wolfe.
        
        Args:
            R (Array-like or scalar float): Values of the radial coordinate to
                map to Rmid. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to Rmid. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of Rmid. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).            
            length_unit (String or 1): Length unit that `R`, `Z` are given in,
                AND that `Rmid` is returned in. If a string is given, it must
                be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `Rmid` or (`Rmid`, `time_idxs`)
            
            * **Rmid** (`Array or scalar float`) - The outboard midplan major
              radius. If all of the input arguments are scalar, then a scalar
              is returned. Otherwise, a scipy Array is returned. If `R` and `Z`
              both have the same shape then `Rmid` has this shape as well,
              unless the `make_grid` keyword was True, in which case `Rmid`
              has shape (len(`Z`), len(`R`)).
            * **time_idxs** (Array with same shape as `Rmid`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single Rmid value at R=0.6m, Z=0.0m, t=0.26s::
            
                R_mid_val = Eq_instance.rz2rmid(0.6, 0, 0.26)

            Find R_mid values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the `Z` vector must be fully specified,
            even if the values are all the same::
            
                R_mid_arr = Eq_instance.rz2rmid([0.6, 0.8], [0, 0], 0.26)

            Find Rmid values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::
            
                R_mid_arr = Eq_instance.rz2rmid(0.6, 0, [0.2, 0.3])

            Find Rmid values at (R, Z, t) points (0.6m, 0m, 0.2s) and (0.5m, 0.2m, 0.3s)::
            
                R_mid_arr = Eq_instance.rz2rmid([0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find Rmid values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                R_mid_mat = Eq_instance.rz2rmid(R, Z, 0.2, make_grid=True)
        """
        
        # Steve Wolfe's version has an extra (linear) interpolation step for
        # small psi_norm. Should check to see if we need this still with the
        # scipy spline. So far looks fine...
        
        # Convert units from meters to desired target but keep units consistent
        # with rho keyword:
        if kwargs.get('rho', False):
            unit_factor = 1
        else:
            unit_factor = self._getLengthConversionFactor('m', kwargs.get('length_unit', 1))
        
        return unit_factor * self._RZ2Quan(self._getRmidSpline, *args, **kwargs)
    
    def rz2roa(self, *args, **kwargs):
        """Maps the given points to the normalized minor radius, r/a.
        
        Based on the IDL version efit_rz2rmid.pro by Steve Wolfe.
       
        Args:
            R (Array-like or scalar float): Values of the radial coordinate to
                map to r/a. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to r/a. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of r/a. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            length_unit (String or 1): Length unit that `R`, `Z` are given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `roa` or (`roa`, `time_idxs`)
            
            * **roa** (`Array or scalar float`) - The normalized minor radius.
              If all of the input arguments are scalar, then a scalar
              is returned. Otherwise, a scipy Array is returned. If `R` and `Z`
              both have the same shape then `roa` has this shape as well,
              unless the `make_grid` keyword was True, in which case `roa`
              has shape (len(`Z`), len(`R`)).
            * **time_idxs** (Array with same shape as `roa`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single r/a value at R=0.6m, Z=0.0m, t=0.26s::
            
                roa_val = Eq_instance.rz2roa(0.6, 0, 0.26)

            Find r/a values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the Z vector must be fully specified,
            even if the values are all the same::
            
                roa_arr = Eq_instance.rz2roa([0.6, 0.8], [0, 0], 0.26)

            Find r/a values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::
            
                roa_arr = Eq_instance.rz2roa(0.6, 0, [0.2, 0.3])

            Find r/a values at (R, Z, t) points (0.6m, 0m, 0.2s) and (0.5m, 0.2m, 0.3s)::
            
                roa_arr = Eq_instance.rz2roa([0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find r/a values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                roa_mat = Eq_instance.rz2roa(R, Z, 0.2, make_grid=True)
        """
        
        # Steve Wolfe's version has an extra (linear) interpolation step for
        # small psi_norm. Should check to see if we need this still with the
        # scipy spline. So far looks fine...
        kwargs['rho'] = True
        return self._RZ2Quan(self._getRmidSpline, *args, **kwargs)
    
    def rz2rho(self, method, *args, **kwargs):
        """Convert the passed (R, Z, t) coordinates into one of several coordinates.
        
        Args:
            method (String): Indicates which coordinates to convert to. Valid
                options are:
                
                    ======= ========================
                    psinorm Normalized poloidal flux
                    phinorm Normalized toroidal flux
                    volnorm Normalized volume
                    Rmid    Midplane major radius
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            R (Array-like or scalar float): Values of the radial coordinate to
                map to `rho`. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `Z` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `R` must
                have exactly one dimension.
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to `rho`. If `R` and `Z` are both scalar values,
                they are used as the coordinate pair for all of the values in
                `t`. Must have the same shape as `R` unless the `make_grid`
                keyword is set. If the `make_grid` keyword is True, `Z` must
                have exactly one dimension.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If the `each_t` keyword is True, then `t` must be
                scalar or have exactly one dimension. If the `each_t` keyword is
                False, `t` must have the same shape as `R` and `Z` (or their
                meshgrid if `make_grid` is True).
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of `rho`. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R`, `Z` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R` and
                `Z` or be a scalar. Default is True (evaluate ALL `R`, `Z` at
                EACH element in `t`).
            make_grid (Boolean): Set to True to pass `R` and `Z` through
                :py:func:`scipy.meshgrid` before evaluating. If this is set to
                True, `R` and `Z` must each only have a single dimension, but
                can have different lengths. Default is False (do not form
                meshgrid).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid when `destination` is Rmid. Default is False
                (return major radius, Rmid).            
            length_unit (String or 1): Length unit that `R`, `Z` are given in,
                AND that `Rmid` is returned in. If a string is given, it must
                be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid/phinorm/volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Raises:
            ValueError: If `method` is not one of the supported values.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at R=0.6m, Z=0.0m, t=0.26s::
            
                psi_val = Eq_instance.rz2rho('psinorm', 0.6, 0, 0.26)

            Find psinorm values at (R, Z) points (0.6m, 0m) and (0.8m, 0m) at the
            single time t=0.26s. Note that the `Z` vector must be fully specified,
            even if the values are all the same::
            
                psi_arr = Eq_instance.rz2rho('psinorm', [0.6, 0.8], [0, 0], 0.26)

            Find psinorm values at (R, Z) points (0.6m, 0m) at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.rz2rho('psinorm', 0.6, 0, [0.2, 0.3])

            Find psinorm values at (R, Z, t) points (0.6m, 0m, 0.2s) and (0.5m, 0.2m, 0.3s)::
            
                psi_arr = Eq_instance.rz2rho('psinorm', [0.6, 0.5], [0, 0.2], [0.2, 0.3], each_t=False)

            Find psinorm values on grid defined by 1D vector of radial positions `R`
            and 1D vector of vertical positions `Z` at time t=0.2s::
            
                psi_mat = Eq_instance.rz2rho('psinorm', R, Z, 0.2, make_grid=True)
        """
        
        if method.startswith('sqrt'):
            kwargs['sqrt'] = True
            method = method[4:]
        
        if method == 'psinorm':
            return self.rz2psinorm(*args, **kwargs)
        elif method == 'phinorm':
            return self.rz2phinorm(*args, **kwargs)
        elif method == 'volnorm':
            return self.rz2volnorm(*args, **kwargs)
        elif method == 'Rmid':
            return self.rz2rmid(*args, **kwargs)
        elif method == 'r/a':
            kwargs['rho'] = True
            return self.rz2rmid(*args, **kwargs)
        else:
            raise ValueError("rz2rho: Unsupported normalized coordinate method '%s'!" % method)
    
    def rmid2roa(self, R_mid, t, each_t=True, return_t=False, sqrt=False, time_idxs=None, length_unit=1):
        """Convert the passed (R_mid, t) coordinates into r/a.
        
        Args:
            R_mid (Array-like or scalar float): Values of the outboard midplane
                major radius to map to r/a.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R_mid`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `R_mid`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of r/a. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R_mid` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R_mid`
                or be a scalar. Default is True (evaluate ALL `R_mid` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `R_mid` is given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `roa` or (`roa`, `time_idxs`)
        
            * **roa** (`Array or scalar float`) - Normalized midplane minor
              radius. If all of the input arguments are scalar, then a scalar
              is returned. Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `roa`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single r/a value at R_mid=0.6m, t=0.26s::
            
                roa_val = Eq_instance.rmid2roa(0.6, 0.26)

            Find roa values at R_mid points 0.6m and 0.8m at the
            single time t=0.26s.::
            
                roa_arr = Eq_instance.rmid2roa([0.6, 0.8], 0.26)

            Find roa values at R_mid of 0.6m at times t=[0.2s, 0.3s]::
            
                roa_arr = Eq_instance.rmid2roa(0.6, [0.2, 0.3])

            Find r/a values at (R_mid, t) points (0.6m, 0.2s) and (0.5m, 0.3s)::
            
                roa_arr = Eq_instance.rmid2roa([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        if time_idxs is None:
            (R_mid,
             dum,
             t,
             time_idxs,
             original_shape,
             single_val,
             single_time) = self._processRZt(R_mid, R_mid, t,
                                             each_t=each_t, make_grid=False,
                                             length_unit=length_unit,
                                             convert_only=True)
        else:
            single_val = True
            try:
                iter(R_mid)
            except TypeError:
                R_mid = scipy.asarray([R_mid], dtype=float)
            else:
                single_val = False
                R_mid = scipy.asarray(R_mid, dtype=float)
            
            original_shape = R_mid.shape
            R_mid = scipy.reshape(R_mid, -1)
            time_idxs = scipy.reshape(time_idxs, -1)
            
        roa = self._rmid2roa(R_mid, time_idxs)
        
        # Restore original shape:
        roa = scipy.reshape(roa, original_shape)
 
        if sqrt:
            scipy.place(roa, roa < 0, 0.0)
            out = scipy.sqrt(roa)
        else:
            out = roa

        if single_val:
            out = out[0]
            time_idxs = time_idxs[0]
 
        if return_t:
            return (out, time_idxs)
        else:
            return out
    
    def rmid2psinorm(self, R_mid, t, **kwargs):
        """Calculates the normalized poloidal flux corresponding to the passed R_mid (mapped outboard midplane major radius) values.

        Args:
            R_mid (Array-like or scalar float): Values of the outboard midplane
                major radius to map to psinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R_mid`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `R_mid`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of psinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R_mid` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R_mid`
                or be a scalar. Default is True (evaluate ALL `R_mid` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `R_mid` is given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `psinorm` or (`psinorm`, `time_idxs`)
        
            * **psinorm** (`Array or scalar float`) - Normalized poloidal flux.
              If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `psinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value for Rmid=0.7m, t=0.26s::
        
                psinorm_val = Eq_instance.rmid2psinorm(0.7, 0.26)
            
            Find psinorm values at R_mid values of 0.5m and 0.7m at the single time
            t=0.26s::
        
                psinorm_arr = Eq_instance.rmid2psinorm([0.5, 0.7], 0.26)

            Find psinorm values at R_mid=0.5m at times t=[0.2s, 0.3s]::
        
                psinorm_arr = Eq_instance.rmid2psinorm(0.5, [0.2, 0.3])

            Find psinorm values at (R_mid, t) points (0.6m, 0.2s) and (0.5m, 0.3s)::
        
                psinorm_arr = Eq_instance.rmid2psinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._psinorm2Quan(self._getRmidToPsiNormSpline, R_mid, t, check_space=True, **kwargs)
    
    def rmid2phinorm(self, *args, **kwargs):
        r"""Calculates the normalized toroidal flux.
        
        Uses the definitions:
        
        .. math::
        
            \texttt{phi} &= \int q(\psi)\,d\psi
            
            \texttt{phi\_norm} &= \frac{\phi}{\phi(a)}
            
        This is based on the IDL version efit_rz2rho.pro by Steve Wolfe.
        
        Args:
            R_mid (Array-like or scalar float): Values of the outboard midplane
                major radius to map to phinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R_mid`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `R_mid`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of phinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R_mid` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R_mid`
                or be a scalar. Default is True (evaluate ALL `R_mid` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `R_mid` is given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `phinorm` or (`phinorm`, `time_idxs`)
        
            * **phinorm** (`Array or scalar float`) - Normalized toroidal flux.
              If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `phinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single phinorm value at R_mid=0.6m, t=0.26s::
            
                phi_val = Eq_instance.rmid2phinorm(0.6, 0.26)
        
            Find phinorm values at R_mid points 0.6m and 0.8m at the single time
            t=0.26s::
            
                phi_arr = Eq_instance.rmid2phinorm([0.6, 0.8], 0.26)

            Find phinorm values at R_mid point 0.6m at times t=[0.2s, 0.3s]::
            
                phi_arr = Eq_instance.rmid2phinorm(0.6, [0.2, 0.3])

            Find phinorm values at (R, t) points (0.6m, 0.2s) and (0.5m, 0.3s)::
            
                phi_arr = Eq_instance.rmid2phinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._Rmid2Quan(self._getPhiNormSpline, *args, **kwargs)
    
    def rmid2volnorm(self, *args, **kwargs):
        """Calculates the normalized flux surface volume.
        
        Based on the IDL version efit_rz2rho.pro by Steve Wolfe.
        
        Args:
            R_mid (Array-like or scalar float): Values of the outboard midplane
                major radius to map to volnorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R_mid`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `R_mid`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of volnorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R_mid` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R_mid`
                or be a scalar. Default is True (evaluate ALL `R_mid` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `R_mid` is given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `volnorm` or (`volnorm`, `time_idxs`)
        
            * **volnorm** (`Array or scalar float`) - Normalized volume.
              If all of the input arguments are scalar, then a scalar is
              returned. Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `volnorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single volnorm value at R_mid=0.6m, t=0.26s::
            
                vol_val = Eq_instance.rmid2volnorm(0.6, 0.26)

            Find volnorm values at R_mid points 0.6m and 0.8m at the single time
            t=0.26s::
            
                vol_arr = Eq_instance.rmid2volnorm([0.6, 0.8], 0.26)

            Find volnorm values at R_mid points 0.6m at times t=[0.2s, 0.3s]::
            
                vol_arr = Eq_instance.rmid2volnorm(0.6, [0.2, 0.3])

            Find volnorm values at (R_mid, t) points (0.6m, 0.2s) and (0.5m, 0.3s)::
            
                vol_arr = Eq_instance.rmid2volnorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """

        return self._Rmid2Quan(self._getVolNormSpline, *args, **kwargs)
    
    def rmid2rho(self, method, R_mid, t, **kwargs):
        """Convert the passed (R_mid, t) coordinates into one of several coordinates.
        
        Args:
            method (String): Indicates which coordinates to convert to. Valid
                options are:
                
                    ======= ========================
                    psinorm Normalized poloidal flux
                    phinorm Normalized toroidal flux
                    volnorm Normalized volume
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            R_mid (Array-like or scalar float): Values of the outboard midplane
                major radius to map to rho.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `R_mid`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `R_mid`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of rho. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `R_mid` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `R_mid`
                or be a scalar. Default is True (evaluate ALL `R_mid` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `R_mid` is given in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to volnorm or phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at R_mid=0.6m, t=0.26s::
            
                psi_val = Eq_instance.rmid2rho('psinorm', 0.6, 0.26)

            Find psinorm values at R_mid points 0.6m and 0.8m at the
            single time t=0.26s.::
            
                psi_arr = Eq_instance.rmid2rho('psinorm', [0.6, 0.8], 0.26)

            Find psinorm values at R_mid of 0.6m at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.rmid2rho('psinorm', 0.6, [0.2, 0.3])

            Find psinorm values at (R_mid, t) points (0.6m, 0.2s) and (0.5m, 0.3s)::
            
                psi_arr = Eq_instance.rmid2rho('psinorm', [0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        if method.startswith('sqrt'):
            kwargs['sqrt'] = True
            method = method[4:]
        
        if method == 'psinorm':
            return self.rmid2psinorm(R_mid, t, **kwargs)
        elif method == 'r/a':
            return self.rmid2roa(R_mid, t, **kwargs)
        elif method == 'phinorm':
            return self.rmid2phinorm(R_mid, t, **kwargs)
        elif method == 'volnorm':
            return self.rmid2volnorm(R_mid, t, **kwargs)
        else:
            # Default back to the old kuldge that wastes time in rz2psi:
            # TODO: This doesn't handle length units properly!
            Z_mid = self.getMagZSpline()(t)
            
            if kwargs.get('each_t', True):
                # Need to override the default in _processRZt, since we are doing
                # the shaping here:
                kwargs['each_t'] = False
                try:
                    iter(t)
                except TypeError:
                    # For a single t, there will only be a single value of Z_mid and
                    # we only need to make it have the same shape as R_mid. Note
                    # that ones_like appears to be clever enough to handle the case
                    # of a scalar R_mid.
                    Z_mid = Z_mid * scipy.ones_like(R_mid)
                else:
                    # For multiple t, we need to repeat R_mid for every t, then
                    # repeat the corresponding Z_mid that many times for each such
                    # entry.
                    t = scipy.asarray(t)
                    if t.ndim != 1:
                        raise ValueError("rmid2rho: When using the each_t keyword, "
                                         "t must have only one dimension.")
                    R_mid = scipy.tile(
                        R_mid,
                        scipy.concatenate(([len(t),], scipy.ones_like(scipy.shape(R_mid))))
                    )
                    # TODO: Is there a clever way to do this without a loop?
                    Z_mid_temp = scipy.ones_like(R_mid)
                    t_temp = scipy.ones_like(R_mid)
                    for k in xrange(0, len(Z_mid)):
                        Z_mid_temp[k] *= Z_mid[k]
                        t_temp[k] *= t[k]
                    Z_mid = Z_mid_temp
                    t = t_temp
                    
            return self.rz2rho(method, R_mid, Z_mid, t, **kwargs)
    
    def roa2rmid(self, roa, t, each_t=True, return_t=False, time_idxs=None, length_unit=1):
        """Convert the passed (r/a, t) coordinates into Rmid.
        
        Args:
            roa (Array-like or scalar float): Values of the normalized minor
                radius to map to Rmid.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `roa`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `roa`.
        
        Keyword Args:
            each_t (Boolean): When True, the elements in `roa` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `roa`
                or be a scalar. Default is True (evaluate ALL `roa` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).            
        
        Returns:
            `Rmid` or (`Rmid`, `time_idxs`)
        
            * **Rmid** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `Rmid`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single R_mid value at r/a=0.6, t=0.26s::
            
                R_mid_val = Eq_instance.roa2rmid(0.6, 0.26)

            Find R_mid values at r/a points 0.6 and 0.8 at the
            single time t=0.26s.::
            
                R_mid_arr = Eq_instance.roa2rmid([0.6, 0.8], 0.26)

            Find R_mid values at r/a of 0.6 at times t=[0.2s, 0.3s]::
            
                R_mid_arr = Eq_instance.roa2rmid(0.6, [0.2, 0.3])

            Find R_mid values at (roa, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                R_mid_arr = Eq_instance.roa2rmid([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        if time_idxs is None:
            (roa,
             dum,
             t,
             time_idxs,
             original_shape,
             single_val,
             single_time) = self._processRZt(roa, roa, t,
                                             each_t=each_t, make_grid=False,
                                             check_space=False)
        else:
            single_val = True
            try:
                iter(roa)
            except TypeError:
                roa = scipy.asarray([roa], dtype=float)
            else:
                single_val = False
                roa = scipy.asarray(roa, dtype=float)
            
            original_shape = roa.shape
            roa = scipy.reshape(roa, -1)
            time_idxs = scipy.reshape(time_idxs, -1)
            
        R_mid = self._roa2rmid(roa, time_idxs)
        
        # Restore original shape:
        R_mid = scipy.reshape(R_mid, original_shape)
 
        out = roa

        if single_val:
            out = out[0]
            time_idxs = time_idxs[0]
        
        out *= self._getLengthConversionFactor('m', length_unit)
        
        if return_t:
            return (out, time_idxs)
        else:
            return out
    
    def roa2psinorm(self, *args, **kwargs):
        """Convert the passed (r/a, t) coordinates into psinorm.
        
        Args:
            roa (Array-like or scalar float): Values of the normalized minor
                radius to map to psinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `roa`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `roa`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of psinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `roa` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `roa`
                or be a scalar. Default is True (evaluate ALL `roa` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to volnorm or phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
                
        Returns:
            `psinorm` or (`psinorm`, `time_idxs`)
        
            * **psinorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `psinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at r/a=0.6, t=0.26s::
            
                psinorm_val = Eq_instance.roa2psinorm(0.6, 0.26)

            Find psinorm values at r/a points 0.6 and 0.8 at the
            single time t=0.26s.::
            
                psinorm_arr = Eq_instance.roa2psinorm([0.6, 0.8], 0.26)

            Find psinorm values at r/a of 0.6 at times t=[0.2s, 0.3s]::
            
                psinorm_arr = Eq_instance.roa2psinorm(0.6, [0.2, 0.3])

            Find psinorm values at (roa, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                psinorm_arr = Eq_instance.roa2psinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self.roa2rho('psinorm', *args, **kwargs)
    
    def roa2phinorm(self, *args, **kwargs):
        """Convert the passed (r/a, t) coordinates into phinorm.
        
        Args:
            roa (Array-like or scalar float): Values of the normalized minor
                radius to map to phinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `roa`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `roa`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of phinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `roa` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `roa`
                or be a scalar. Default is True (evaluate ALL `roa` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to volnorm or phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
                
        Returns:
            `phinorm` or (`phinorm`, `time_idxs`)
        
            * **phinorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `phinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single phinorm value at r/a=0.6, t=0.26s::
            
                phinorm_val = Eq_instance.roa2phinorm(0.6, 0.26)

            Find phinorm values at r/a points 0.6 and 0.8 at the
            single time t=0.26s.::
            
                phinorm_arr = Eq_instance.roa2phinorm([0.6, 0.8], 0.26)

            Find phinorm values at r/a of 0.6 at times t=[0.2s, 0.3s]::
            
                phinorm_arr = Eq_instance.roa2phinorm(0.6, [0.2, 0.3])

            Find phinorm values at (roa, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                phinorm_arr = Eq_instance.roa2phinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self.roa2rho('phinorm', *args, **kwargs)
    
    def roa2volnorm(self, *args, **kwargs):
        """Convert the passed (r/a, t) coordinates into volnorm.
        
        Args:
            roa (Array-like or scalar float): Values of the normalized minor
                radius to map to volnorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `roa`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `roa`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of volnorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `roa` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `roa`
                or be a scalar. Default is True (evaluate ALL `roa` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to volnorm or phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
                
        Returns:
            `volnorm` or (`volnorm`, `time_idxs`)
        
            * **volnorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `volnorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single volnorm value at r/a=0.6, t=0.26s::
            
                volnorm_val = Eq_instance.roa2volnorm(0.6, 0.26)

            Find volnorm values at r/a points 0.6 and 0.8 at the
            single time t=0.26s.::
            
                volnorm_arr = Eq_instance.roa2volnorm([0.6, 0.8], 0.26)

            Find volnorm values at r/a of 0.6 at times t=[0.2s, 0.3s]::
            
                volnorm_arr = Eq_instance.roa2volnorm(0.6, [0.2, 0.3])

            Find volnorm values at (roa, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                volnorm_arr = Eq_instance.roa2volnorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self.roa2rho('volnorm', *args, **kwargs)
    
    def roa2rho(self, method, *args, **kwargs):
        """Convert the passed (r/a, t) coordinates into one of several coordinates.
        
        Args:
            method (String): Indicates which coordinates to convert to.
                Valid options are:
                
                    ======= ========================
                    psinorm Normalized poloidal flux
                    phinorm Normalized toroidal flux
                    volnorm Normalized volume
                    Rmid    Midplane major radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            roa (Array-like or scalar float): Values of the normalized minor
                radius to map to rho.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `roa`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `roa`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of rho. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `roa` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `roa`
                or be a scalar. Default is True (evaluate ALL `roa` at EACH
                element in `t`).
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from Rmid to
                psinorm and psinorm to volnorm or phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at r/a=0.6, t=0.26s::
            
                psi_val = Eq_instance.roa2rho('psinorm', 0.6, 0.26)

            Find psinorm values at r/a points 0.6 and 0.8 at the
            single time t=0.26s::
            
                psi_arr = Eq_instance.roa2rho('psinorm', [0.6, 0.8], 0.26)

            Find psinorm values at r/a of 0.6 at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.roa2rho('psinorm', 0.6, [0.2, 0.3])

            Find psinorm values at (r/a, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                psi_arr = Eq_instance.roa2rho('psinorm', [0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        if method == 'Rmid':
            return self.roa2rmid(*args, **kwargs)
        else:
            return_t = kwargs.get('return_t', False)
            kwargs['return_t'] = True
        
            # Not used by roa2rmid:
            kind = kwargs.pop('kind', 'cubic')
            sqrt = kwargs.pop('sqrt', False)

            R_mid, time_idxs = self.roa2rmid(*args, **kwargs)
        
            kwargs['return_t'] = return_t
            kwargs['kind'] = kind
            kwargs['sqrt'] = sqrt
            kwargs['time_idxs'] = time_idxs
            # TODO: This technically computes the time indices twice. Is there are
            # good compromise to get the best of both worlds (nice calling of
            # _psinorm2Quan AND no recompute)?
            return self.rmid2rho(method, *args, **kwargs)
    
    def psinorm2rmid(self, psi_norm, t, **kwargs):
        """Calculates the outboard R_mid location corresponding to the passed psinorm (normalized poloidal flux) values.
        
        Args:
            psi_norm (Array-like or scalar float): Values of the normalized
                poloidal flux to map to Rmid.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `psi_norm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `psi_norm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of Rmid. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `psi_norm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `psi_norm` or be
                a scalar. Default is True (evaluate ALL `psi_norm` at EACH element in
                `t`).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).            
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `Rmid` or (`Rmid`, `time_idxs`)
        
            * **Rmid** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `Rmid`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single R_mid value for psinorm=0.7, t=0.26s::
            
                R_mid_val = Eq_instance.psinorm2rmid(0.7, 0.26)

            Find R_mid values at psi_norm values of 0.5 and 0.7 at the single time
            t=0.26s::
            
                R_mid_arr = Eq_instance.psinorm2rmid([0.5, 0.7], 0.26)

            Find R_mid values at psi_norm=0.5 at times t=[0.2s, 0.3s]::
            
                R_mid_arr = Eq_instance.psinorm2rmid(0.5, [0.2, 0.3])

            Find R_mid values at (psinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                R_mid_arr = Eq_instance.psinorm2rmid([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        # Convert units from meters to desired target but keep units consistent
        # with rho keyword:
        if kwargs.get('rho', False):
            unit_factor = 1
        else:
            unit_factor = self._getLengthConversionFactor('m', kwargs.get('length_unit', 1))
        
        return unit_factor * self._psinorm2Quan(self._getRmidSpline,
                                                psi_norm,
                                                t,
                                                **kwargs)

    def psinorm2roa(self, psi_norm, t, **kwargs):
        """Calculates the normalized minor radius location corresponding to the passed psi_norm (normalized poloidal flux) values.
        
        Args:
            psi_norm (Array-like or scalar float): Values of the normalized
                poloidal flux to map to r/a.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `psi_norm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `psi_norm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of r/a. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `psi_norm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `psi_norm` or be
                a scalar. Default is True (evaluate ALL `psi_norm` at EACH element in
                `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `roa` or (`roa`, `time_idxs`)
        
            * **roa** (`Array or scalar float`) - Normalized midplane minor
              radius. If all of the input arguments are scalar, then a scalar
              is returned. Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `roa`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single r/a value for psinorm=0.7, t=0.26s::
            
                roa_val = Eq_instance.psinorm2roa(0.7, 0.26)

            Find r/a values at psi_norm values of 0.5 and 0.7 at the single time
            t=0.26s::
            
                roa_arr = Eq_instance.psinorm2roa([0.5, 0.7], 0.26)

            Find r/a values at psi_norm=0.5 at times t=[0.2s, 0.3s]::
            
                roa_arr = Eq_instance.psinorm2roa(0.5, [0.2, 0.3])

            Find r/a values at (psinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                roa_arr = Eq_instance.psinorm2roa([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        kwargs['rho'] = True
        return self._psinorm2Quan(self._getRmidSpline,
                                  psi_norm,
                                  t,
                                  **kwargs)

    def psinorm2volnorm(self, psi_norm, t, **kwargs):
        """Calculates the normalized volume corresponding to the passed psi_norm (normalized poloidal flux) values.

        Args:
            psi_norm (Array-like or scalar float): Values of the normalized
                poloidal flux to map to volnorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `psi_norm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `psi_norm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of volnorm. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `psi_norm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `psi_norm` or be
                a scalar. Default is True (evaluate ALL `psi_norm` at EACH element in
                `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `volnorm` or (`volnorm`, `time_idxs`)
        
            * **volnorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `volnorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single volnorm value for psinorm=0.7, t=0.26s::
            
                volnorm_val = Eq_instance.psinorm2volnorm(0.7, 0.26)

            Find volnorm values at psi_norm values of 0.5 and 0.7 at the single time
            t=0.26s::
            
                volnorm_arr = Eq_instance.psinorm2volnorm([0.5, 0.7], 0.26)

            Find volnorm values at psi_norm=0.5 at times t=[0.2s, 0.3s]::
            
                volnorm_arr = Eq_instance.psinorm2volnorm(0.5, [0.2, 0.3])

            Find volnorm values at (psinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                volnorm_arr = Eq_instance.psinorm2volnorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._psinorm2Quan(self._getVolNormSpline, psi_norm, t, **kwargs)

    def psinorm2phinorm(self, psi_norm, t, **kwargs):
        """Calculates the normalized toroidal flux corresponding to the passed psi_norm (normalized poloidal flux) values.

        Args:
            psi_norm (Array-like or scalar float): Values of the normalized
                poloidal flux to map to phinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `psi_norm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `psi_norm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of phinorm. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `psi_norm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `psi_norm` or be
                a scalar. Default is True (evaluate ALL `psi_norm` at EACH element in
                `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `phinorm` or (`phinorm`, `time_idxs`)
        
            * **phinorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `phinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single phinorm value for psinorm=0.7, t=0.26s::
            
                phinorm_val = Eq_instance.psinorm2phinorm(0.7, 0.26)
                
            Find phinorm values at psi_norm values of 0.5 and 0.7 at the single time
            t=0.26s::
            
                phinorm_arr = Eq_instance.psinorm2phinorm([0.5, 0.7], 0.26)

            Find phinorm values at psi_norm=0.5 at times t=[0.2s, 0.3s]::
            
                phinorm_arr = Eq_instance.psinorm2phinorm(0.5, [0.2, 0.3])

            Find phinorm values at (psinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
            
                phinorm_arr = Eq_instance.psinorm2phinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._psinorm2Quan(self._getPhiNormSpline, psi_norm, t, **kwargs)

    def psinorm2rho(self, method, *args, **kwargs):
        """Convert the passed (psinorm, t) coordinates into one of several coordinates.
        
        Args:
            method (String): Indicates which coordinates to convert to.
                Valid options are:
                
                    ======= ========================
                    phinorm Normalized toroidal flux
                    volnorm Normalized volume
                    Rmid    Midplane major radius
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            psi_norm (Array-like or scalar float): Values of the normalized
                poloidal flux to map to rho.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `psi_norm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `psi_norm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of rho. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `psi_norm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `psi_norm` or be
                a scalar. Default is True (evaluate ALL `psi_norm` at EACH element in
                `t`).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).            
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid/phinorm/volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Raises:
            ValueError: If `method` is not one of the supported values.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single phinorm value at psinorm=0.6, t=0.26s::
            
                phi_val = Eq_instance.psinorm2rho('phinorm', 0.6, 0.26)

            Find phinorm values at phinorm of 0.6 and 0.8 at the
            single time t=0.26s::
            
                phi_arr = Eq_instance.psinorm2rho('phinorm', [0.6, 0.8], 0.26)

            Find phinorm values at psinorm of 0.6 at times t=[0.2s, 0.3s]::
            
                phi_arr = Eq_instance.psinorm2rho('phinorm', 0.6, [0.2, 0.3])

            Find phinorm values at (psinorm, t) points (0.6, 0.2s) and (0.5m, 0.3s)::
            
                phi_arr = Eq_instance.psinorm2rho('phinorm', [0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        
        if method.startswith('sqrt'):
            kwargs['sqrt'] = True
            method = method[4:]
        
        if method == 'phinorm':
            return self.psinorm2phinorm(*args, **kwargs)
        elif method == 'volnorm':
            return self.psinorm2volnorm(*args, **kwargs)
        elif method == 'Rmid':
            return self.psinorm2rmid(*args, **kwargs)
        elif method == 'r/a':
            kwargs['rho'] = True
            return self.psinorm2rmid(*args, **kwargs)
        else:
            raise ValueError("psinorm2rho: Unsupported normalized coordinate method '%s'!" % method)
    
    def phinorm2psinorm(self, phinorm, t, **kwargs):
        """Calculates the normalized poloidal flux corresponding to the passed phinorm (normalized toroidal flux) values.

        Args:
            phinorm (Array-like or scalar float): Values of the normalized
                toroidal flux to map to psinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `phinorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `phinorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of psinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `phinorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `phinorm`
                or be a scalar. Default is True (evaluate ALL `phinorm` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from phinorm to
                psinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `psinorm` or (`psinorm`, `time_idxs`)
        
            * **psinorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `psinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value for phinorm=0.7, t=0.26s::
        
                psinorm_val = Eq_instance.phinorm2psinorm(0.7, 0.26)
            
            Find psinorm values at phinorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                psinorm_arr = Eq_instance.phinorm2psinorm([0.5, 0.7], 0.26)

            Find psinorm values at phinorm=0.5 at times t=[0.2s, 0.3s]::
        
                psinorm_arr = Eq_instance.phinorm2psinorm(0.5, [0.2, 0.3])

            Find psinorm values at (phinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                psinorm_arr = Eq_instance.phinorm2psinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._psinorm2Quan(self._getPhiNormToPsiNormSpline, phinorm, t, **kwargs)
    
    def phinorm2volnorm(self, *args, **kwargs):
        """Calculates the normalized flux surface volume corresponding to the passed phinorm (normalized toroidal flux) values.

        Args:
            phinorm (Array-like or scalar float): Values of the normalized
                toroidal flux to map to volnorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `phinorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `phinorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of volnorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `phinorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `phinorm`
                or be a scalar. Default is True (evaluate ALL `phinorm` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from phinorm to
                psinorm and psinorm to volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `volnorm` or (`volnorm`, `time_idxs`)
        
            * **volnorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `volnorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single volnorm value for phinorm=0.7, t=0.26s::
        
                volnorm_val = Eq_instance.phinorm2volnorm(0.7, 0.26)
            
            Find volnorm values at phinorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                volnorm_arr = Eq_instance.phinorm2volnorm([0.5, 0.7], 0.26)

            Find volnorm values at phinorm=0.5 at times t=[0.2s, 0.3s]::
        
                volnorm_arr = Eq_instance.phinorm2volnorm(0.5, [0.2, 0.3])

            Find volnorm values at (phinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                volnorm_arr = Eq_instance.phinorm2volnorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._phinorm2Quan(self._getVolNormSpline, *args, **kwargs)
    
    def phinorm2rmid(self, *args, **kwargs):
        """Calculates the mapped outboard midplane major radius corresponding to the passed phinorm (normalized toroidal flux) values.

        Args:
            phinorm (Array-like or scalar float): Values of the normalized
                toroidal flux to map to Rmid.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `phinorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `phinorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of Rmid. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `phinorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `phinorm`
                or be a scalar. Default is True (evaluate ALL `phinorm` at EACH
                element in `t`).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).                        
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).            
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from phinorm to
                psinorm and psinorm to Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `Rmid` or (`Rmid`, `time_idxs`)
        
            * **Rmid** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `Rmid`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single Rmid value for phinorm=0.7, t=0.26s::
        
                Rmid_val = Eq_instance.phinorm2rmid(0.7, 0.26)
            
            Find Rmid values at phinorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                Rmid_arr = Eq_instance.phinorm2rmid([0.5, 0.7], 0.26)

            Find Rmid values at phinorm=0.5 at times t=[0.2s, 0.3s]::
        
                Rmid_arr = Eq_instance.phinorm2rmid(0.5, [0.2, 0.3])

            Find Rmid values at (phinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                Rmid_arr = Eq_instance.phinorm2rmid([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        # Convert units from meters to desired target but keep units consistent
        # with rho keyword:
        if kwargs.get('rho', False):
            unit_factor = 1
        else:
            unit_factor = self._getLengthConversionFactor('m', kwargs.get('length_unit', 1))
        
        return unit_factor * self._phinorm2Quan(
            self._getRmidSpline,
            *args,
            **kwargs
        )
    
    def phinorm2roa(self, phi_norm, t, **kwargs):
        """Calculates the normalized minor radius corresponding to the passed phinorm (normalized toroidal flux) values.

        Args:
            phinorm (Array-like or scalar float): Values of the normalized
                toroidal flux to map to r/a.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `phinorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `phinorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of r/a. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `phinorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `phinorm`
                or be a scalar. Default is True (evaluate ALL `phinorm` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from phinorm to
                psinorm and psinorm to Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `roa` or (`roa`, `time_idxs`)
        
            * **roa** (`Array or scalar float`) - Normalized midplane minor
              radius. If all of the input arguments are scalar, then a scalar
              is returned. Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `roa`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single r/a value for phinorm=0.7, t=0.26s::
        
                roa_val = Eq_instance.phinorm2roa(0.7, 0.26)
            
            Find r/a values at phinorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                roa_arr = Eq_instance.phinorm2roa([0.5, 0.7], 0.26)

            Find r/a values at phinorm=0.5 at times t=[0.2s, 0.3s]::
        
                roa_arr = Eq_instance.phinorm2roa(0.5, [0.2, 0.3])

            Find r/a values at (phinorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                roa_arr = Eq_instance.phinorm2roa([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        kwargs['rho'] = True
        return self._phinorm2Quan(self._getRmidSpline, phi_norm, t, **kwargs)
    
    def phinorm2rho(self, method, *args, **kwargs):
        """Convert the passed (phinorm, t) coordinates into one of several coordinates.
        
        Args:
            method (String): Indicates which coordinates to convert to.
                Valid options are:
                
                    ======= ========================
                    psinorm Normalized poloidal flux
                    volnorm Normalized volume
                    Rmid    Midplane major radius
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            phinorm (Array-like or scalar float): Values of the normalized
                toroidal flux to map to rho.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `phinorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `phinorm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of rho. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `phinorm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `phinorm` or be
                a scalar. Default is True (evaluate ALL `phinorm` at EACH element in
                `t`).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).            
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                Rmid/phinorm/volnorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Raises:
            ValueError: If `method` is not one of the supported values.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at phinorm=0.6, t=0.26s::
            
                psi_val = Eq_instance.phinorm2rho('psinorm', 0.6, 0.26)

            Find psinorm values at phinorm of 0.6 and 0.8 at the
            single time t=0.26s::
            
                psi_arr = Eq_instance.phinorm2rho('psinorm', [0.6, 0.8], 0.26)

            Find psinorm values at phinorm of 0.6 at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.phinorm2rho('psinorm', 0.6, [0.2, 0.3])

            Find psinorm values at (phinorm, t) points (0.6, 0.2s) and (0.5m, 0.3s)::
            
                psi_arr = Eq_instance.phinorm2rho('psinorm', [0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        
        if method.startswith('sqrt'):
            kwargs['sqrt'] = True
            method = method[4:]
        
        if method == 'psinorm':
            return self.phinorm2psinorm(*args, **kwargs)
        elif method == 'volnorm':
            return self.phinorm2volnorm(*args, **kwargs)
        elif method == 'Rmid':
            return self.phinorm2rmid(*args, **kwargs)
        elif method == 'r/a':
            return self.phinorm2roa(*args, **kwargs)
        else:
            raise ValueError("phinorm2rho: Unsupported normalized coordinate method '%s'!" % method)
    
    def volnorm2psinorm(self, *args, **kwargs):
        """Calculates the normalized poloidal flux corresponding to the passed volnorm (normalized flux surface volume) values.

        Args:
            volnorm (Array-like or scalar float): Values of the normalized
                flux surface volume to map to psinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `volnorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `volnorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of psinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `volnorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `volnorm`
                or be a scalar. Default is True (evaluate ALL `volnorm` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from volnorm to
                psinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `psinorm` or (`psinorm`, `time_idxs`)
        
            * **psinorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `psinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value for volnorm=0.7, t=0.26s::
        
                psinorm_val = Eq_instance.volnorm2psinorm(0.7, 0.26)
            
            Find psinorm values at volnorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                psinorm_arr = Eq_instance.volnorm2psinorm([0.5, 0.7], 0.26)

            Find psinorm values at volnorm=0.5 at times t=[0.2s, 0.3s]::
        
                psinorm_arr = Eq_instance.volnorm2psinorm(0.5, [0.2, 0.3])

            Find psinorm values at (volnorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                psinorm_arr = Eq_instance.volnorm2psinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._psinorm2Quan(self._getVolNormToPsiNormSpline, *args, **kwargs)
    
    def volnorm2phinorm(self, *args, **kwargs):
        """Calculates the normalized toroidal flux corresponding to the passed volnorm (normalized flux surface volume) values.

        Args:
            volnorm (Array-like or scalar float): Values of the normalized
                flux surface volume to map to phinorm.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `volnorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `volnorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of phinorm. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `volnorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `volnorm`
                or be a scalar. Default is True (evaluate ALL `volnorm` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from volnorm to
                psinorm and psinorm to phinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `phinorm` or (`phinorm`, `time_idxs`)
        
            * **phinorm** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `phinorm`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single phinorm value for volnorm=0.7, t=0.26s::
        
                phinorm_val = Eq_instance.volnorm2phinorm(0.7, 0.26)
            
            Find phinorm values at volnorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                phinorm_arr = Eq_instance.volnorm2phinorm([0.5, 0.7], 0.26)

            Find phinorm values at volnorm=0.5 at times t=[0.2s, 0.3s]::
        
                phinorm_arr = Eq_instance.volnorm2phinorm(0.5, [0.2, 0.3])

            Find phinorm values at (volnorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                phinorm_arr = Eq_instance.volnorm2phinorm([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        return self._volNorm2Quan(self._getPhiNormSpline, *args, **kwargs)
    
    def volnorm2rmid(self, *args, **kwargs):
        """Calculates the mapped outboard midplane major radius corresponding to the passed volnorm (normalized flux surface volume) values.

        Args:
            volnorm (Array-like or scalar float): Values of the normalized
                flux surface volume to map to Rmid.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `volnorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `volnorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of Rmid. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `volnorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `volnorm`
                or be a scalar. Default is True (evaluate ALL `volnorm` at EACH
                element in `t`).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).                        
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).            
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from volnorm to
                psinorm and psinorm to Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `Rmid` or (`Rmid`, `time_idxs`)
        
            * **Rmid** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `Rmid`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single Rmid value for volnorm=0.7, t=0.26s::
        
                Rmid_val = Eq_instance.volnorm2rmid(0.7, 0.26)
            
            Find Rmid values at volnorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                Rmid_arr = Eq_instance.volnorm2rmid([0.5, 0.7], 0.26)

            Find Rmid values at volnorm=0.5 at times t=[0.2s, 0.3s]::
        
                Rmid_arr = Eq_instance.volnorm2rmid(0.5, [0.2, 0.3])

            Find Rmid values at (volnorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                Rmid_arr = Eq_instance.volnorm2rmid([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        # Convert units from meters to desired target but keep units consistent
        # with rho keyword:
        if kwargs.get('rho', False):
            unit_factor = 1
        else:
            unit_factor = self._getLengthConversionFactor('m', kwargs.get('length_unit', 1))
        
        return unit_factor * self._volNorm2Quan(self._getRmidSpline, *args, **kwargs)
    
    def volnorm2roa(self, *args, **kwargs):
        """Calculates the normalized minor radius corresponding to the passed volnorm (normalized flux surface volume) values.

        Args:
            volnorm (Array-like or scalar float): Values of the normalized
                flux surface volume to map to r/a.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `volnorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `volnorm`.
    
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of r/a. 
                Only the square root of positive values is taken. Negative 
                values are replaced with zeros, consistent with Steve Wolfe's
                IDL implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `volnorm` are evaluated 
                at each value in `t`. If True, `t` must have only one dimension
                (or be a scalar). If False, `t` must match the shape of `volnorm`
                or be a scalar. Default is True (evaluate ALL `volnorm` at EACH
                element in `t`).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from volnorm to
                psinorm and psinorm to Rmid. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.            
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
        
        Returns:
            `roa` or (`roa`, `time_idxs`)
        
            * **roa** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `roa`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
    
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single r/a value for volnorm=0.7, t=0.26s::
        
                roa_val = Eq_instance.volnorm2roa(0.7, 0.26)
            
            Find r/a values at volnorm values of 0.5 and 0.7 at the single time
            t=0.26s::
        
                roa_arr = Eq_instance.volnorm2roa([0.5, 0.7], 0.26)

            Find r/a values at volnorm=0.5 at times t=[0.2s, 0.3s]::
        
                roa_arr = Eq_instance.volnorm2roa(0.5, [0.2, 0.3])

            Find r/a values at (volnorm, t) points (0.6, 0.2s) and (0.5, 0.3s)::
        
                roa_arr = Eq_instance.volnorm2roa([0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        kwargs['rho'] = True
        return self._volNorm2Quan(self._getRmidSpline, *args, **kwargs)
    
    def volnorm2rho(self, method, *args, **kwargs):
        """Convert the passed (volnorm, t) coordinates into one of several coordinates.
        
        Args:
            method (String): Indicates which coordinates to convert to.
                Valid options are:
                
                    ======= ========================
                    psinorm Normalized poloidal flux
                    phinorm Normalized toroidal flux
                    Rmid    Midplane major radius
                    r/a     Normalized minor radius
                    ======= ========================
                
                Additionally, each valid option may be prepended with 'sqrt'
                to specify the square root of the desired unit.
            volnorm (Array-like or scalar float): Values of the normalized
                flux surface volume to map to rho.
            t (Array-like or scalar float): Times to perform the conversion at.
                If `t` is a single value, it is used for all of the elements of
                `volnorm`. If the `each_t` keyword is True, then `t` must be scalar
                or have exactly one dimension. If the `each_t` keyword is False,
                `t` must have the same shape as `volnorm`.
        
        Keyword Args:
            sqrt (Boolean): Set to True to return the square root of rho. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            each_t (Boolean): When True, the elements in `volnorm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `volnorm` or be
                a scalar. Default is True (evaluate ALL `volnorm` at EACH element in
                `t`).
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).            
            length_unit (String or 1): Length unit that `Rmid` is returned in.
                If a string is given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (use meters).
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from volnorm to
                Rmid/phinorm/psinorm. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            
        Returns:
            `rho` or (`rho`, `time_idxs`)
        
            * **rho** (`Array or scalar float`) - The converted coordinates. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        
        Raises:
            ValueError: If `method` is not one of the supported values.
        
        Examples:
            All assume that `Eq_instance` is a valid instance of the appropriate
            extension of the :py:class:`Equilibrium` abstract class.

            Find single psinorm value at volnorm=0.6, t=0.26s::
            
                psi_val = Eq_instance.volnorm2rho('psinorm', 0.6, 0.26)

            Find psinorm values at volnorm of 0.6 and 0.8 at the
            single time t=0.26s::
            
                psi_arr = Eq_instance.volnorm2rho('psinorm', [0.6, 0.8], 0.26)

            Find psinorm values at volnorm of 0.6 at times t=[0.2s, 0.3s]::
            
                psi_arr = Eq_instance.volnorm2rho('psinorm', 0.6, [0.2, 0.3])

            Find psinorm values at (volnorm, t) points (0.6, 0.2s) and (0.5m, 0.3s)::
            
                psi_arr = Eq_instance.volnorm2rho('psinorm', [0.6, 0.5], [0.2, 0.3], each_t=False)
        """
        
        if method.startswith('sqrt'):
            kwargs['sqrt'] = True
            method = method[4:]
        
        if method == 'psinorm':
            return self.volnorm2psinorm(*args, **kwargs)
        elif method == 'phinorm':
            return self.volnorm2phinorm(*args, **kwargs)
        elif method == 'Rmid':
            return self.volnorm2rmid(*args, **kwargs)
        elif method == 'r/a':
            return self.volnorm2roa(*args, **kwargs)
        else:
            raise ValueError("volnorm2rho: Unsupported normalized coordinate method '%s'!" % method)
    
    ###########################
    # Backend Mapping Drivers #
    ###########################

    def _psinorm2Quan(self, spline_func, psi_norm, t, each_t=True, return_t=False,
                      sqrt=False, rho=False, kind='cubic', time_idxs=None,
                      check_space=False, convert_only=True, length_unit=1):
        """Convert psinorm to a given quantity.
        
        Utility function for computing a variety of quantities given psi_norm
        and the relevant time indices.
        
        Args:
            spline_func (callable): Function which returns a 1d spline for the 
                quantity you want to convert into as a function of `psi_norm`
                given a time index.
            psi_norm (Array or scalar float): `psi_norm` values to evaluate at.
            time_idxs (Array or scalar float): Time indices for each of the
                `psi_norm` values. Shape must match that of `psi_norm`.
            t: Array or scalar float. Representative time array that `psi_norm`
                and `time_idxs` was formed from (used to determine output shape).
        
        Keyword Args:
            each_t (Boolean): When True, the elements in `psi_norm` are evaluated at
                each value in `t`. If True, `t` must have only one dimension (or
                be a scalar). If False, `t` must match the shape of `psi_norm` or be
                a scalar. Default is True (evaluate ALL `psi_norm` at EACH element in
                `t`).
            return_t (Boolean): Set to True to return a tuple of (`rho`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `rho` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `rho`).
            sqrt (Boolean): Set to True to return the square root of `rho`. Only
                the square root of positive values is taken. Negative values are
                replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False.
            rho (Boolean): Set to True to return r/a (normalized minor radius)
                instead of Rmid. Default is False (return major radius, Rmid).            
                Note that this will have unexpected results if `spline_func`
                returns anything other than R_mid.
            kind (String or non-negative int): Specifies the type of
                interpolation to be performed in getting from psinorm to
                `rho`. This is passed to
                :py:class:`scipy.interpolate.interp1d`. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for :py:class:`interp1d` for more
                details. Default value is 'cubic' (3rd order spline
                interpolation). On some builds of scipy, this can cause problems,
                in which case you should try 'linear' until you can rebuild your
                scipy install.
            time_idxs (Array with same shape as `psi_norm` or None):
                The time indices to use (as computed by :py:meth:`_processRZt`).
                Default is None (compute time indices in method).
        
        Returns:
            (`rho`, `time_idxs`)
            
            * **rho** (`Array or scalar float`) - The converted quantity. If
              all of the input arguments are scalar, then a scalar is returned.
              Otherwise, a scipy Array is returned.
            * **time_idxs** (Array with same shape as `rho`) - The indices 
              (in :py:meth:`self.getTimeBase`) that were used for
              nearest-neighbor interpolation. Only returned if `return_t` is
              True.
        """
 
        if time_idxs is None:
            (psi_norm,
             dum,
             t,
             time_idxs,
             original_shape,
             single_val,
             single_time) = self._processRZt(psi_norm, psi_norm, t,
                                             each_t=each_t, make_grid=False,
                                             check_space=check_space,
                                             length_unit=length_unit,
                                             convert_only=convert_only)
        else:
            single_val = True
            try:
                iter(psi_norm)
            except TypeError:
                psi_norm = scipy.asarray([psi_norm], dtype=float)
            else:
                single_val = False
                # This is almost certainly redundant for the designed use case,
                # but should add minimal overhead in either case:
                psi_norm = scipy.asarray(psi_norm, dtype=float)
            
            original_shape = psi_norm.shape
            psi_norm = scipy.reshape(psi_norm, -1)
            time_idxs = scipy.reshape(time_idxs, -1)
            
            # TODO: This might waste more time than it saves with long time_idxs:
            single_time = (len(scipy.unique(time_idxs)) == 1)

        if not self._tricubic:
            if single_time:
                quan_norm = spline_func(time_idxs[0], kind=kind)(psi_norm)
            else:
                # TODO: This can probaby be done a lot better!
                quan_norm = scipy.zeros(psi_norm.shape)
                for k in xrange(0, len(quan_norm)):
                    quan_norm[k] = spline_func(time_idxs[k], kind=kind)(psi_norm[k])
        else:
            quan_norm = spline_func(time_idxs).ev(time_idxs, psi_norm)
        
        # Convert to r/a if needed:
        if rho:
            quan_norm = self._rmid2roa(quan_norm, time_idxs)
        
        # Restore original shape:
        quan_norm = scipy.reshape(quan_norm, original_shape)
 
        if sqrt:
            scipy.place(quan_norm, quan_norm < 0, 0.0)
            out = scipy.sqrt(quan_norm)
        else:
            out = quan_norm

        if single_val:
            out = out[0]
            time_idxs = time_idxs[0]
 
        if return_t:
            return (out, time_idxs)
        else:
            return out
    
    def _rmid2roa(self, R_mid, time_idxs):
        r"""Covert the given `R_mid` at the given `time_idxs` to r/a.
        
        If you want to use a different definition of r/a, you should override
        this function and :py:meth:`_roa2rmid`.
        
        The definition used here is
        
        .. math::
            
            r/a = \frac{R_{mid} - R_0}{R_a - R_0} = \frac{R_{mid} - R_0}{a}
        
        Args:
            R_mid (Array or scalar float): Values of outboard midplane major
                radius to evaluate r/a at.
            time_idxs (Array, same shape as `R_mid`): If :py:attr:`self._tricubic`
                is True, this should be an array of the time points to evaluate
                at. Otherwise, this should be an array of the time INDICES in
                :py:meth:`getTimeBase` to evaluate at.
        
        Returns:
            roa (Array): Same shape as `R_mid` and `time_idxs`. The normalized minor radius at the given `R_mid`, `t` points.
        """
        # Get necessary quantities at the relevant times:
        if not self._tricubic:
            magR = self.getMagR(length_unit='m')[time_idxs]
            Rout = self.getRmidOut(length_unit='m')[time_idxs]
        else:
            magR = self.getMagRSpline(length_unit='m')(time_idxs)
            Rout = self.getRmidOutSpline(length_unit='m')(time_idxs)
        
        # Compute r/a according to our definition:
        return (R_mid - magR) / (Rout - magR)

    def _roa2rmid(self, roa, time_idxs):
        r"""Covert the given r/a at the given time_idxs to R_mid.
        
        If you want to use a different definition of r/a, you should override
        this function and :py:meth:`_rmid2roa`.
        
        The definition used here is
        
        .. math::
            
            r/a = \frac{R_{mid} - R_0}{R_a - R_0} = \frac{R_{mid} - R_0}{a}
        
        Args:
            roa (Array or scalar float): Values of normalized minor radius to
                evaluate R_mid at.
            time_idxs (Array, same shape as `roa`): If :py:attr:`self._tricubic`
                is True, this should be an array of the time points to evaluate
                at. Otherwise, this should be an array of the time INDICES in
                :py:meth:`getTimeBase` to evaluate at.
        
        Returns:
            R_mid (Array): Same shape as `roa` and `time_idxs`. The mapped midplane major radius at the given `roa`, `t` points.
        """
        # Get necessary quantities at the relevant times:
        if not self._tricubic:
            magR = self.getMagR(length_unit='m')[time_idxs]
            Rout = self.getRmidOut(length_unit='m')[time_idxs]
        else:
            magR = self.getMagRSpline(length_unit='m')(time_idxs)
            Rout = self.getRmidOutSpline(length_unit='m')(time_idxs)
        
        # Compute R_mid according to our definition:
        return roa * (Rout - magR) + Rout
    
    def _RZ2Quan(self, spline_func, R, Z, t, **kwargs):
        """Convert RZ to a given quantity.
        
        Utility function for converting R, Z coordinates to a variety of things
        that are interpolated from something measured on a uniform normalized
        flux grid, in particular phi_norm, vol_norm and R_mid.
        
        If tspline is False for this Equilibrium instance, uses
        scipy.interpolate.RectBivariateSpline to interpolate in terms of R and
        Z. Finds the nearest time slices to those given: nearest-neighbor
        interpolation in time. Otherwise, uses the tricubic package to perform
        a trivariate interpolation in space and time.
        
        Args:
            spline_func (callable): Function which returns a 1d spline for the
                quantity you want to convert into as a function of psi_norm
                given a time index.
            R (Array-like or scalar float): Values of the radial coordinate to
                map to Quan. If R and Z are both scalar values, they are used
                as the coordinate pair for all of the values in t. Must have
                the same shape as Z unless the make_grid keyword is set. If the
                make_grid keyword is True, R must have shape (len_R,).
            Z (Array-like or scalar float): Values of the vertical coordinate to
                map to Quan. If R and Z are both scalar values, they are used
                as the coordinate pair for all of the values in t. Must have
                the same shape as R unless the make_grid keyword is set. If the
                make_grid keyword is True, Z must have shape (len_Z,).
            t (Array-like or single value): If t is a single value, it is used
                for all of the elements of R, Z. If t is array-like and the
                make_grid keyword is False, t must have the same dimensions as
                R and Z. If t is array-like and the make_grid keyword is True,
                t must have shape (len(Z), len(R)).
        
        Keyword Args:
            each_t (Boolean):
                When True, the elements in `R` and `Z` (or the meshgrid thereof
                if `make_grid` is True) are evaluated at each value in `t`. If
                True, `t` must have only one dimension (or be a scalar). If
                False, `t` must match the shape of `R` and `Z` (or their
                meshgrid if `make_grid` is True) or be a scalar. Default is True
                (evaluate ALL `R`, `Z` at each element in `t`).
            return_t (Boolean):
                Set to True to return a tuple of (Quan,
                time_idxs), where time_idxs is the array of time indices
                actually used in evaluating R_mid with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return Quan).
            sqrt (Boolean):
                Set to True to return the square root of Quan. Only
                the square root of positive values is taken. Negative values
                are replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False (return Quan
                itself).
            make_grid (Boolean):
                Set to True to pass R and Z through meshgrid
                before evaluating. If this is set to True, R and Z must each
                only have a single dimension, but can have different lengths.
                When using this option, it is highly recommended to only pass
                a scalar value for t (such that each point in the flux grid is
                evaluated at this same value t). Otherwise, t must have the
                same shape as the resulting meshgrid, and each element in the
                returned psi array will be at the corresponding time in the t
                array. Default is False (do not form meshgrid).
            rho (Boolean):
                Set to True to return r/a (normalized minor radius)
                instead of R_mid. Default is False (return major radius, R_mid).
                Note that this will have unexpected results if spline_func
                returns anything other than R_mid.
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to Quan. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
            length_unit (String or 1):
                Length unit that R and Z are being given
                in. If a string is given, it must be a valid unit specifier:
                
                    =========== ===========
                    'm'         meters
                    'cm'        centimeters
                    'mm'        millimeters
                    'in'        inches
                    'ft'        feet
                    'yd'        yards
                    'smoot'     smoots
                    'cubit'     cubits
                    'hand'      hands
                    'default'   meters
                    =========== ===========
                    
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (R and Z given in meters). Note that this factor is
                ONLY applied to the inputs in this function -- if Quan needs to
                be corrected, it must be done in the calling function.
        
        Returns:
            Quan: Array or scalar float. If all of the input arguments are
                scalar, then a scalar is returned. Otherwise, a scipy Array
                instance is returned. If R and Z both have the same shape then
                Quand has this shape as well. If the make_grid keyword was True
                then R_mid has shape (len(Z), len(R)).
            time_idxs: Array with same shape as R_mid. The indices (in
                self.getTimeBase()) that were used for nearest-neighbor
                interpolation. Only returned if return_t is True.
        """
        return_t = kwargs.get('return_t', False)
        kwargs['return_t'] = True
        
        # Not used by rz2psinorm:
        kind = kwargs.pop('kind', 'cubic')
        rho = kwargs.pop('rho', False)

        psi_norm, time_idxs = self.rz2psinorm(R, Z, t, **kwargs)
        
        kwargs['return_t'] = return_t
        
        # Not used by _psinorm2Quan
        kwargs.pop('length_unit', 1)
        kwargs.pop('make_grid', False)
        
        kwargs['rho'] = rho
        # TODO: This technically computes the time indices twice. Is there are
        # good compromise to get the best of both worlds (nice calling of
        # _psinorm2Quan AND no recompute)?
        return self._psinorm2Quan(spline_func,
                                  psi_norm,
                                  t,
                                  time_idxs=time_idxs,
                                  kind=kind,
                                  **kwargs)
    
    def _Rmid2Quan(self, spline_func, R_mid, t, **kwargs):
        """Convert R_mid to a given quantity.
        
        Utility function for converting R, Z coordinates to a variety of things
        that are interpolated from something measured on a uniform normalized
        flux grid, in particular phi_norm and vol_norm.
        
        If tspline is False for this Equilibrium instance, uses
        scipy.interpolate.RectBivariateSpline to interpolate in terms of R and
        Z. Finds the nearest time slices to those given: nearest-neighbor
        interpolation in time. Otherwise, uses the tricubic package to perform
        a trivariate interpolation in space and time.
        
        Args:
            spline_func (callable):
                Function which returns a 1d spline for the quantity
                you want to convert into as a function of psi_norm given a
                time index.
            R_mid (Array-like or scalar float):
                Values of the radial coordinate to map to Quan.
            t (Array-like or single value):
                If t is a single value, it is used
                for all of the elements of R_mid. If t is array-like it must
                have the same dimensions as R_mid.
        
        Keyword Args:
            each_t (Boolean):
                When True, the elements in `R` and `Z` (or the meshgrid thereof
                if `make_grid` is True) are evaluated at each value in `t`. If
                True, `t` must have only one dimension (or be a scalar). If
                False, `t` must match the shape of `R` and `Z` (or their
                meshgrid if `make_grid` is True) or be a scalar. Default is True
                (evaluate ALL `R`, `Z` at each element in `t`).
            return_t (Boolean):
                Set to True to return a tuple of (Quan,
                time_idxs), where time_idxs is the array of time indices
                actually used in evaluating R_mid with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return Quan).
            sqrt (Boolean):
                Set to True to return the square root of Quan. Only
                the square root of positive values is taken. Negative values
                are replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False (return Quan
                itself).
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to Quan. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
            length_unit (String or 1):
                Length unit that R and Z are being given
                in. If a string is given, it must be a valid unit specifier:
                    'm'         meters
                    'cm'        centimeters
                    'mm'        millimeters
                    'in'        inches
                    'ft'        feet
                    'yd'        yards
                    'smoot'     smoots
                    'cubit'     cubits
                    'hand'      hands
                    'default'   meters
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (R_mid given in meters). Note that this factor is
                ONLY applied to the inputs in this function -- if Quan needs to
                be corrected, it must be done in the calling function.
        
        Returns:
            Quan: Array or scalar float. If all of the input arguments are
                scalar, then a scalar is returned. Otherwise, a scipy Array
                instance is returned. Has the same shape as R_mid.
            time_idxs: Array with same shape as Quan. The indices (in
                self.getTimeBase()) that were used for nearest-neighbor
                interpolation. Only returned if return_t is True.
        """
        return_t = kwargs.get('return_t', False)
        kwargs['return_t'] = True
        
        # Not used by rmid2psinorm:
        kind = kwargs.pop('kind', 'cubic')
        rho = kwargs.pop('rho', False)

        psi_norm, time_idxs = self.rmid2psinorm(R_mid, t, **kwargs)
        
        kwargs['time_idxs'] = time_idxs
        kwargs['kind'] = kind
        kwargs['return_t'] = return_t
        kwargs['rho'] = rho
        
        # Not used by _psinorm2Quan
        kwargs.pop('length_unit', 1)
        kwargs.pop('make_grid', False)
        
        # TODO: This technically computes the time indices twice. Is there are
        # good compromise to get the best of both worlds (nice calling of
        # _psinorm2Quan AND no recompute)?
        return self._psinorm2Quan(spline_func,
                                  psi_norm,
                                  t,
                                  **kwargs)
    
    def _phiNorm2Quan(self, spline_func, phinorm, t, **kwargs):
        """Convert phinorm to a given quantity.
        
        Utility function for converting phinorm coordinates to a variety of things
        that are interpolated from something measured on a uniform normalized
        flux grid, in particular psi_norm and vol_norm.
        
        If tspline is False for this Equilibrium instance, uses
        scipy.interpolate.RectBivariateSpline to interpolate in terms of R and
        Z. Finds the nearest time slices to those given: nearest-neighbor
        interpolation in time. Otherwise, uses the tricubic package to perform
        a trivariate interpolation in space and time.
        
        Args:
            spline_func (callable):
                Function which returns a 1d spline for the quantity
                you want to convert into as a function of psi_norm given a
                time index.
            phinorm (Array-like or scalar float):
                Values of the normalized toroidal flux to map to `Quan`.
            t (Array-like or single value):
                If `t` is a single value, it is used
                for all of the elements of `phinorm`. If `t` is array-like it
                must have the same dimensions as `phinorm`.
        
        Keyword Args:
            each_t (Boolean):
                When True, the elements in `phinorm` are evaluated at each value
                in `t`. If True, `t` must have only one dimension (or be a
                scalar). If False, `t` must match the shape of `phinorm` or be a
                scalar. Default is True (evaluate ALL `phinorm` at each element
                in `t`).
            return_t (Boolean):
                Set to True to return a tuple of (`Quan`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `phinorm` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `Quan`).
            sqrt (Boolean):
                Set to True to return the square root of `Quan`. Only
                the square root of positive values is taken. Negative values
                are replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False (return Quan
                itself).
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from `psinorm` to `Quan`. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            Quan: Array or scalar float. If all of the input arguments are
                scalar, then a scalar is returned. Otherwise, a scipy Array
                instance is returned. Has the same shape as `phinorm`.
            time_idxs: Array with same shape as `Quan`. The indices (in
                self.getTimeBase()) that were used for nearest-neighbor
                interpolation. Only returned if `return_t` is True.
        """
        return_t = kwargs.get('return_t', False)
        kwargs['return_t'] = True
        
        # Not used by phinorm2psinorm:
        kind = kwargs.pop('kind', 'cubic')
        rho = kwargs.pop('rho', False)

        psi_norm, time_idxs = self.phinorm2psinorm(phinorm, t, **kwargs)
        
        kwargs['return_t'] = return_t
        kwargs['rho'] = rho
        kwargs['kind'] = kind
        
        # Not used by _psinorm2Quan
        kwargs.pop('length_unit', 1)
        
        # TODO: This technically computes the time indices twice. Is there are
        # good compromise to get the best of both worlds (nice calling of
        # _psinorm2Quan AND no recompute)?
        return self._psinorm2Quan(spline_func,
                                  psi_norm,
                                  t,
                                  time_idxs=time_idxs,
                                  **kwargs)
    
    def _volNorm2Quan(self, spline_func, volnorm, t, **kwargs):
        """Convert volnorm to a given quantity.
        
        Utility function for converting volnorm coordinates to a variety of things
        that are interpolated from something measured on a uniform normalized
        flux grid, in particular psi_norm and phi_norm.
        
        If tspline is False for this Equilibrium instance, uses
        scipy.interpolate.RectBivariateSpline to interpolate in terms of R and
        Z. Finds the nearest time slices to those given: nearest-neighbor
        interpolation in time. Otherwise, uses the tricubic package to perform
        a trivariate interpolation in space and time.
        
        Args:
            spline_func (callable): Function which returns a 1d spline for the quantity
                you want to convert into as a function of psi_norm given a
                time index.
            volnorm (Array-like or scalar float):
                Values of the normalized volume to map to `Quan`.
            t (Array-like or single value):
                If `t` is a single value, it is used
                for all of the elements of `volnorm`. If `t` is array-like it
                must have the same dimensions as `volnorm`.
        
        Keyword Args:
            each_t (Boolean):
                When True, the elements in `volnorm` are evaluated at each value
                in `t`. If True, `t` must have only one dimension (or be a
                scalar). If False, `t` must match the shape of `volnorm` or be a
                scalar. Default is True (evaluate ALL `volnorm` at each element
                in `t`).
            return_t (Boolean):
                Set to True to return a tuple of (`Quan`,
                `time_idxs`), where `time_idxs` is the array of time indices
                actually used in evaluating `phinorm` with nearest-neighbor
                interpolation. (This is mostly present as an internal helper.)
                Default is False (only return `Quan`).
            sqrt (Boolean):
                Set to True to return the square root of `Quan`. Only
                the square root of positive values is taken. Negative values
                are replaced with zeros, consistent with Steve Wolfe's IDL
                implementation efit_rz2rho.pro. Default is False (return Quan
                itself).
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from `volnorm` to `Quan`. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            Quan: Array or scalar float. If all of the input arguments are
                scalar, then a scalar is returned. Otherwise, a scipy Array
                instance is returned. Has the same shape as `volnorm`.
            time_idxs: Array with same shape as `Quan`. The indices (in
                self.getTimeBase()) that were used for nearest-neighbor
                interpolation. Only returned if `return_t` is True.
        """
        return_t = kwargs.get('return_t', False)
        kwargs['return_t'] = True
        
        # Not used by phinorm2psinorm:
        kind = kwargs.pop('kind', 'cubic')
        rho = kwargs.pop('rho', False)

        psi_norm, time_idxs = self.volnorm2psinorm(volnorm, t, **kwargs)
        
        kwargs['return_t'] = return_t
        kwargs['rho'] = rho
        kwargs['kind'] = kind
        
        # Not used by _psinorm2Quan
        kwargs.pop('length_unit', 1)
        
        # TODO: This technically computes the time indices twice. Is there are
        # good compromise to get the best of both worlds (nice calling of
        # _psinorm2Quan AND no recompute)?
        return self._psinorm2Quan(spline_func,
                                  psi_norm,
                                  t,
                                  time_idxs=time_idxs,
                                  **kwargs)
    
    ####################
    # Helper Functions #
    ####################

    def _getLengthConversionFactor(self, start, end, default=None):
        """Gets the conversion factor to convert from units start to units end.
        
        Uses a regex to parse units of the form:
        'm'
        'm^2'
        'm2'
        Leading and trailing spaces are NOT allowed.
        
        Valid unit specifiers are:
            'm'         meters
            'cm'        centimeters
            'mm'        millimeters
            'in'        inches
            'ft'        feet
            'yd'        yards
            'smoot'     smoots
            'cubit'     cubits
            'hand'      hands
        
        Args:
            start (String, int or None):
                Starting unit for the conversion.
                - If None, uses the unit specified when the instance was created.
                - If start is an int, the starting unit is taken to be the unit
                    specified when the instance was created raised to that power.
                - If start is 'default', either explicitly or because of
                    reverting to the instance-level unit, then the value passed
                    in the kwarg default is used. In this case, default must be
                    a complete unit string (i.e., not None, not an int and not
                    'default').
                - Otherwise, start must be a valid unit specifier as given above.
            end (String, int or None):
                Target (ending) unit for the conversion.
                - If None, uses the unit specified when the instance was created.
                - If end is an int, the target unit is taken to be the unit
                    specified when the instance was created raised to that power.
                - If end is 'default', either explicitly or because of
                    reverting to the instance-level unit, then the value passed
                    in the kwarg default is used. In this case, default must be
                    a complete unit string (i.e., not None, not an int and not
                    'default').
                - Otherwise, end must be a valid unit specifier as given above.
                    In this case, if end does not specify an exponent, it uses
                    whatever the exponent on start is. This allows a user to
                    ask for an area in units of m^2 by specifying
                    length_unit='m', for instance. An error will still be
                    raised if the user puts in a completely inconsistent
                    specification such as length_unit='m^3' or length_unit='m^1'.
        
        Keyword Args:
            default (String, int or None):
                The default unit to use in cases
                where start or end is 'default'. If default is None, an int, or 
                'default', then the value given for start is used. (A circular
                definition is prevented for cases in which start is default by
                checking for this case during the handling of the case
                start=='default'.)
        
        Returns:
            Conversion factor: Scalar float. The conversion factor to get from
                the start unit to the end unit.
        
        Raises:
            ValueError: If start is 'default' and default is None, an int, or
                'default'.
            ValueError: If the (processed) exponents of start and end or start
                and default are incompatible.
            ValueError: If the processed units for start and end are not valid.
        """
        # Input handling:
        # Starting unit:
        if start is None:
            # If start is None, it means to use the instance's default unit (implied to the power of 1):
            start = self._length_unit
        elif isinstance(start, (int, long)):
            # If start is an integer type, this is used as the power applied to the instance's default unit:
            if self._length_unit != 'default':
                start = self._length_unit + '^' + str(start)
            else:
                # If the instance's default unit is 'default', this is handled next:
                start = self._length_unit
        if start == 'default':
            # If start is 'default', the thing passed to default is used, but only if it is a complete unit specification:
            if default is None or isinstance(default, (int, long)) or default == 'default':
                raise ValueError("You must specify a complete unit (i.e., "
                                 "non-None, non-integer and not 'default') "
                                 "when using 'default' for the starting unit.")
            else:
                start = default
        
        # Default unit:
        if default is None or isinstance(default, (int, long)) or default == 'default':
            # If start is 'default', these cases have already been caught above.
            default = start
        
        # Target (ending) unit:
        if end is None:
            # If end is None, it means to use the instance's default unit (implied to the power of 1):
            end = self._length_unit
        elif isinstance(end, (int, long)):
            # If end is an integer type, this is used as the power applied to the instance's default unit:
            if self._length_unit != 'default':
                end = self._length_unit + '^' + str(end)
            else:
                # If the instance's default unit is 'default', this is handled next:
                end = self._length_unit
        if end == 'default':
            # If end is 'default', the thing passed to default is used, which
            # defaults to start, which itself is not allowed to be 'default':
            end = default
        
        unit_regex = r'^([A-Za-z]+)\^?([0-9]*)$'
        
        # Need to explicitly cast because MDSplus returns its own classes and
        # re.split doesn't seem to handle the polymorphism properly:
        start = str(start)
        end = str(end)
        default = str(default)
        
        dum1, start_u, start_pow, dum2 = re.split(unit_regex, start)
        dum1, end_u, end_pow, dum2 = re.split(unit_regex, end)
        dum1, default_u, default_pow, dum2 = re.split(unit_regex, default)
        
        start_pow = 1.0 if start_pow == '' else float(start_pow)
        if end_pow == '':
            end_pow = start_pow
        else:
            end_pow = float(end_pow)
        default_pow = 1.0 if default_pow == '' else float(default_pow)
        
        if start_pow != end_pow or start_pow != default_pow:
            raise ValueError("Incompatible exponents between '%s', '%s' and '%s'!" % (start, end, default))
        try:
            return (_length_conversion[start_u][end_u])**start_pow
        except KeyError:
            raise ValueError("Unit '%s' is not a recognized length unit!" % end)

    def _processRZt(self, R, Z, t, make_grid=False, each_t=True, check_space=True, length_unit=1, convert_only=False):
        """Input checker/processor.
        
        Takes R, Z and t. Appropriately packages them into scipy arrays. Checks
        the validity of the R, Z ranges. If there is a single time value but
        multiple R, Z values, creates matching time vector. If there is a single
        R, Z value but multiple t values, creates matching R and Z vectors.
        Finds list of nearest-neighbor time indices.
        
        Args:
            R (Array-like or scalar float):
                Values of the radial coordinate. If `R` and `Z` are both scalar
                values, they are used as the coordinate pair for all of the
                values in `t`. Must have the same shape as `Z` unless the
                `make_grid` keyword is True. If `make_grid` is True, `R` must
                have only one dimension (or be a scalar).
            Z (Array-like or scalar float):
                Values of the vertical coordinate. If `R` and `Z` are both
                scalar values, they are used as the coordinate pair for all of
                the values in `t`. Must have the same shape as `R` unless the
                `make_grid` keyword is True. If `make_grid` is True, `Z` must
                have only one dimension.
            t (Array-like or single value):
                If `t` is a single value, it is used for all of the elements of
                `R`, `Z`. If `t` is array-like and `make_grid` is False, `t`
                must have the same dimensions as `R` and `Z`. If `t` is
                array-like and `make_grid` is True, `t` must have shape
                (len(Z), len(R)).
        
        Keyword Args:
            make_grid (Boolean):
                Set to True to pass `R` and `Z` through :py:func:`meshgrid`
                before evaluating. If this is set to True, `R` and `Z` must each
                only have a single dimension, but can have different lengths.
                Default is False (do not form meshgrid).
            each_t (Boolean):
                When True, the elements in `R` and `Z` (or the meshgrid thereof
                if `make_grid` is True) are evaluated at each value in `t`. If
                True, `t` must have only one dimension (or be a scalar). If
                False, `t` must match the shape of `R` and `Z` (or their
                meshgrid if `make_grid` is True) or be a scalar. Default is True
                (evaluate ALL `R`, `Z` at each element in `t`).
            check_space (Boolean):
                If True, `R` and `Z` are converted to meters and checked against
                the extents of the spatial grid.
            length_unit (String or 1):
                Length unit that `R` and `Z` are being given in. If a string is
                given, it must be a valid unit specifier:
                
                    ===========  ===========
                    'm'          meters
                    'cm'         centimeters
                    'mm'         millimeters
                    'in'         inches
                    'ft'         feet
                    'yd'         yards
                    'smoot'      smoots
                    'cubit'      cubits
                    'hand'       hands
                    'default'    meters
                    ===========  ===========
                
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (R and Z given in meters). Note that this factor is
                ONLY applied to the inputs in this function -- if Quan needs to
                be corrected, it must be done in the calling function.
        
        Returns:
            Tuple of:
            
            * **R** - Flattened `R` array with out-of-range values replaced with NaN.
            * **Z** - Flattened Z array with out-of-range values replaced with NaN.
            * **t** - Flattened t array with out-of-range values replaced with NaN.
            * **time_idxs** - Flattened array of nearest-neighbor time indices.
            * **original_shape** - Original shape tuple, used to return the
              arrays to their starting form.
            * **single_val** - Boolean indicating whether a single point is used.
              If True, then the final step of the calling code should unpack the
              result from the array.
            * **single_time** - Boolean indicating whether a single time value
              is used. If True, then certain simplifying steps can be made.
        """

        # Handle single-value form of R and Z:
        single_val = True
        try:
            iter(R)
        except TypeError:
            R = scipy.asarray([R], dtype=float)
        else:
            single_val = False
            R = scipy.asarray(R, dtype=float)
        
        try:
            iter(Z)
        except TypeError:
            Z = scipy.asarray([Z], dtype=float)
        else:
            single_val = False
            Z = scipy.asarray(Z, dtype=float)

        # Make the grid, if called for:
        if make_grid:
            if R.ndim != 1 or Z.ndim != 1:
                raise ValueError('_processRZt: When using the make_grid keyword, the '
                                 'number of dimensions of R and Z must both be one!')
            R, Z = scipy.meshgrid(R, Z)

        if R.shape != Z.shape:
            raise ValueError('_processRZt: Shape of R and Z arrays must match!')

        # Check that R, Z points are fine:
        if check_space:
            # Convert units to meters:
            unit_factor = self._getLengthConversionFactor(length_unit, 'm', default='m')
            R = unit_factor * R
            Z = unit_factor * Z
            
            if not convert_only:
                good_points, num_good = self._checkRZ(R, Z)

                if num_good < 1:
                    raise ValueError('_processRZt: No valid points!')

                if not single_val:
                    # Mask out the bad points here so we don't interfere with the
                    # single-value case (which must be valid to have made it past the
                    # test above):
                    scipy.place(R, ~good_points, scipy.nan)
                    scipy.place(Z, ~good_points, scipy.nan)

        # Handle single-value time cases:
        
        try:
            iter(t)
        except TypeError:
            single_time = True
            # The bivariate spline case technically only needs one element, but
            # the trispline case looks like it needs the full shape.
            t = t * scipy.ones_like(R, dtype=float)
        else:
            single_time = False
            t = scipy.asarray(t, dtype=float)
   
        if each_t and not single_time:
            if t.ndim != 1:
                raise ValueError("_processRZt: When using the each_t keyword, "
                                 "t must have only one dimension.")
            single_val = False
            R = scipy.tile(R, [len(t),] + [1,] * R.ndim)
            Z = scipy.tile(Z, [len(t),] + [1,] * Z.ndim)
            t = t[scipy.indices(R.shape)[0]]

        if t.size > 1 and t.shape != R.shape:
            if make_grid:
                raise ValueError('_processRZt: shape of t does not match shape of R '
                                 'and Z. Recall that use of the make_grid '
                                 'keyword requires that t either be a single '
                                 'value, or that its shape matches that of '
                                 'scipy.meshgrid(R, Z).')
            else:
                raise ValueError('_processRZt: t must either be a single number, '
                                 'or must match the shape of R and Z!')

        # Handle non-vector array inputs: store the shape, then flatten the arrays.
        # Don't bother with a test/flag -- just use the shape vector at the end.
        original_shape = R.shape
        R = scipy.reshape(R, -1)
        Z = scipy.reshape(Z, -1)
        t = scipy.reshape(t, -1)
 
        # Takes keyword to bypass for tricubic interpolation
        if not self._tricubic:
            timebase = self.getTimeBase()
            # Set up times to use -- essentially use nearest-neighbor interpolation
            time_idxs = self._getNearestIdx(t, timebase)
            # Check errors and warn if needed:
            t_errs = scipy.absolute(t - timebase[time_idxs])
            if len(timebase) > 1 and (t_errs > scipy.mean(scipy.diff(timebase)) / 3.0).any():
                warnings.warn("Some time points are off by more than 1/3 "
                              "the EFIT point spacing. Using nearest-neighbor interpolation "
                              "between time points. You may want to run EFIT on the timebase "
                              "you need. Max error: %.3fs" % max(t_errs),
                              RuntimeWarning)

                # If a single time value is passed with multiple R, Z points, evaluate
                # them all at that time point:
            if single_time and not single_val:
                t = scipy.ones(R.shape) * t[0]
                time_idxs = scipy.ones(R.shape, dtype=int) * time_idxs[0]
        else:
            time_idxs = t

        return (R, Z, t, time_idxs, original_shape, single_val, single_time)

    def _checkRZ(self, R, Z):
        """Checks whether or not the passed arrays of (R, Z) are within the bounds of the reconstruction data.
        
        Returns the mask array of booleans indicating the goodness of each point
        at the corresponding index. Raises warnings if there are no good_points
        and if there are some values out of bounds.
        
        Assumes R and Z are in meters and that the R and Z arrays returned by
        this instance's getRGrid() and getZGrid() are monotonically increasing.
        
        Args:
            R (Array):
                Radial coordinate to check. Must have the same size as Z.
            Z (Array)
                Vertical coordinate to check. Must have the same size as R.
        
        Returns:
            good_points: Boolean array. True where points are within the bounds
                defined by self.getRGrid and self.getZGrid.
            num_good: The number of good points.
        """
        good_points = ((R <= self.getRGrid(length_unit='m')[-1]) &
                       (R >= self.getRGrid(length_unit='m')[0]) &
                       (Z <= self.getZGrid(length_unit='m')[-1]) &
                       (Z >= self.getZGrid(length_unit='m')[0]))
        # Gracefully handle single-value versus array inputs, returning in the
        # corresponding type.
        num_good = scipy.sum(good_points)
        test = scipy.array(R)
        if len(test.shape) > 0:
            num_pts = test.size
        else:
            num_good = good_points
            num_pts = 1
        if num_good == 0:
            warnings.warn("Warning: _checkRZ: No valid (R, Z) points!",
                          RuntimeWarning)
        elif num_good != num_pts:
            warnings.warn("Warning: _checkRZ: Some (R, Z) values out of bounds. "
                          "(%(bad)d bad out of %(tot)d)"
                          % {'bad': num_pts - num_good, 'tot': num_pts},
                          RuntimeWarning)
        
        return (good_points, num_good)

    def _getNearestIdx(self, v, a):
        """Returns the array of indices of the nearest value in a corresponding to each value in v.
        
        If the monotonic keyword in the instance is True, then this is done using
        scipy.digitize under the assumption that a is monotonic. Otherwise,
        this is done in a general manner by looking for the minimum distance
        between the points in v and a.
        
        Args:
            v (Array):
                Input values to match to nearest neighbors in a.
            a (Array):
                Given values to match against.
        
        Returns:
            Indices in a of the nearest values to each value in v. Has the same
                shape as v.
        """
        # Gracefully handle single-value versus array inputs, returning in the
        # corresponding type.
        if not self._monotonic:
            try:
                return scipy.array([(scipy.absolute(a - val)).argmin() for val in v])
            except TypeError:
                return (scipy.absolute(a - v)).argmin()
        else:
            try:
                return scipy.digitize(v,(a[1:]+a[:-1])/2.0)
            except ValueError:
                return scipy.digitize(scipy.atleast_1d(v),(a[1:]+a[:-1])/2.0).reshape(())

            

    def _getFluxBiSpline(self, idx):
        """Gets the spline corresponding to the given time index, generating as needed.
        
        This returns a bivariate spline for when the instance is created with
        keyword tspline=False.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Returns:
            An instance of scipy.interpolate.RectBivariateSpline corresponding
                to the given time index idx.
        """
        try:
            return self._psiOfRZSpline[idx]
        except KeyError:
            # Note the order of the arguments -- psiRZ is stored with t along
            # the first dimension, Z along the second and R along the third.
            # This leads to intuitive behavior when contour plotting, but
            # mandates the syntax here.
            self._psiOfRZSpline[idx] = scipy.interpolate.RectBivariateSpline(
                self.getZGrid(length_unit='m'),
                self.getRGrid(length_unit='m'),
                self.getFluxGrid()[idx, :, :]
            )
            return self._psiOfRZSpline[idx]

    def _getFluxTriSpline(self):
        """Gets the tricubic interpolating spline for the flux.
        
        This is for use when the instance is created with keyword tspline=True.
        
        Returns:
            trispline.spline to give the flux as a function of R, Z and t.
        """
        if self._psiOfRZSpline:
            return self._psiOfRZSpline
        else:
            self._psiOfRZSpline = trispline.Spline(self.getTimeBase(),
                                                   self.getZGrid(length_unit='m'),
                                                   self.getRGrid(length_unit='m'),
                                                   self.getFluxGrid())
            return self._psiOfRZSpline

    def _getPhiNormSpline(self, idx, kind='cubic'):
        """Get spline to convert psinorm to phinorm.
        
        Returns the spline object corresponding to the passed time index idx,
        generating it if it does not already exist.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to phinorm. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d or tripline.RectBivariateSpline depending
                on whether or not the instance was created with the tspline
                keyword.
        """
        if not self._tricubic:
            try:
                return self._phiNormSpline[idx][kind]
            except KeyError:
                # Insert zero at beginning because older versions of cumtrapz don't
                # support the initial keyword to make the initial value zero:
                phi_norm_meas = scipy.insert(
                    scipy.integrate.cumtrapz(self.getQProfile()[idx]),
                    0,
                    0
                )
                phi_norm_meas = phi_norm_meas / phi_norm_meas[-1]

                spline = scipy.interpolate.interp1d(
                    scipy.linspace(0, 1, len(phi_norm_meas)),
                    phi_norm_meas,
                    kind=kind,
                    bounds_error=False
                )
                try:
                    self._phiNormSpline[idx][kind] = spline
                except KeyError:
                    self._phiNormSpline[idx] = {kind: spline}
                return self._phiNormSpline[idx][kind]
        else:
            if self._phiNormSpline:
                return self._phiNormSpline
            else:
                # Insert zero at beginning because older versions of cumtrapz don't
                # support the initial keyword to make the initial value zero:
                phi_norm_meas = scipy.insert(scipy.integrate.cumtrapz(self.getQProfile(),axis=1), 0, 0, axis=1)
                phi_norm_meas = phi_norm_meas / phi_norm_meas[-1]
                self._phiNormSpline = trispline.RectBivariateSpline(self.getTimeBase(),
                                                                    scipy.linspace(0, 1, len(phi_norm_meas[:,0])),
                                                                    phi_norm_meas,
                                                                    bounds_error = False)
                return self._phiNormSpline
    
    def _getPhiNormToPsiNormSpline(self, idx, kind='cubic'):
        """Get spline to convert phinorm to psinorm.
        
        Returns the spline object corresponding to the passed time index idx,
        generating it if it does not already exist.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to phinorm. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d or tripline.RectBivariateSpline depending
                on whether or not the instance was created with the tspline
                keyword.
        """
        if not self._tricubic:
            try:
                return self._phiNormToPsiNormSpline[idx][kind]
            except KeyError:
                # Insert zero at beginning because older versions of cumtrapz don't
                # support the initial keyword to make the initial value zero:
                phi_norm_meas = scipy.insert(
                    scipy.integrate.cumtrapz(self.getQProfile()[idx]),
                    0,
                    0
                )
                phi_norm_meas = phi_norm_meas / phi_norm_meas[-1]

                spline = scipy.interpolate.interp1d(
                    phi_norm_meas,
                    scipy.linspace(0, 1, len(phi_norm_meas)),
                    kind=kind,
                    bounds_error=False
                )
                try:
                    self._phiNormToPsiNormSpline[idx][kind] = spline
                except KeyError:
                    self._phiNormToPsiNormSpline[idx] = {kind: spline}
                return self._phiNormToPsiNormSpline[idx][kind]
        else:
            if self._phiNormToPsiNormSpline:
                return self._phiNormToPsiNormSpline
            else:
                # Insert zero at beginning because older versions of cumtrapz don't
                # support the initial keyword to make the initial value zero:
                phi_norm_meas = scipy.insert(
                    scipy.integrate.cumtrapz(self.getQProfile(), axis=1),
                    0,
                    0,
                    axis=1
                )
                phi_norm_meas = phi_norm_meas / phi_norm_meas[-1]
                # TODO: Ian, did I do this right?
                # I had to take out the bounds error...
                t_grid, psinorm_grid = scipy.meshgrid(
                    self.getTimeBase(),
                    scipy.linspace(0, 1, len(phi_norm_meas[:, 0]))
                )
                self._phiNormToPsiNormSpline = scipy.interpolate.SmoothBivariateSpline(
                    t_grid.ravel(),  
                    phi_norm_meas.ravel(),
                    psinorm_grid.ravel(),
                    # bounds_error = False
                )
                return self._phiNormToPsiNormSpline
    
    def _getVolNormSpline(self, idx, kind='cubic'):
        """Get spline to convert psinorm to volnorm.
        
        Returns the spline object corresponding to the passed time index idx,
        generating it if it does not already exist.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to volnorm. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d or tripline.RectBivariateSpline depending
                on whether or not the instance was created with the tspline
                keyword.
        """
        if not self._tricubic:
            try:
                return self._volNormSpline[idx][kind]
            except KeyError:
                vol_norm_meas = self.getFluxVol()[idx]
                vol_norm_meas = vol_norm_meas / vol_norm_meas[-1]

                spline = scipy.interpolate.interp1d(scipy.linspace(0, 1, len(vol_norm_meas)),
                                                    vol_norm_meas,
                                                    kind=kind,
                                                    bounds_error=False)
                try:
                    self._volNormSpline[idx][kind] = spline
                except KeyError:
                    self._volNormSpline[idx] = {kind: spline}
                return self._volNormSpline[idx][kind]
        else:
            #BiSpline for time variant interpolation
            if self._volNormSpline:
                return self._volNormSpline
            else:
                vol_norm_meas = self.getFluxVol()
                vol_norm_meas = vol_norm_meas / vol_norm_meas[-1]
                self._volNormSpline = trispline.RectBivariateSpline(self.getTimeBase(),
                                                                    scipy.linspace(0, 1, len(vol_norm_meas[:,0])),
                                                                    vol_norm_meas,
                                                                    bounds_error = False)
                return self._volNormSpline
    
    def _getVolNormToPsiNormSpline(self, idx, kind='cubic'):
        """Get spline to convert volnorm to psinorm.
        
        Returns the spline object corresponding to the passed time index idx,
        generating it if it does not already exist.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to volnorm. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d or tripline.RectBivariateSpline depending
                on whether or not the instance was created with the tspline
                keyword.
        """
        if not self._tricubic:
            try:
                return self._volNormToPsiNormSpline[idx][kind]
            except KeyError:
                vol_norm_meas = self.getFluxVol()[idx]
                vol_norm_meas = vol_norm_meas / vol_norm_meas[-1]
                
                spline = scipy.interpolate.interp1d(
                    vol_norm_meas,
                    scipy.linspace(0, 1, len(vol_norm_meas)),
                    kind=kind,
                    bounds_error=False
                )
                try:
                    self._volNormToPsiNormSpline[idx][kind] = spline
                except KeyError:
                    self._volNormToPsiNormSpline[idx] = {kind: spline}
                return self._volNormToPsiNormSpline[idx][kind]
        else:
            #BiSpline for time variant interpolation
            if self._volNormToPsiNormSpline:
                return self._volNormToPsiNormSpline
            else:
                vol_norm_meas = self.getFluxVol()
                vol_norm_meas = vol_norm_meas / vol_norm_meas[-1]
                
                t_grid, psinorm_grid = scipy.meshgrid(
                    self.getTimeBase(),
                    scipy.linspace(0, 1, len(vol_norm_meas[:, 0]))
                )
                # TODO: Ian, did I do this right?
                # I had to take out the bounds error...
                self._volNormToPsiNormSpline = scipy.interpolate.SmoothBivariateSpline(
                    t_grid.ravel(),
                    vol_norm_meas.ravel(),
                    psinorm_grid.ravel(),
                    # bounds_error = False
                )
                return self._volNormToPsiNormSpline
                                                                        
    def _getRmidSpline(self, idx, kind='cubic'):
        """Returns the spline object corresponding to the passed time index idx,
        generating it if it does not already exist.

        There are two approaches that come to mind:
            -- In Steve Wolfe's implementation of efit_rz2mid and efit_psi2rmid,
                he uses the EFIT output Rmid as a function of normalized flux
                (i.e., what is returned by self.getRmidPsi()) in the core, then
                expands the grid beyond this manually.
            -- A simpler approach would be to just compute the psi_norm(R_mid)
                grid directly from the radial grid.

        The latter approach is selected for simplicity.
        
        The units of R_mid are always meters, and are converted by the wrapper
        functions to whatever the user wants.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from psinorm to R_mid. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d or tripline.RectBivariateSpline depending
                on whether or not the instance was created with the tspline
                keyword.
        """
        if not self._tricubic:
            try:
                return self._RmidSpline[idx][kind]
            except KeyError:
                # New approach: create a fairly dense radial grid from the global
                # flux grid to avoid 1d interpolation problems in the core. The
                # bivariate spline seems to be a little more robust in this respect.
                resample_factor = 3
                R_grid = scipy.linspace(self.getMagR(length_unit='m')[idx],
                                        self.getRGrid(length_unit='m')[-1],
                                        resample_factor * len(self.getRGrid(length_unit='m')))

                psi_norm_on_grid = self.rz2psinorm(R_grid,
                                                   self.getMagZ(length_unit='m')[idx] * scipy.ones(R_grid.shape),
                                                   self.getTimeBase()[idx])

                spline = scipy.interpolate.interp1d(psi_norm_on_grid,
                                                    R_grid,
                                                    kind=kind,
                                                    bounds_error=False)
                try:
                    self._RmidSpline[idx][kind] = spline
                except KeyError:
                    self._RmidSpline[idx] = {kind: spline}
                return self._RmidSpline[idx][kind]
        else:
            if self._RmidSpline:
                return self._RmidSpline
            else:
                resample_factor = 3 * len(self.getRGrid(length_unit='m'))

                # generate timebase and R_grid through a meshgrid
                t, R_grid = scipy.meshgrid(self.getTimeBase(),scipy.zeros((resample_factor,)))
                Z_grid = scipy.dot(scipy.ones((resample_factor,1)),
                                   scipy.atleast_2d(self.getMagZ(length_unit='m')))

                for idx in scipy.arange(self.getTimeBase().size):
                    R_grid[:,idx] = scipy.linspace(self.getMagR(length_unit='m')[idx],
                                                   self.getRGrid(length_unit='m')[-1],
                                                   resample_factor)

                psi_norm_on_grid = self.rz2psinorm(R_grid, Z_grid, t, each_t=False)
                    
                self._RmidSpline = scipy.interpolate.SmoothBivariateSpline(
                    t.flatten(),
                    psi_norm_on_grid.flatten(),
                    R_grid.flatten()
                )
            
                return self._RmidSpline
    
    def _getRmidToPsiNormSpline(self, idx, kind='cubic'):
        """Returns the spline object corresponding to the passed time index idx,
        generating it if it does not already exist.

        There are two approaches that come to mind:
            -- In Steve Wolfe's implementation of efit_rz2mid and efit_psi2rmid,
                he uses the EFIT output Rmid as a function of normalized flux
                (i.e., what is returned by self.getRmidPsi()) in the core, then
                expands the grid beyond this manually.
            -- A simpler approach would be to just compute the psi_norm(R_mid)
                grid directly from the radial grid.

        The latter approach is selected for simplicity.
        
        The units of R_mid are always meters, and are converted by the wrapper
        functions to whatever the user wants.
        
        Args:
            idx (Scalar int):
                The time index to retrieve the flux spline for.
                This is ASSUMED to be a valid index for the first dimension of
                self.getFluxGrid(), otherwise an IndexError will be raised.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from R_mid to psinorm. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d or tripline.RectBivariateSpline depending
                on whether or not the instance was created with the tspline
                keyword.
        """
        if not self._tricubic:
            try:
                return self._RmidToPsiNormSpline[idx][kind]
            except KeyError:
                # New approach: create a fairly dense radial grid from the global
                # flux grid to avoid 1d interpolation problems in the core. The
                # bivariate spline seems to be a little more robust in this respect.
                resample_factor = 3
                R_grid = scipy.linspace(self.getMagR(length_unit='m')[idx],
                                        self.getRGrid(length_unit='m')[-1],
                                        resample_factor * len(self.getRGrid(length_unit='m')))

                psi_norm_on_grid = self.rz2psinorm(R_grid,
                                                   self.getMagZ(length_unit='m')[idx] * scipy.ones(R_grid.shape),
                                                   self.getTimeBase()[idx])

                spline = scipy.interpolate.interp1d(R_grid,
                                                    psi_norm_on_grid,
                                                    kind=kind,
                                                    bounds_error=False)
                try:
                    self._RmidToPsiNormSpline[idx][kind] = spline
                except KeyError:
                    self._RmidToPsiNormSpline[idx] = {kind: spline}
                return self._RmidToPsiNormSpline[idx][kind]
        else:
            if self._RmidToPsiNormSpline:
                return self._RmidToPsiNormSpline
            else:
                resample_factor = 3 * len(self.getRGrid(length_unit='m'))

                #generate timebase and R_grid through a meshgrid
                t, R_grid = scipy.meshgrid(self.getTimeBase(), scipy.zeros((resample_factor,)))
                Z_grid = scipy.dot(scipy.ones((resample_factor, 1)),
                                   scipy.atleast_2d(self.getMagZ(length_unit='m')))

                for idx in scipy.arange(self.getTimeBase().size):
                    R_grid[:, idx] = scipy.linspace(self.getMagR(length_unit='m')[idx],
                                                   self.getRGrid(length_unit='m')[-1],
                                                   resample_factor)

                psi_norm_on_grid = self.rz2psinorm(R_grid, Z_grid, t, each_t=False)
                    
                self._RmidToPsiNormSpline = scipy.interpolate.SmoothBivariateSpline(
                    t.flatten(),                   
                    R_grid.flatten(),
                    psi_norm_on_grid.flatten()
                )
                
                return self._RmidToPsiNormSpline

    def _getPsi0Spline(self, kind='cubic'):
        """Gets the univariate spline to interpolate psi0 as a function of time.
        
        Only used if the instance was created with keyword tspline=True.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from t to psi0. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d to convert from t to psi0.
        """
        if self._psiOfPsi0Spline:
            return self._psiOfPsi0Spline
        else:

            try:
                self._psiOfPsi0Spline = scipy.interpolate.interp1d(self.getTimeBase(),
                                                                   self.getFluxAxis(),
                                                                   kind=kind,
                                                                   bounds_error=False)
            except ValueError:
                # created to allow for single time (such as gfiles) to properly call this method
                kind = 'zero'
                fill_value = self.getFluxAxis()
                self._psiOfPsi0Spline = scipy.interpolate.interp1d([0.],[0.],
                                                                   kind=kind,
                                                                   bounds_error=False,
                                                                   fill_value=fill_value)
          
                
            return self._psiOfPsi0Spline

    def _getLCFSPsiSpline(self, kind='cubic'):
        """Gets the univariate spline to interpolate psi_a as a function of time.
        
        Only used if the instance was created with keyword tspline=True.
        
        Keyword Args:
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from t to psi_a. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d to convert from t to psi_a.
        """
        if self._psiOfLCFSSpline:
            return self._psiOfLCFSSpline
        else:
            try:
                self._psiOfLCFSSpline = scipy.interpolate.interp1d(self.getTimeBase(),
                                                                   self.getFluxLCFS(),
                                                                   kind=kind,
                                                                   bounds_error=False)
            except ValueError:
                # created to allow for single time (such as gfiles) to properly call this method
                kind = 'zero'
                fill_value = self.getFluxLCFS()
                self._psiOfLCFSSpline = scipy.interpolate.interp1d([0.],[0.],
                                                                   kind=kind,
                                                                   bounds_error=False,
                                                                   fill_value=fill_value)
          

            return self._psiOfLCFSSpline

    def getMagRSpline(self, length_unit=1, kind='nearest'):
        """Gets the univariate spline to interpolate R_mag as a function of time.
        
        Only used if the instance was created with keyword tspline=True.
        
        Keyword Args:
            length_unit (String or 1):
                Length unit that R_mag is returned in. If
                a string is given, it must be a valid unit specifier:
                    'm'         meters
                    'cm'        centimeters
                    'mm'        millimeters
                    'in'        inches
                    'ft'        feet
                    'yd'        yards
                    'smoot'     smoots
                    'cubit'     cubits
                    'hand'      hands
                    'default'   meters
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (R_out returned in meters).
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from t to R_mag. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d to convert from t to R_mid.
        """
        if self._magRSpline:
            return self._magRSpline
        else:
            if kind == 'nearest' and self._tricubic:
                kind = 'cubic'

            try:
                self._magRSpline = scipy.interpolate.interp1d(self.getTimeBase(),
                                                              self.getMagR(length_unit=length_unit),
                                                              kind=kind,
                                                              bounds_error=False)
            except ValueError:
                # created to allow for single time (such as gfiles) to properly call this method
                kind = 'zero'
                fill_value = self.getMagR(length_unit=length_unit)
                self._magRSpline = scipy.interpolate.interp1d([0.],[0.],
                                                                   kind=kind,
                                                                   bounds_error=False,
                                                                   fill_value=fill_value)
                
            return self._magRSpline

    def getMagZSpline(self, length_unit=1, kind='nearest'):
        """Gets the univariate spline to interpolate Z_mag as a function of time.
        
        Generated for completeness of the core position calculation when using
        tspline = True
        
        Keyword Args:
            length_unit (String or 1):
                Length unit that R_mag is returned in. If
                a string is given, it must be a valid unit specifier:
                    'm'         meters
                    'cm'        centimeters
                    'mm'        millimeters
                    'in'        inches
                    'ft'        feet
                    'yd'        yards
                    'smoot'     smoots
                    'cubit'     cubits
                    'hand'      hands
                    'default'   meters
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (R_out returned in meters).
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from t to R_mag. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d to convert from t to R_mid.
        """
        if self._magZSpline:
            return self._magZSpline
        else:
            if kind == 'nearest' and self._tricubic:
                kind = 'cubic'

            try:
                self._magZSpline = scipy.interpolate.interp1d(self.getTimeBase(),
                                                              self.getMagZ(length_unit=length_unit),
                                                              kind=kind,
                                                              bounds_error=False)

            except ValueError:
                # created to allow for single time (such as gfiles) to properly call this method
                kind = 'zero'
                fill_value = self.getMagZ(length_unit=length_unit)
                self._magZSpline = scipy.interpolate.interp1d([0.],[0.],
                                                              kind=kind,
                                                              bounds_error=False,
                                                              fill_value=fill_value)
                

            return self._magZSpline
    
    def getRmidOutSpline(self, length_unit=1, kind='nearest'):
        """Gets the univariate spline to interpolate R_mid_out as a function of time.
        
        Generated for completeness of the core position calculation when using
        tspline = True
        
        Keyword Args:
            length_unit (String or 1):
                Length unit that R_mag is returned in. If
                a string is given, it must be a valid unit specifier:
                    'm'         meters
                    'cm'        centimeters
                    'mm'        millimeters
                    'in'        inches
                    'ft'        feet
                    'yd'        yards
                    'smoot'     smoots
                    'cubit'     cubits
                    'hand'      hands
                    'default'   meters
                If length_unit is 1 or None, meters are assumed. The default
                value is 1 (R_out returned in meters).
            kind (String or non-negative int):
                Specifies the type of interpolation
                to be performed in getting from t to R_mag. This is
                passed to scipy.interpolate.interp1d. Valid options are:
                'linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic'
                If this keyword is an integer, it specifies the order of spline
                to use. See the documentation for interp1d for more details.
                Default value is 'cubic' (3rd order spline interpolation). On
                some builds of scipy, this can cause problems, in which case
                you should try 'linear' until you can rebuild your scipy install.
        
        Returns:
            scipy.interpolate.interp1d to convert from t to R_mid.
        """
        if self._RmidOutSpline:
            return self._RmidOutSpline
        else:
            if kind == 'nearest' and self._tricubic:
                kind = 'cubic'

            try:
                self._RmidOutSpline = scipy.interpolate.interp1d(self.getTimeBase(),
                                                                 self.getRmidOut(length_unit=length_unit),
                                                                 kind=kind,
                                                                 bounds_error=False)
            except ValueError:
                # created to allow for single time (such as gfiles) to properly call this method
                kind = 'zero'
                fill_value = self.getRmidOut(length_unit=length_unit)
                self._RmidOutSpline = scipy.interpolate.interp1d([0.],[0.],
                                                                 kind=kind,
                                                                 bounds_error=False,
                                                                 fill_value=fill_value)
                


            return self._RmidOutSpline

    def getInfo(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns namedtuple of instance parameters (shot, equilibrium type, size, timebase, etc.)
        """
        raise NotImplementedError()

    def getTimeBase(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns timebase array [t]
        """
        raise NotImplementedError()

    def getFluxGrid(self):
        """
        Abstract method.  See child classes for implementation.
        
        returns 3D grid of psi(r,z,t)
         The array returned should have the following dimensions:
           First dimension: time
           Second dimension: Z
           Third dimension: R
        """
        raise NotImplementedError()

    def getRGrid(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns vector of R-values for psiRZ grid [r]
        """
        raise NotImplementedError()

    def getZGrid(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns vector of Z-values for psiRZ grid [z]
        """
        raise NotImplementedError()

    def getFluxAxis(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns psi at magnetic axis [t]
        """
        raise NotImplementedError()

    def getFluxLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns psi a separatrix [t]
        """
        raise NotImplementedError()

    def getRLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns R-positions (n points) mapping LCFS [t,n]
        """
        raise NotImplementedError()

    def getZLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns Z-positions (n points) mapping LCFS [t,n]
        """
        raise NotImplementedError()
        
    def remapLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Overwrites stored R,Z positions of LCFS with explicitly calculated psinorm=1
        surface.  This surface is then masked using core.inPolygon() to only draw within
        vacuum vessel, the end result replacing RLCFS, ZLCFS with an R,Z array showing
        the divertor legs of the flux surface in addition to the core-enclosing closed
        flux surface.
        """
        raise NotImplementedError()

    def getFluxVol(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns volume contained within flux surface as function of psi [psi,t].
        Psi assumed to be evenly-spaced grid on [0,1]
        """
        raise NotImplementedError()

    def getVolLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns plasma volume within LCFS [t]
        """
        raise NotImplementedError()

    def getRmidPsi(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns outboard-midplane major radius of flux surface [t,psi]
        """
        raise NotImplementedError()

    def getF(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns F=RB_{\Phi}(\Psi), often calculated for grad-shafranov solutions  [psi,t]
        """
        raise NotImplementedError()
    
    def getFluxPres(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated pressure profile [psi,t].
        Psi assumed to be evenly-spaced grid on [0,1]
        """
        raise NotImplementedError()

    def getFFPrime(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns FF' function used for grad-shafranov solutions [psi,t]
        """
        raise NotImplementedError()

    def getPPrime(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns plasma pressure gradient as a function of psi [psi,t]
        """
        raise NotImplementedError()

    def getElongation(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns LCFS elongation [t]
        """
        raise NotImplementedError()

    def getUpperTriangularity(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns LCFS upper triangularity [t]
        """
        raise NotImplementedError()

    def getLowerTriangularity(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns LCFS lower triangularity [t]
        """
        raise NotImplementedError()

    def getShaping(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns dimensionless shaping parameters for plasma.
        Namedtuple containing {LCFS elongation, LCFS upper/lower triangularity}
        """
        raise NotImplementedError()

    def getMagR(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns magnetic-axis major radius [t]
        """
        raise NotImplementedError()

    def getMagZ(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns magnetic-axis Z [t]
        """
        raise NotImplementedError()

    def getAreaLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns LCFS surface area [t]
        """
        raise NotImplementedError()

    def getAOut(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns outboard-midplane minor radius [t]
        """
        raise NotImplementedError()

    def getRmidOut(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns outboard-midplane major radius [t]
        """
        raise NotImplementedError()

    def getGeometry(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns dimensional geometry parameters
        Namedtuple containing {mag axis R,Z, LCFS area, volume, outboard-midplane major radius}
        """
        raise NotImplementedError()

    def getQProfile(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns safety factor q profile [psi,t]
        Psi assumed to be evenly-spaced grid on [0,1]
        """
        raise NotImplementedError()

    def getQ0(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns q on magnetic axis [t]
        """
        raise NotImplementedError()

    def getQ95(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns q on 95% flux surface [t]
        """
        raise NotImplementedError()

    def getQLCFS(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns q on LCFS [t]
        """
        raise NotImplementedError()

    def getQ1Surf(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns outboard-midplane minor radius of q=1 surface [t]
        """
        raise NotImplementedError()
    
    def getQ2Surf(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns outboard-midplane minor radius of q=2 surface [t]
        """
        raise NotImplementedError()

    def getQ3Surf(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns outboard-midplane minor radius of q=3 surface [t]
        """
        raise NotImplementedError()

    def getQs(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns specific q-profile values.
        Namedtuple containing {q0, q95, qLCFS, minor radius of q=1,2,3 surfaces}
        """
        raise NotImplementedError()

    def getBtVac(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns vacuum on-axis toroidal field [t]
        """
        raise NotImplementedError()

    def getBtPla(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns plasma on-axis toroidal field [t]
        """
        raise NotImplementedError()

    def getBpAvg(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns average poloidal field [t]
        """
        raise NotImplementedError() 

    def getFields(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns magnetic-field values.
        Namedtuple containing {Btor on magnetic axis (plasma and vacuum), avg Bpol}
        """
        raise NotImplementedError()

    def getIpCalc(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated plasma current [t]
        """
        raise NotImplementedError()

    def getIpMeas(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns measured plasma current [t]
        """
        raise NotImplementedError()

    def getJp(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns grid of calculated toroidal current density [t,z,r]
        """
        raise NotImplementedError()

    def getBetaT(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated global toroidal beta [t]
        """
        raise NotImplementedError()

    def getBetaP(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated global poloidal beta [t]
        """
        raise NotImplementedError()

    def getLi(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated internal inductance of plasma [t]
        """
        raise NotImplementedError()

    def getBetas(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated betas and inductance.
        Namedtuple of {betat,betap,Li}
        """
        raise NotImplementedError()

    def getDiamagFlux(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns diamagnetic flux [t]
        """
        raise NotImplementedError()

    def getDiamagBetaT(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns diamagnetic-loop toroidal beta [t]
        """
        raise NotImplementedError()

    def getDiamagBetaP(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns diamagnetic-loop poloidal beta [t]
        """
        raise NotImplementedError()

    def getDiamagTauE(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns diamagnetic-loop energy confinement time [t]
        """
        raise NotImplementedError()

    def getDiamagWp(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns diamagnetic-loop plasma stored energy [t]
        """
        raise NotImplementedError()

    def getDiamag(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns diamagnetic measurements of plasma parameters.
        Namedtuple of {diamag. flux, betat, betap from coils, tau_E from diamag., diamag. stored energy}
        """
        raise NotImplementedError()

    def getWMHD(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated MHD stored energy [t]
        """
        raise NotImplementedError()

    def getTauMHD(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated MHD energy confinement time [t]
        """
        raise NotImplementedError()

    def getPinj(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated injected power [t]
        """
        raise NotImplementedError()

    def getCurrentSign(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated current direction, where CCW = +
        """
        raise NotImplementedError()

    def getWbdot(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated d/dt of magnetic stored energy [t]
        """
        raise NotImplementedError()

    def getWpdot(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns calculated d/dt of plasma stored energy [t]
        """
        raise NotImplementedError()

    def getEnergy(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns stored-energy parameters.
        Namedtuple of {stored energy, confinement time, injected power, d/dt of magnetic, plasma stored energy}
        """
        raise NotImplementedError()

    def getParam(self,path):
        """
        Abstract method.  See child classes for implementation.
        
        Backup function: takes parameter name for variable, returns variable directly.
        Acts as wrapper to direct data-access routines from within object.
        """
        #backup function - takes parameter name for EFIT variable, returns that variable
        #acts as wrapper for EFIT tree access from within object
        raise NotImplementedError()

    def getMachineCrossSection(self):
        """
        Abstract method.  See child classes for implementation.

        Returns (R,Z) coordinates of vacuum wall cross-section for plotting/masking routines.
        """
        raise NotImplementedError()

    def getMachineCrossSectionFull(self):
        """
        Abstract method.  See child classes for implementation.
        
        Returns (R,Z) coordinates of machine wall cross-section for plotting routines.
        Returns a more detailed cross-section than getLimiter(), generally a vector map
        displaying non-critical cross-section information.  If this is unavailable, this
        should point to self.getMachineCrossSection(), which pulls the limiter outline
        stored by default in data files e.g. g-eqdsk files.
        """
        raise NotImplementedError("function to return machine cross-section not implemented for this class yet!")

    def gfile(self, time=None, nw=None, nh=None, shot=None, name=None, tunit='ms', title='EQTOOLS'):
        filewriter.gfile(self,
                         time,
                         nw=nw,
                         nh=nh,
                         shot=shot,
                         name=name,
                         tunit=tunit,
                         title=title)

    def plotFlux(self,fill=True,mask=True):
        """Plots flux contours directly from psi grid.
        
        Keyword Args:
            fill (Boolean):
                Set True to plot filled contours.  Set False (default) to plot white-background
                color contours.
        """
        
        try:
            psiRZ = self.getFluxGrid()
            rGrid = self.getRGrid(length_unit='m')
            zGrid = self.getZGrid(length_unit='m')
            t = self.getTimeBase()

            RLCFS = self.getRLCFS(length_unit='m')
            ZLCFS = self.getZLCFS(length_unit='m')
        except ValueError:
            raise AttributeError('cannot plot EFIT flux map.')
        try:
            limx, limy = self.getMachineCrossSection()
        except NotImplementedError:
            if self._verbose:
                print('No machine cross-section implemented!')
            limx = None
            limy = None
        try:
            macx, macy = self.getMachineCrossSectionFull()
        except:
            macx = None
            macy = None

        #event handler for arrow key events in plot windows.  Pass slider object
        #to update as masked argument using lambda function
        #lambda evt: arrow_respond(my_slider,evt)
        def arrowRespond(slider,event):
            if event.key == 'right':
                slider.set_val(min(slider.val+1, slider.valmax))
            if event.key == 'left':
                slider.set_val(max(slider.val-1, slider.valmin))

        #make time-slice window
        fluxPlot = plt.figure(figsize=(6,11))
        gs = mplgs.GridSpec(2,1,height_ratios=[30,1])
        psi = fluxPlot.add_subplot(gs[0,0])
        psi.set_aspect('equal')
        timeSliderSub = fluxPlot.add_subplot(gs[1,0])
        title = fluxPlot.suptitle('')

        # dummy plot to get x,ylims
        psi.contour(rGrid,zGrid,psiRZ[0],1)

        # generate graphical mask for limiter wall
        if mask:
            xlim = psi.get_xlim()
            ylim = psi.get_ylim()
            bound_verts = [(xlim[0],ylim[0]),(xlim[0],ylim[1]),(xlim[1],ylim[1]),(xlim[1],ylim[0]),(xlim[0],ylim[0])]
            poly_verts = [(limx[i],limy[i]) for i in range(len(limx) - 1, -1, -1)]

            bound_codes = [mpath.Path.MOVETO] + (len(bound_verts) - 1) * [mpath.Path.LINETO]
            poly_codes = [mpath.Path.MOVETO] + (len(poly_verts) - 1) * [mpath.Path.LINETO]

            path = mpath.Path(bound_verts + poly_verts, bound_codes + poly_codes)
            patch = mpatches.PathPatch(path,facecolor='white',edgecolor='none')

        def updateTime(val):
            psi.clear()
            t_idx = int(timeSlider.val)

            title.set_text('EFIT Reconstruction, $t = %(t).2f$ s' % {'t':t[t_idx]})
            psi.set_xlabel('$R$ [m]')
            psi.set_ylabel('$Z$ [m]')
            if macx is not None:
                psi.plot(macx,macy,'k',linewidth=3,zorder=5)
            elif limx is not None:
                psi.plot(limx,limy,'k',linewidth=3,zorder=5)
            # catch NaNs separating disjoint sections of R,ZLCFS in mask
            maskarr = scipy.where(scipy.logical_or(RLCFS[:,t_idx] > 0.0,scipy.isnan(RLCFS[:,t_idx])))
            RLCFSframe = RLCFS[maskarr[0],t_idx]
            ZLCFSframe = ZLCFS[maskarr[0],t_idx]
            psi.plot(RLCFSframe,ZLCFSframe,'r',linewidth=3,zorder=3)
            if fill:
                psi.contourf(rGrid,zGrid,psiRZ[t_idx],50,zorder=2)
                psi.contour(rGrid,zGrid,psiRZ[t_idx],50,colors='k',linestyles='solid',zorder=3)
            else:
                psi.contour(rGrid,zGrid,psiRZ[t_idx],50,linestyles='solid',zorder=2)
            if mask:
                patchdraw = psi.add_patch(patch)
                patchdraw.set_zorder(4)
            fluxPlot.canvas.draw()

        timeSlider = mplw.Slider(timeSliderSub,'t index',0,len(t)-1,valinit=0,valfmt="%d")
        timeSlider.on_changed(updateTime)
        updateTime(0)

        plt.ion()
        fluxPlot.show()

        fluxPlot.canvas.mpl_connect('key_press_event', lambda evt: arrowRespond(timeSlider, evt))
