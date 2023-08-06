import sys
import typing


def attribute_add(name: str = "Attribute",
                  domain: typing.Union[int, str] = 'POINT',
                  data_type: typing.Union[int, str] = 'FLOAT'):
    ''' Add attribute to geometry

    :param name: Name, Name of new attribute
    :type name: str
    :param domain: Domain, Type of element that attribute is stored on
    :type domain: typing.Union[int, str]
    :param data_type: Data Type, Type of data stored in attribute
    :type data_type: typing.Union[int, str]
    '''

    pass


def attribute_convert(mode: typing.Union[int, str] = 'GENERIC',
                      domain: typing.Union[int, str] = 'POINT',
                      data_type: typing.Union[int, str] = 'FLOAT'):
    ''' Change how the attribute is stored

    :param mode: Mode
    :type mode: typing.Union[int, str]
    :param domain: Domain, Which geometry element to move the attribute to
    :type domain: typing.Union[int, str]
    :param data_type: Data Type
    :type data_type: typing.Union[int, str]
    '''

    pass


def attribute_remove():
    ''' Remove attribute from geometry

    '''

    pass


def color_attribute_add(name: str = "Color",
                        domain: typing.Union[int, str] = 'POINT',
                        data_type: typing.Union[int, str] = 'FLOAT_COLOR',
                        color: typing.List[float] = (0.0, 0.0, 0.0, 1.0)):
    ''' Add color attribute to geometry

    :param name: Name, Name of new color attribute
    :type name: str
    :param domain: Domain, Type of element that attribute is stored on
    :type domain: typing.Union[int, str]
    :param data_type: Data Type, Type of data stored in attribute
    :type data_type: typing.Union[int, str]
    :param color: Color, Default fill color
    :type color: typing.List[float]
    '''

    pass


def color_attribute_duplicate():
    ''' Duplicate color attribute

    '''

    pass


def color_attribute_remove():
    ''' Remove color attribute from geometry

    '''

    pass


def color_attribute_render_set(name: str = "Color"):
    ''' Set default color attribute used for rendering

    :param name: Name, Name of color attribute
    :type name: str
    '''

    pass
