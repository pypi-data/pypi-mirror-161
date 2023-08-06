from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeIdentifyCode(BaseMerge):
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
        set_data = set()
        lst_suggest_data = []
        for a in profile_data:
            if a not in set_data:
                lst_suggest_data.append(self.__build_value__(value=a, suggest=True, predict=predict))
                set_data.add(a)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_data,
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
        set_data = set()
        lst_suggest_data = []
        origin_data = origin_data if origin_data is not None else []
        for a in origin_data:
            if a not in set_data:
                lst_suggest_data.append(self.__build_value__(value=a, suggest=True))
                set_data.add(a)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_data,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
        set_data = set(target_data.get(self.field_key)) if not is_master_data else set()
        if source_data:
            for data in source_data.get('field_value'):
                suggest = data.get("suggest")
                value = str(data.get("value")).strip() if data.get("value") is not None else ""
                if suggest and value:
                    set_data.add(value)
        target_data[self.field_key] = list(set_data)
