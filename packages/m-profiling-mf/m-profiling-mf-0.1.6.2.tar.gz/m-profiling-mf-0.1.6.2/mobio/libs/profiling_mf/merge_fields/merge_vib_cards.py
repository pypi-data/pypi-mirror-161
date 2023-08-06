from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeVibCards(BaseMerge):
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
        set_id = set()
        for data in profile_data:
            if data.get("card_id") not in set_id:
                set_id.add(data.get("card_id"))
                lst_suggest.append(
                    self.__build_value__(value=data, suggest=True)
                )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.DYNAMIC,
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
        set_id = set()
        origin_data = origin_data or []
        for data in origin_data:
            if data.get("card_id") not in set_id:
                set_id.add(data.get("card_id"))
                lst_suggest.append(
                    self.__build_value__(value=data, suggest=True)
                )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.DYNAMIC,
            value=lst_suggest,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            target_data[self.field_key] = target_data.get(target_data, [])
            set_id = set([x.get("card_id") for x in target_data.get(target_data)])
            for data in source_data.get('field_value'):
                if data.get("card_id") not in set_id:
                    target_data[self.field_key].append(data)
                    set_id.add(data.get("card_id"))
