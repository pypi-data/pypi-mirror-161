from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergePushId(BaseMerge):
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
        set_push_id = set()
        profile_data = profile_data if profile_data is not None else []
        for push_id in profile_data:
            if push_id.get("push_id") not in set_push_id:
                set_push_id.add(push_id.get("push_id"))
                lst_suggest.append(self.__build_value__(value=push_id, suggest=True, predict=predict))
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.OTHER,
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
        if type(origin_data) == list:
            set_push_id = set()
            for push_id in origin_data:
                if push_id.get("push_id") not in set_push_id:
                    set_push_id.add(push_id.get("push_id"))
                    lst_suggest.append(
                        self.__build_value__(value=push_id, suggest=True)
                    )
        elif type(origin_data) == dict:
            lst_suggest.append(self.__build_value__(value=origin_data, suggest=True))
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.OTHER,
            value=lst_suggest,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
        set_push_id = set([x.get("push_id") for x in target_data.get(self.field_key)])
        if source_data:
            for push_id in source_data.get("field_value"):
                suggest = push_id.get("suggest")
                value = push_id.get("value")
                if suggest and value.get("push_id") not in set_push_id:
                    target_data[self.field_key].append(value)
                    set_push_id.add(value.get("push_id"))

    def normalized_value(self, data):
        return [x.get("push_id") for x in data.get(self.field_key, [])]
