from marshmallow import Schema, fields, validate, ValidationError

from mobio.libs.profiling_mf import ProfileByIdentifyStructure
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import DisplayType, ProfileHistoryChangeType
from mobio.libs.profiling_mf.profiling_schema import ProfileByIdentifySchema


class MergeProfileIdentify(BaseMerge):
    def serialize_data(
        self,
        suggest_data,
        profile_data,
        set_suggest_fields,
        set_unique_suggest_values,
        field_property,
        display_type,
        translate_key,
        predict=None,
    ):
        lst_profile_identify = []
        profile_data = profile_data if profile_data is not None else []
        for profile_identify in profile_data:
            # profile_identify_unique_value = "{}:{}".format(
            #     profile_identify.get(ProfileByIdentifyStructure.IDENTIFY_TYPE),
            #     profile_identify.get(ProfileByIdentifyStructure.IDENTIFY_VALUE),
            # )
            # suggest_profile_identify = (
            #     True
            #     if profile_identify_unique_value not in set_unique_suggest_values
            #     else False
            # )
            # set_unique_suggest_values.add(profile_identify_unique_value)
            lst_profile_identify.append(
                self.__build_value__(
                    value=profile_identify,
                    suggest=True,
                    changealbe=False,
                    predict=predict,
                )
            )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_profile_identify,
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
        lst_profile_identify = []
        origin_data = origin_data if origin_data is not None else []
        for profile_identify in origin_data:
            # profile_identify_unique_value = "{}:{}".format(
            #     profile_identify.get(ProfileByIdentifyStructure.IDENTIFY_TYPE),
            #     profile_identify.get(ProfileByIdentifyStructure.IDENTIFY_VALUE),
            # )
            # suggest_profile_identify = (
            #     True
            #     if profile_identify_unique_value not in set_unique_suggest_values
            #     else False
            # )
            # set_unique_suggest_values.add(profile_identify_unique_value)
            lst_profile_identify.append(
                self.__build_value__(
                    value=profile_identify, suggest=True, changealbe=False
                )
            )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_profile_identify,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            # normalize data
            target_data[self.field_key] = (
                target_data.get(self.field_key)
                if target_data.get(self.field_key)
                else []
            )
            # set data is empty if is_master_data is True
            target_data[self.field_key] = (
                target_data.get(self.field_key) if not is_master_data else []
            )
            for source_identify in source_data.get("field_value"):
                suggest = source_identify.get("suggest")
                if suggest:
                    profile_identify = ProfileByIdentifySchema().load(
                        source_identify.get("value")
                    )

                    exists_identify = next(
                        (
                            x
                            for x in target_data.get(self.field_key)
                            if x.get(ProfileByIdentifyStructure.IDENTIFY_TYPE)
                            == profile_identify.get(
                                ProfileByIdentifyStructure.IDENTIFY_TYPE
                            )
                            and x.get(ProfileByIdentifyStructure.IDENTIFY_VALUE)
                            == profile_identify.get(
                                ProfileByIdentifyStructure.IDENTIFY_VALUE
                            )
                        ),
                        None,
                    )
                    if not exists_identify:
                        target_data[self.field_key].append(profile_identify)

    def validate_merge(self, data, schema_validate_value=None):
        schema_validate_value = {
            "changeable": fields.Boolean(default=True, missing=True, allow_none=False),
            "suggest": fields.Boolean(default=True, missing=True, allow_none=False),
            "value": fields.Nested(ProfileByIdentifySchema),
            "status": fields.Int(default=None, allow_none=True),
            "predict": fields.Dict(allow_none=True),
        }
        field_value = data.get("field_value", [])
        tmp_field_value = []
        for value in field_value:
            generated_schema_value = Schema.from_dict(schema_validate_value)
            try:
                valid_value = generated_schema_value().load(value)
                tmp_field_value.append(valid_value)
            except ValidationError as ex:
                print(
                    "MergeProfileIdentify:: validation value error: {}".format(ex)
                )
        data["field_value"] = tmp_field_value
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
            "field_value": fields.List(
                fields.Nested(Schema.from_dict(schema_validate_value))
            ),
        }

        generated_schema = Schema.from_dict(rules)
        return generated_schema().load(data)

    def normalized_value(self, data):
        return [
            "{identify_type}::{identify_value}".format(
                identify_type=x.get(ProfileByIdentifyStructure.IDENTIFY_TYPE),
                identify_value=x.get(ProfileByIdentifyStructure.IDENTIFY_VALUE),
            )
            for x in data.get(self.field_key, [])
        ]

    def get_normalized_value(self, data):
        return [
            "{identify_type}::{identify_value}".format(
                identify_type=x.get(ProfileByIdentifyStructure.IDENTIFY_TYPE),
                identify_value=x.get(ProfileByIdentifyStructure.IDENTIFY_VALUE),
            )
            for x in data.get(self.field_key, [])
        ]

    def get_add_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.ADD not in data:
            data[ProfileHistoryChangeType.ADD] = []
        return [x.get(ProfileByIdentifyStructure.IDENTIFY_VALUE) for x in data.get(ProfileHistoryChangeType.ADD)]

    def get_remove_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.REMOVE not in data:
            data[ProfileHistoryChangeType.REMOVE] = []
        return [x.get(ProfileByIdentifyStructure.IDENTIFY_VALUE) for x in data.get(ProfileHistoryChangeType.REMOVE)]

