"""
    Pod API

    This document refers to Symphony API calls that do not need encryption or decryption of content.  - sessionToken can be obtained by calling the authenticationAPI on the symphony back end and the key manager respectively. Refer to the methods described in authenticatorAPI.yaml. - Actions are defined to be atomic, ie will succeed in their entirety or fail and have changed nothing. - If it returns a 40X status then it will have made no change to the system even if ome subset of the request would have succeeded. - If this contract cannot be met for any reason then this is an error and the response code will be 50X.   # noqa: E501

    The version of the OpenAPI document: 20.12.1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401
from typing import List

from symphony.bdk.gen.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
)

from symphony.bdk.gen.pod_model.faceted_match_count import FacetedMatchCount
from symphony.bdk.gen.pod_model.room_search_criteria import RoomSearchCriteria
from symphony.bdk.gen.pod_model.v2_room_detail import V2RoomDetail
globals()['FacetedMatchCount'] = FacetedMatchCount
globals()['RoomSearchCriteria'] = RoomSearchCriteria
globals()['V2RoomDetail'] = V2RoomDetail


class RoomSearchResults(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
    }

    validations = {
    }

    additional_properties_type = None

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a pod_model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'count': (int, none_type),  # noqa: E501
            'skip': (int, none_type),  # noqa: E501
            'limit': (int, none_type),  # noqa: E501
            'query': (RoomSearchCriteria, none_type),  # noqa: E501
            'rooms': ([V2RoomDetail], none_type),  # noqa: E501
            'faceted_match_count': ([FacetedMatchCount], none_type),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'count': 'count',  # noqa: E501
        'skip': 'skip',  # noqa: E501
        'limit': 'limit',  # noqa: E501
        'query': 'query',  # noqa: E501
        'rooms': 'rooms',  # noqa: E501
        'faceted_match_count': 'facetedMatchCount',  # noqa: E501
    }

    _composed_schemas = {}

    required_properties = set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):  # noqa: E501
        """RoomSearchResults - a pod_model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the pod_model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            count (int): The total number of rooms matched by the search.. [optional]  # noqa: E501
            skip (int): The number of skipped results.. [optional]  # noqa: E501
            limit (int): The number of returned results.. [optional]  # noqa: E501
            query (RoomSearchCriteria): [optional]  # noqa: E501
            rooms ([V2RoomDetail]): A list of rooms matched by the query.. [optional]  # noqa: E501
            faceted_match_count ([FacetedMatchCount]): Detailed counts of matched rooms per search criterion.. [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)
        self.count: int = None
        self.skip: int = None
        self.limit: int = None
        self.query: RoomSearchCriteria = None
        self.rooms: List[V2RoomDetail] = None
        self.faceted_match_count: List[FacetedMatchCount] = None
        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
