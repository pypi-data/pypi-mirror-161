from marshmallow import fields, validate, Schema
from mobio.libs.profiling_mf import ProfileTagsStructure, ProfileStructure, TagInteractiveStructure
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import DisplayType, ProfileHistoryChangeType
from mobio.libs.profiling_mf.profiling_schema import ProfileTagSchema


class MergeProfileTags(BaseMerge):
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
        set_data = set()
        lst_suggest_data = []
        profile_data = profile_data if profile_data is not None else []
        for a in profile_data:
            if type(a) == dict and a.get(ProfileTagsStructure.ID) not in set_data:
                lst_suggest_data.append(self.__build_value__(value=a, suggest=True))
                set_data.add(a.get(ProfileTagsStructure.ID))
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.ACTIVITY,
            value=lst_suggest_data,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        profile_data = profile_data if profile_data is not None else []
        for tag in profile_data:
            if tag and type(tag) == dict:
                suggest_filter_data.add(tag.get(ProfileTagsStructure.TAG))

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
        set_data = set()
        lst_suggest_data = []
        origin_data = origin_data if origin_data is not None else []
        if type(origin_data) == list:
            for a in origin_data:
                if type(a) == dict and a.get(ProfileTagsStructure.ID) not in set_data:
                    lst_suggest_data.append(self.__build_value__(value=a, suggest=True))
                    set_data.add(a.get(ProfileTagsStructure.ID))
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.ACTIVITY,
            value=lst_suggest_data,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[ProfileStructure.PROFILE_TAGS] = (
            target_data.get(ProfileStructure.PROFILE_TAGS)
            if target_data.get(ProfileStructure.PROFILE_TAGS)
            else []
        )
        target_data[ProfileStructure.TAGS_INTERACTIVE] = (
            target_data.get(ProfileStructure.TAGS_INTERACTIVE)
            if target_data.get(ProfileStructure.TAGS_INTERACTIVE)
            else []
        )
        if source_data:
            for data_suggest in source_data.get("field_value"):
                suggest = data_suggest.get("suggest")
                value = data_suggest.get("value")
                if suggest and value is not None:
                    exists_tags = next(
                        (
                            x
                            for x in target_data.get(ProfileStructure.PROFILE_TAGS)
                            if x.get(ProfileTagsStructure.MERCHANT_ID)
                            == value.get(ProfileTagsStructure.MERCHANT_ID)
                            and x.get(ProfileTagsStructure.ID) == value.get(ProfileTagsStructure.ID)
                        ),
                        None,
                    )
                    if not exists_tags:
                        target_data[ProfileStructure.PROFILE_TAGS].append(value)
        for tag in target_data.get(ProfileStructure.PROFILE_TAGS):
            if tag.get(ProfileTagsStructure.ID) not in target_data.get(
                ProfileStructure.TAGS_INTERACTIVE
            ):
                tag_interactive = CommonHelper.create_tag_interactive()
                tag_interactive[TagInteractiveStructure.TAG_ID] = tag.get(ProfileTagsStructure.ID)
                target_data[ProfileStructure.TAGS_INTERACTIVE].append(tag_interactive)
        target_data[ProfileStructure.TAGS] = list(
            set(
                [
                    x.get(ProfileTagsStructure.TAG)
                    for x in target_data.get(ProfileStructure.PROFILE_TAGS)
                ]
            )
        )

    def validate_merge(self, data, schema_validate_value=None):
        schema_validate_value = {
            "changeable": fields.Boolean(default=True, missing=True, allow_none=False),
            "suggest": fields.Boolean(default=True, missing=True, allow_none=False),
            "value": fields.Nested(ProfileTagSchema),
            "status": fields.Int(default=None, allow_none=True),
            "predict": fields.Dict(allow_none=True),
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
            "field_value": fields.List(
                fields.Nested(Schema.from_dict(schema_validate_value))
            ),
        }

        generated_schema = Schema.from_dict(rules)
        return generated_schema().load(data)

    def get_add_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.ADD not in data:
            data[ProfileHistoryChangeType.ADD] = []
        return [x.get(ProfileTagsStructure.ID) for x in data.get(ProfileHistoryChangeType.ADD)]

    def get_remove_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.REMOVE not in data:
            data[ProfileHistoryChangeType.REMOVE] = []
        return [x.get(ProfileTagsStructure.ID) for x in data.get(ProfileHistoryChangeType.REMOVE)]
