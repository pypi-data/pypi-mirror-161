from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeName(BaseMerge):
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
        suggest = (
            True
            if profile_data and ProfileStructure.NAME not in set_suggest_fields
            else False
        )
        if suggest:
            set_suggest_fields.add(ProfileStructure.NAME)
        field_value = self.__build_value__(
            value=profile_data, suggest=suggest, predict=predict
        )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=field_value,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        if profile_data:
            suggest_filter_data.add(profile_data)

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
        suggest = (
            True
            if ProfileStructure.NAME not in set_suggest_fields and origin_data
            else False
        )
        field_value = self.__build_value__(value=origin_data, suggest=suggest,)
        if suggest:
            set_suggest_fields.add(ProfileStructure.NAME)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=field_value,
        )
