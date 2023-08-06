from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeInternalId(BaseMerge):
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
        lst_suggest_internal_id = []
        set_internal_id = set()
        profile_data = profile_data if profile_data is not None else []
        for internal_id in profile_data:
            if internal_id not in set_internal_id:
                lst_suggest_internal_id.append(
                    self.__build_value__(value=internal_id, suggest=True, changealbe=False)
                )
                set_internal_id.add(internal_id)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_internal_id,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        profile_data = profile_data if profile_data is not None else []
        for internal_id in profile_data:
            if internal_id:
                suggest_filter_data.add(internal_id)

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
        lst_suggest_internal_id = []
        set_internal_id = set()
        origin_data = origin_data if origin_data is not None else []
        for internal_id in origin_data:
            if internal_id not in set_internal_id and internal_id:
                lst_suggest_internal_id.append(
                    self.__build_value__(value=internal_id, suggest=True, changealbe=False)
                )
                set_internal_id.add(internal_id)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_internal_id,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
            set_internal_id = set(target_data.get(self.field_key)) if not is_master_data else set()
            for internal_id in source_data.get('field_value'):
                if internal_id.get("suggest") and internal_id.get("value"):
                    set_internal_id.add(internal_id.get("value"))
            target_data[self.field_key] = list(set_internal_id)

    def normalized_value(self, data):
        return data.get(self.field_key)
