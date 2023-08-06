from marshmallow import fields, validate, Schema

from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import DisplayType, ProfileHistoryChangeType
from mobio.libs.profiling_mf.profiling_data.hobby_data import df_get_hobby_data
from mobio.libs.profiling_mf.profiling_schema import HobbySchema


class MergeHobby(BaseMerge):
    def serialize_data(
        self,
        suggest_data,
        profile_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_property,
        display_type,
        translate_key,
        predict=None
    ):
        lst_suggest = []
        profile_data = profile_data if profile_data is not None else []
        for a in profile_data:
            lst_suggest.append(self.__build_value__(value=a, suggest=True))
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.ACTIVITY,
            value=lst_suggest,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        pass

    def serialize_origin_data(
        self,
        suggest_data,
        origin_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_property,
        display_type,
        translate_key,
    ):
        lst_suggest = []
        profile_data = origin_data if origin_data is not None else []
        if isinstance(profile_data, str):
            try:
                arr_ids = list(map(lambda x: int(x), profile_data.split(";")))
            except Exception as ex:
                print("MERGE::HOBBY = {}".format(ex))
                arr_ids = []
        elif isinstance(profile_data, list):
            try:
                arr_ids = list(map(lambda x: int(x), profile_data))
            except Exception as ex:
                print("MERGE::HOBBY = {}".format(ex))
                arr_ids = []
        else:
            print("ERROR HOBBY: {} invalid".format(profile_data))
            arr_ids = []
        hobby_data = df_get_hobby_data()
        arr_hobby = list(filter(lambda x: x["id"] in arr_ids, hobby_data))
        arr_hobby = list(
            map(
                lambda x: CommonHelper.create_simple_data_type(
                    _id=x["id"], _name=x["name"]
                ),
                arr_hobby,
            )
        )
        for a in arr_hobby:
            lst_suggest.append(self.__build_value__(value=a, suggest=True))
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.ACTIVITY,
            value=lst_suggest,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
        if source_data:
            hobby_data = df_get_hobby_data()
            set_hobby = set([x.get("id") for x in target_data.get(self.field_key)]) if not is_master_data else set()
            set_hobby.update(
                [x.get("value").get("id") for x in source_data.get("field_value")]
            )
            arr_ids = list(set_hobby)
            arr_hobby = list(filter(lambda x: x["id"] in arr_ids, hobby_data))
            arr_hobby = list(
                map(
                    lambda x: CommonHelper.create_simple_data_type(
                        _id=x["id"], _name=x["name"]
                    ),
                    arr_hobby,
                )
            )
            target_data[self.field_key] = arr_hobby

    def validate_merge(self, data, schema_validate_value=None):
        schema_validate_value = {
            "changeable": fields.Boolean(
                default=True, missing=True, allow_none=False
            ),
            "suggest": fields.Boolean(default=True, missing=True, allow_none=False),
            "value": fields.Nested(HobbySchema),
            "status": fields.Int(default=None, allow_none=True),
            "predict": fields.Dict(allow_none=True)
        }
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
            "field_value": fields.List(fields.Nested(Schema.from_dict(schema_validate_value)))
        }

        generated_schema = Schema.from_dict(rules)
        return generated_schema().load(data)

    def normalized_value(self, data):
        return [x.get("id") for x in data.get(self.field_key, [])]

    def get_add_data(self, data):
        if not data:
            data = dict()
        result = []
        if data.get(ProfileHistoryChangeType.ADD):
            result = [x.get("id") for x in data.get(ProfileHistoryChangeType.ADD)]
        return result

    def get_remove_data(self, data):
        if not data:
            data = dict()
        result = []
        if data.get(ProfileHistoryChangeType.REMOVE):
            result = [x.get("id") for x in data.get(ProfileHistoryChangeType.REMOVE)]
        return result
