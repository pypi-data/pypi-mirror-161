from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeCif(BaseMerge):
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
        lst_suggest_cif = []
        set_cif = set()
        profile_data = profile_data if profile_data is not None else []
        for cif in profile_data:
            if cif not in set_cif:
                lst_suggest_cif.append(self.__build_value__(value=cif, suggest=True))
                set_cif.add(cif)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_cif,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        profile_data = profile_data if profile_data is not None else []
        for cif in profile_data:
            if cif:
                suggest_filter_data.add(cif)

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
        lst_suggest_cif = []
        set_cif = set()
        origin_data = origin_data if origin_data is not None else []
        for cif in origin_data:
            if cif not in set_cif:
                lst_suggest_cif.append(self.__build_value__(value=cif, suggest=True))
                set_cif.add(cif)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_suggest_cif,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
            set_cif = set(target_data.get(self.field_key)) if not is_master_data else set()
            for cif in source_data.get("field_value"):
                suggest = cif.get("suggest")
                if suggest:
                    set_cif.add(cif.get("value"))
            target_data[self.field_key] = list(set_cif)
