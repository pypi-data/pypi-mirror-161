from abc import ABCMeta, abstractmethod

from marshmallow import Schema, fields, validate

from mobio.libs.profiling_mf.profiling_common import DynamicFieldProperty, DisplayType, DISPLAY_TYPE_IS_LIST_TYPE, \
    ProfileHistoryChangeType
from mobio.libs.profiling_mf.profiling_schema import SocialUserSchema, PushIdSchema, CardSchema


class MergeListGroup:
    INFORMATION = "information"
    DEMOGRAPHIC = "demographic"
    ACTIVITY = "activity"
    LOYALTY = "loyalty"
    OTHER = "other"
    DYNAMIC = "dynamic"


class BaseMerge(metaclass=ABCMeta):

    def __init__(self, field_key):
        self.field_key = field_key

    @staticmethod
    def build_merge_data(
        translate_key,
        field_property,
        display_type,
        displayable,
        editable,
        mergeable,
        order,
        group,
        value,
        tooltip_i18n=None
    ):
        return {
            "translate_key": translate_key,
            "tooltip_i18n": tooltip_i18n,
            "field_property": field_property,
            "display_type": display_type,
            "displayable": displayable,
            "editable": editable,
            "mergeable": mergeable,
            "order": order,
            "group": group,
            "field_value": value,
        }

    @abstractmethod
    def serialize_data(
        self,
        suggest_data,
        profile_data,
        set_suggest_fields,
        set_unique_suggest_values,
        # field_key,
        field_property,
        display_type,
        translate_key,
        predict=None
    ):
        pass

    @abstractmethod
    def set_filter_value(self, suggest_filter_data, profile_data):
        pass

    @abstractmethod
    def serialize_origin_data(
        self,
        suggest_data,
        origin_data,
        set_suggest_fields,
        set_unique_suggest_values,
        # field_key,
        field_property,
        display_type,
        translate_key,
    ):
        pass

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            suggest = source_data.get("field_value").get("suggest")
            value = source_data.get("field_value").get("value")
            if suggest and value is not None:
                target_data[self.field_key] = value

    def increase_trust_point(self, **kwargs):
        return 0

    def __build_value__(self, value, suggest=True, changealbe=True, predict=None):
        return {"value": value, "suggest": suggest, "changeable": changealbe, "predict": predict}

    def __validate_field_value__(self, field_property, validate_value=None):
        if not validate_value:
            if field_property in [
                DynamicFieldProperty.INTEGER,
                DynamicFieldProperty.GENDER,
                DynamicFieldProperty.UDT
            ]:
                validate_value = fields.Int(allow_none=True)
            elif field_property == DynamicFieldProperty.FLOAT:
                validate_value = fields.Float(allow_none=True)
            elif field_property == DynamicFieldProperty.DATETIME:
                validate_value = fields.DateTime(allow_none=True)
            elif field_property in [
                DynamicFieldProperty.STRING,
                DynamicFieldProperty.PHONE_NUMBER,
            ]:
                validate_value = fields.Str(allow_none=True)
            elif field_property == DynamicFieldProperty.DICT:
                validate_value = fields.Dict(allow_none=True)
            elif field_property == DynamicFieldProperty.EMAIL:
                validate_value = fields.Email(allow_none=True)
            elif field_property == DynamicFieldProperty.SOCIAL_USER:
                validate_value = fields.Nested(
                    SocialUserSchema, allow_none=True, missing=None, default=None
                )
            # elif field_property == DynamicFieldProperty.UDT:
            #     validate_value = fields.Nested(
            #         UdtSchema, allow_none=True, missing=None, default=None
            #     )
            elif field_property == DynamicFieldProperty.PUSH_ID:
                validate_value = fields.Nested(
                    PushIdSchema, allow_none=True, missing=None, default=None
                )
            elif field_property == DynamicFieldProperty.CARDS:
                validate_value = fields.Nested(
                    CardSchema, allow_none=True, missing=None, default=None
                )
        return Schema.from_dict(
            {
                "changeable": fields.Boolean(
                    default=True, missing=True, allow_none=False
                ),
                "suggest": fields.Boolean(default=True, missing=True, allow_none=False),
                "value": validate_value,
                "status": fields.Int(default=None, allow_none=True),
                "predict": fields.Dict(allow_none=True)
            }
        )

    def validate_merge(self, data, schema_validate_value=None):
        rules = {
            "display_type": fields.Str(
                validate=validate.OneOf([x.value for x in DisplayType])
            ),
            "displayable": fields.Boolean(),
            "editable": fields.Boolean(),
            "field_property": fields.Int(),
            "group": fields.Str(),
            "mergeable": fields.Boolean(),
            "order": fields.Int(),
            "tooltip_i18n": fields.Str(allow_none=True, missing=None, default=None),
            "translate_key": fields.Str(allow_none=True, missing=None, default=None),
        }
        if not schema_validate_value:
            display_type = data.get("display_type")
            field_property = data.get("field_property")
            if display_type in DISPLAY_TYPE_IS_LIST_TYPE:
                rules["field_value"] = fields.List(
                    fields.Nested(
                        self.__validate_field_value__(field_property=field_property)
                    )
                )
            else:
                rules["field_value"] = fields.Nested(
                    self.__validate_field_value__(field_property=field_property)
                )
        else:
            rules["field_value"] = schema_validate_value
        generated_schema = Schema.from_dict(rules)
        return generated_schema().load(data)

    def get_updated_data(self, data):
        if not data:
            data = dict()
        if data.get(ProfileHistoryChangeType.REMOVE):
            old_value = data.get(ProfileHistoryChangeType.REMOVE)[0]
        else:
            old_value = (
                data.get(ProfileHistoryChangeType.CHANGE)[0].get("from")
                if data.get(ProfileHistoryChangeType.CHANGE)
                else None
            )
        if data.get(ProfileHistoryChangeType.ADD):
            new_value = data.get(ProfileHistoryChangeType.ADD)[0]
        else:
            new_value = (
                data.get(ProfileHistoryChangeType.CHANGE)[0].get("to")
                if data.get(ProfileHistoryChangeType.CHANGE)
                else None
            )
        return old_value, new_value

    def get_add_data(self, data):
        if not data:
            data = dict()
        return data.get(ProfileHistoryChangeType.ADD) or []

    def get_remove_data(self, data):
        if not data:
            data = dict()
        return data.get(ProfileHistoryChangeType.REMOVE) or []

    # Function get data đã được chuẩn hóa, thường là data FE send lên
    def get_normalized_value(self, data):
        return data.get(self.field_key)

    # Function chuẩn hóa data để lưu vào satellite
    def normalized_value(self, data):
        return data.get(self.field_key)
