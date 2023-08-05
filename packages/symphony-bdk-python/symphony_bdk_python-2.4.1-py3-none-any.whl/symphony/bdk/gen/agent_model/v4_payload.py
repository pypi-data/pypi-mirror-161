"""
    Agent API

    This document refers to Symphony API calls to send and receive messages and content. They need the on-premise Agent installed to perform decryption/encryption of content.  - sessionToken and keyManagerToken can be obtained by calling the authenticationAPI on the symphony back end and the key manager respectively. Refer to the methods described in authenticatorAPI.yaml. - A new authorizationToken has been introduced in the authenticationAPI response payload. It can be used to replace the sessionToken in any of the API calls and can be passed as \"Authorization\" header. - Actions are defined to be atomic, ie will succeed in their entirety or fail and have changed nothing. - If it returns a 40X status then it will have sent no message to any stream even if a request to some subset of the requested streams would have succeeded. - If this contract cannot be met for any reason then this is an error and the response code will be 50X. - MessageML is a markup language for messages. See reference here: https://rest-api.symphony.com/docs/messagemlv2 - **Real Time Events**: The following events are returned when reading from a real time messages and events stream (\"datafeed\"). These events will be returned for datafeeds created with the v5 endpoints. To know more about the endpoints, refer to Create Messages/Events Stream and Read Messages/Events Stream. Unless otherwise specified, all events were added in 1.46.   # noqa: E501

    The version of the OpenAPI document: 22.5.1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401
from typing import List, Union

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
    OpenApiModel
)
from symphony.bdk.gen.exceptions import ApiAttributeError


from symphony.bdk.gen.agent_model.v4_connection_accepted import V4ConnectionAccepted
from symphony.bdk.gen.agent_model.v4_connection_requested import V4ConnectionRequested
from symphony.bdk.gen.agent_model.v4_instant_message_created import V4InstantMessageCreated
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_message_suppressed import V4MessageSuppressed
from symphony.bdk.gen.agent_model.v4_room_created import V4RoomCreated
from symphony.bdk.gen.agent_model.v4_room_deactivated import V4RoomDeactivated
from symphony.bdk.gen.agent_model.v4_room_member_demoted_from_owner import V4RoomMemberDemotedFromOwner
from symphony.bdk.gen.agent_model.v4_room_member_promoted_to_owner import V4RoomMemberPromotedToOwner
from symphony.bdk.gen.agent_model.v4_room_reactivated import V4RoomReactivated
from symphony.bdk.gen.agent_model.v4_room_updated import V4RoomUpdated
from symphony.bdk.gen.agent_model.v4_shared_post import V4SharedPost
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom
from symphony.bdk.gen.agent_model.v4_user_left_room import V4UserLeftRoom
from symphony.bdk.gen.agent_model.v4_user_requested_to_join_room import V4UserRequestedToJoinRoom
globals()['V4ConnectionAccepted'] = V4ConnectionAccepted
globals()['V4ConnectionRequested'] = V4ConnectionRequested
globals()['V4InstantMessageCreated'] = V4InstantMessageCreated
globals()['V4MessageSent'] = V4MessageSent
globals()['V4MessageSuppressed'] = V4MessageSuppressed
globals()['V4RoomCreated'] = V4RoomCreated
globals()['V4RoomDeactivated'] = V4RoomDeactivated
globals()['V4RoomMemberDemotedFromOwner'] = V4RoomMemberDemotedFromOwner
globals()['V4RoomMemberPromotedToOwner'] = V4RoomMemberPromotedToOwner
globals()['V4RoomReactivated'] = V4RoomReactivated
globals()['V4RoomUpdated'] = V4RoomUpdated
globals()['V4SharedPost'] = V4SharedPost
globals()['V4SymphonyElementsAction'] = V4SymphonyElementsAction
globals()['V4UserJoinedRoom'] = V4UserJoinedRoom
globals()['V4UserLeftRoom'] = V4UserLeftRoom
globals()['V4UserRequestedToJoinRoom'] = V4UserRequestedToJoinRoom

class V4Payload(ModelNormal):
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

    @cached_property
    def additional_properties_type():
        """
        This must be a method because a agent_model may have properties that are
        of type self, this must run after the class is loaded
        """
        return (bool, date, datetime, dict, float, int, list, str, none_type,)  # noqa: E501

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a agent_model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'message_sent': (V4MessageSent, none_type),  # noqa: E501
            'shared_post': (V4SharedPost, none_type),  # noqa: E501
            'instant_message_created': (V4InstantMessageCreated, none_type),  # noqa: E501
            'room_created': (V4RoomCreated, none_type),  # noqa: E501
            'room_updated': (V4RoomUpdated, none_type),  # noqa: E501
            'room_deactivated': (V4RoomDeactivated, none_type),  # noqa: E501
            'room_reactivated': (V4RoomReactivated, none_type),  # noqa: E501
            'user_joined_room': (V4UserJoinedRoom, none_type),  # noqa: E501
            'user_left_room': (V4UserLeftRoom, none_type),  # noqa: E501
            'room_member_promoted_to_owner': (V4RoomMemberPromotedToOwner, none_type),  # noqa: E501
            'room_member_demoted_from_owner': (V4RoomMemberDemotedFromOwner, none_type),  # noqa: E501
            'connection_requested': (V4ConnectionRequested, none_type),  # noqa: E501
            'connection_accepted': (V4ConnectionAccepted, none_type),  # noqa: E501
            'message_suppressed': (V4MessageSuppressed, none_type),  # noqa: E501
            'symphony_elements_action': (V4SymphonyElementsAction, none_type),  # noqa: E501
            'user_requested_to_join_room': (V4UserRequestedToJoinRoom, none_type),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'message_sent': 'messageSent',  # noqa: E501
        'shared_post': 'sharedPost',  # noqa: E501
        'instant_message_created': 'instantMessageCreated',  # noqa: E501
        'room_created': 'roomCreated',  # noqa: E501
        'room_updated': 'roomUpdated',  # noqa: E501
        'room_deactivated': 'roomDeactivated',  # noqa: E501
        'room_reactivated': 'roomReactivated',  # noqa: E501
        'user_joined_room': 'userJoinedRoom',  # noqa: E501
        'user_left_room': 'userLeftRoom',  # noqa: E501
        'room_member_promoted_to_owner': 'roomMemberPromotedToOwner',  # noqa: E501
        'room_member_demoted_from_owner': 'roomMemberDemotedFromOwner',  # noqa: E501
        'connection_requested': 'connectionRequested',  # noqa: E501
        'connection_accepted': 'connectionAccepted',  # noqa: E501
        'message_suppressed': 'messageSuppressed',  # noqa: E501
        'symphony_elements_action': 'symphonyElementsAction',  # noqa: E501
        'user_requested_to_join_room': 'userRequestedToJoinRoom',  # noqa: E501
    }

    read_only_vars = {
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, *args, **kwargs):  # noqa: E501
        """V4Payload - a agent_model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the agent_model in received_data
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
            message_sent (V4MessageSent): [optional]  # noqa: E501
            shared_post (V4SharedPost): [optional]  # noqa: E501
            instant_message_created (V4InstantMessageCreated): [optional]  # noqa: E501
            room_created (V4RoomCreated): [optional]  # noqa: E501
            room_updated (V4RoomUpdated): [optional]  # noqa: E501
            room_deactivated (V4RoomDeactivated): [optional]  # noqa: E501
            room_reactivated (V4RoomReactivated): [optional]  # noqa: E501
            user_joined_room (V4UserJoinedRoom): [optional]  # noqa: E501
            user_left_room (V4UserLeftRoom): [optional]  # noqa: E501
            room_member_promoted_to_owner (V4RoomMemberPromotedToOwner): [optional]  # noqa: E501
            room_member_demoted_from_owner (V4RoomMemberDemotedFromOwner): [optional]  # noqa: E501
            connection_requested (V4ConnectionRequested): [optional]  # noqa: E501
            connection_accepted (V4ConnectionAccepted): [optional]  # noqa: E501
            message_suppressed (V4MessageSuppressed): [optional]  # noqa: E501
            symphony_elements_action (V4SymphonyElementsAction): [optional]  # noqa: E501
            user_requested_to_join_room (V4UserRequestedToJoinRoom): [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        self = super(OpenApiModel, cls).__new__(cls)

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

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
        return self

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
        """V4Payload - a agent_model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the agent_model in received_data
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
            message_sent (V4MessageSent): [optional]  # noqa: E501
            shared_post (V4SharedPost): [optional]  # noqa: E501
            instant_message_created (V4InstantMessageCreated): [optional]  # noqa: E501
            room_created (V4RoomCreated): [optional]  # noqa: E501
            room_updated (V4RoomUpdated): [optional]  # noqa: E501
            room_deactivated (V4RoomDeactivated): [optional]  # noqa: E501
            room_reactivated (V4RoomReactivated): [optional]  # noqa: E501
            user_joined_room (V4UserJoinedRoom): [optional]  # noqa: E501
            user_left_room (V4UserLeftRoom): [optional]  # noqa: E501
            room_member_promoted_to_owner (V4RoomMemberPromotedToOwner): [optional]  # noqa: E501
            room_member_demoted_from_owner (V4RoomMemberDemotedFromOwner): [optional]  # noqa: E501
            connection_requested (V4ConnectionRequested): [optional]  # noqa: E501
            connection_accepted (V4ConnectionAccepted): [optional]  # noqa: E501
            message_suppressed (V4MessageSuppressed): [optional]  # noqa: E501
            symphony_elements_action (V4SymphonyElementsAction): [optional]  # noqa: E501
            user_requested_to_join_room (V4UserRequestedToJoinRoom): [optional]  # noqa: E501
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

        self.message_sent: V4MessageSent = None
        self.shared_post: V4SharedPost = None
        self.instant_message_created: V4InstantMessageCreated = None
        self.room_created: V4RoomCreated = None
        self.room_updated: V4RoomUpdated = None
        self.room_deactivated: V4RoomDeactivated = None
        self.room_reactivated: V4RoomReactivated = None
        self.user_joined_room: V4UserJoinedRoom = None
        self.user_left_room: V4UserLeftRoom = None
        self.room_member_promoted_to_owner: V4RoomMemberPromotedToOwner = None
        self.room_member_demoted_from_owner: V4RoomMemberDemotedFromOwner = None
        self.connection_requested: V4ConnectionRequested = None
        self.connection_accepted: V4ConnectionAccepted = None
        self.message_suppressed: V4MessageSuppressed = None
        self.symphony_elements_action: V4SymphonyElementsAction = None
        self.user_requested_to_join_room: V4UserRequestedToJoinRoom = None
        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
            if var_name in self.read_only_vars:
                raise ApiAttributeError(f"`{var_name}` is a read-only attribute. Use `from_openapi_data` to instantiate "
                                     f"class with read only attributes.")
