from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import ProfileHistoryChangeType


class MergeProvinceCode(BaseMerge):
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
        suggest_province = False
        if profile_data is not None and self.field_key not in set_suggest_fields:
            suggest_province = True
            set_suggest_fields.add(self.field_key)
        field_value = self.__build_value__(
            value=profile_data.get("id") if profile_data is not None else None,
            suggest=suggest_province,
            predict=predict
        )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.DEMOGRAPHIC,
            value=field_value,
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
        suggest = True if self.field_key not in set_suggest_fields and origin_data else False
        field_value = self.__build_value__(value=origin_data, suggest=suggest)
        if suggest:
            set_suggest_fields.add(self.field_key)
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=True,
            mergeable=True,
            order=1,
            group=MergeListGroup.DEMOGRAPHIC,
            value=field_value,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            suggest = source_data.get("field_value").get("suggest")
            value = source_data.get("field_value").get("value")
            # if suggest and value is not None:
            #     lst_province = df_get_province_data()
            #     province_code = next(
            #         (x for x in lst_province if x.get("id") == value), None
            #     )
            #     if province_code:
            #         target_data[self.field_key] = CommonHelper.create_simple_data_type(
            #             _id=province_code.get("id"), _name=province_code.get("name")
            #         )

    def get_updated_data(self, data):
        if not data:
            data = dict()
        if data.get(ProfileHistoryChangeType.REMOVE):
            old_value = data.get(ProfileHistoryChangeType.REMOVE)[0]
        else:
            old_value = (
                data.get(ProfileHistoryChangeType.CHANGE)[0].get("from")
                if data.get(ProfileHistoryChangeType.CHANGE)
                else None
            )
        if data.get(ProfileHistoryChangeType.ADD):
            new_value = data.get(ProfileHistoryChangeType.ADD)[0]
        else:
            new_value = (
                data.get(ProfileHistoryChangeType.CHANGE)[0].get("to")
                if data.get(ProfileHistoryChangeType.CHANGE)
                else None
            )
        return old_value if old_value else None, new_value if new_value else None

    def normalized_value(self, data):
        return data.get(self.field_key).get("id") if data.get(self.field_key) else None
