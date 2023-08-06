import uuid

from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeMerchantId(BaseMerge):
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
        lst_suggest_merchant_id = []
        for merchant_id in profile_data:
            lst_suggest_merchant_id.append(
                self.__build_value__(
                    value=str(merchant_id), suggest=True, predict=predict
                )
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
            value=lst_suggest_merchant_id,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        if type(profile_data) == list:
            for merchant_id in profile_data:
                if merchant_id:
                    suggest_filter_data.add(str(merchant_id))
        elif type(profile_data) == str:
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
        lst_merchant_id = []
        if type(origin_data) == list:
            lst_merchant_id = [str(x) for x in origin_data if x]
        elif type(origin_data) in [str, uuid.UUID]:
            lst_merchant_id = [str(origin_data)]
        lst_suggest_merchant_id = []
        for merchant_id in lst_merchant_id:
            lst_suggest_merchant_id.append(
                self.__build_value__(
                    value=str(merchant_id), suggest=True,
                )
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
            value=lst_suggest_merchant_id,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
        if source_data:
            for row in source_data.get("field_value"):
                suggest = row.get("suggest")
                value = CommonHelper.normalize_uuid(row.get("value"))
                if (
                    suggest
                    and value is not None
                    and value not in target_data.get(self.field_key)
                ):
                    target_data[self.field_key].append(value)
