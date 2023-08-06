from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeProfileGroup(BaseMerge):
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
        lst_suggest_profile_group = []
        for profile_group in profile_data:
            if profile_group:
                lst_suggest_profile_group.append(
                    self.__build_value__(value=str(profile_group), suggest=True)
                )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_profile_group,
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
        lst_suggest_profile_group = []
        origin_data = origin_data if origin_data else []
        for profile_group in origin_data:
            if profile_group:
                lst_suggest_profile_group.append(
                    self.__build_value__(value=str(profile_group), suggest=True)
                )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_profile_group,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
        if source_data:
            for row in source_data.get("field_value"):
                suggest = row.get("suggest")
                value = str(row.get("value"))
                if (
                    suggest
                    and value is not None
                    and value not in target_data.get(self.field_key)
                ):
                    target_data[self.field_key].append(value)
