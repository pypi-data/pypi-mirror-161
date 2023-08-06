import sys
import typing
import bpy.types


def brush_stroke(stroke: typing.Union[
        typing.Dict[str, 'bpy.types.OperatorStrokeElement'], typing.
        List['bpy.types.OperatorStrokeElement'], 'bpy_prop_collection'] = None,
                 mode: typing.Union[str, int] = 'NORMAL'):
    ''' Sculpt curves using a brush

    :param stroke: Stroke
    :type stroke: typing.Union[typing.Dict[str, 'bpy.types.OperatorStrokeElement'], typing.List['bpy.types.OperatorStrokeElement'], 'bpy_prop_collection']
    :param mode: Stroke Mode, Action taken when a paint stroke is made * NORMAL Regular -- Apply brush normally. * INVERT Invert -- Invert action of brush for duration of stroke. * SMOOTH Smooth -- Switch brush to smooth mode for duration of stroke.
    :type mode: typing.Union[str, int]
    '''

    pass


def min_distance_edit():
    ''' Change the minimum distance used by the density brush

    '''

    pass


def select_all(action: typing.Union[str, int] = 'TOGGLE'):
    ''' (De)select all control points

    :param action: Action, Selection action to execute * TOGGLE Toggle -- Toggle selection for all elements. * SELECT Select -- Select all elements. * DESELECT Deselect -- Deselect all elements. * INVERT Invert -- Invert selection of all elements.
    :type action: typing.Union[str, int]
    '''

    pass


def select_end(end_points: bool = True, amount: int = 1):
    ''' Select end points of curves

    :param end_points: End Points, Select points at the end of the curve as opposed to the beginning
    :type end_points: bool
    :param amount: Amount, Number of points to select
    :type amount: int
    '''

    pass


def select_grow(distance: float = 0.1):
    ''' Select curves which are close to curves that are selected already

    :param distance: Distance, By how much to grow the selection
    :type distance: float
    '''

    pass


def select_random(seed: int = 0,
                  partial: bool = False,
                  probability: float = 0.5,
                  min: float = 0.0,
                  constant_per_curve: bool = True):
    ''' Randomizes existing selection or create new random selection

    :param seed: Seed, Source of randomness
    :type seed: int
    :param partial: Partial, Allow points or curves to be selected partially
    :type partial: bool
    :param probability: Probability, Chance of every point or curve being included in the selection
    :type probability: float
    :param min: Min, Minimum value for the random selection
    :type min: float
    :param constant_per_curve: Constant per Curve, The generated random number is the same for every control point of a curve
    :type constant_per_curve: bool
    '''

    pass
