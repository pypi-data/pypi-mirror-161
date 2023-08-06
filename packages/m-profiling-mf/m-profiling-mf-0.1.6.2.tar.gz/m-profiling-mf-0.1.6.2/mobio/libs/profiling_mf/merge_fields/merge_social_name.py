from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeSocialName(BaseMerge):
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
        lst_social = []
        for social in profile_data:
            _id = social.get("id")
            _name = social.get("name")
            _social_id = social.get("social_id")
            unique_suggest_value = CommonHelper().generate_social_unique_key(
                social_type=_id, social_id=_social_id,
            )
            suggest = (
                True if unique_suggest_value not in set_unique_suggest_values else False
            )
            lst_social.append(
                self.__build_value__(value=social, suggest=suggest, changealbe=False)
            )
            set_unique_suggest_values.add(unique_suggest_value)

        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_social,
        )

    def set_filter_value(self, suggest_filter_data: set, profile_data):
        if profile_data:
            for social in profile_data:
                if social and type(social) == dict and social.get("name"):
                    suggest_filter_data.add(social.get("name"))

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
        pass

    def merge_data(self, target_data, source_data, is_master_data=False):
        if source_data:
            lst_social_name = target_data.get(self.field_key, [])
            set_social_name = set()
            for social_name in lst_social_name:
                set_social_name.add(
                    CommonHelper().generate_social_unique_key(
                        social_type=social_name.get("id"),
                        social_id=social_name.get("social_id"),
                    )
                )
            for source_social in source_data.get("field_value"):
                suggest = source_social.get("suggest")
                if suggest:
                    _id = source_social.get("value").get("id")
                    _name = source_social.get("value").get("name")
                    _social_id = source_social.get("value").get("social_id")
                    unique_suggest_value = CommonHelper().generate_social_unique_key(
                        social_type=_id, social_id=_social_id
                    )
                    if unique_suggest_value not in set_social_name:
                        lst_social_name.append(source_social.get("value"))
                        set_social_name.add(unique_suggest_value)
            target_data[self.field_key] = lst_social_name

    def normalized_value(self, data):
        result = []
        field_data = data.get(self.field_key, [])
        if field_data:
            for row in field_data:
                result.append(
                    CommonHelper().generate_social_unique_key(
                        social_type=row.get("id"), social_id=row.get("social_id"),
                    )
                )
        return result
