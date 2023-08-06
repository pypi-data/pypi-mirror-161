from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeAddress(BaseMerge):
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
        set_address = set()
        lst_suggest_address = []
        profile_data = profile_data if profile_data is not None else []
        for a in profile_data:
            if a not in set_address:
                lst_suggest_address.append(
                    self.__build_value__(value=a, suggest=True, changealbe=True, predict=predict)
                )
                set_address.add(a)
        suggest_data[ProfileStructure.PROFILE_ADDRESS] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.DEMOGRAPHIC,
            value=lst_suggest_address,
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
        set_address = set()
        lst_suggest_address = []
        origin_data = origin_data if origin_data else []
        for a in origin_data:
            if a not in set_address:
                lst_suggest_address.append(
                    self.__build_value__(value=a, suggest=True, changealbe=True)
                )
                set_address.add(a)
        suggest_data[ProfileStructure.PROFILE_ADDRESS] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.DEMOGRAPHIC,
            value=lst_suggest_address,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[ProfileStructure.ADDRESS] = (
            target_data.get(ProfileStructure.ADDRESS)
            if target_data.get(ProfileStructure.ADDRESS)
            else []
        )
        set_address = (
            set(target_data.get(ProfileStructure.ADDRESS))
            if not is_master_data
            else set()
        )
        if source_data:
            for address_suggest in source_data.get("field_value"):
                suggest = address_suggest.get("suggest")
                value = (
                    str(address_suggest.get("value")).strip()
                    if address_suggest.get("value") is not None
                    else ""
                )
                if suggest and value:
                    set_address.add(value)
        target_data[ProfileStructure.ADDRESS] = list(set_address)
