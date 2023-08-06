from mobio.libs.profiling_mf import ProfileStructure
from mobio.libs.profiling_mf.common_helper import CommonHelper
from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup
from mobio.libs.profiling_mf.profiling_common import ProfileHistoryChangeType
from mobio.libs.profiling_mf.profiling_schema import SocialUserSchema


class MergeSocialUser(BaseMerge):
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
            self.__add_social_user__(
                social_data=social,
                lst_social=lst_social,
                set_unique_suggest_values=set_unique_suggest_values,
            )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_social,
        )

    def set_filter_value(self, suggest_filter_data, profile_data):
        pass

    def __add_social_user__(self, social_data, lst_social, set_unique_suggest_values):

        social_user = SocialUserSchema().load(social_data)
        unique_suggest_values = "{}:{}".format(
            social_user.get("social_id"), social_user.get("social_type")
        )
        suggest = (
            True if unique_suggest_values not in set_unique_suggest_values else False
        )
        lst_social.append(
            self.__build_value__(value=social_user, suggest=suggest, changealbe=False)
        )
        set_unique_suggest_values.add(unique_suggest_values)

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
        lst_social = []
        if origin_data:
            if type(origin_data) == list:
                for social in origin_data:
                    self.__add_social_user__(
                        social_data=social,
                        lst_social=lst_social,
                        set_unique_suggest_values=set_unique_suggest_values,
                    )
            elif type(origin_data) == dict:
                self.__add_social_user__(
                    social_data=origin_data,
                    lst_social=lst_social,
                    set_unique_suggest_values=set_unique_suggest_values,
                )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=True,
            editable=False,
            mergeable=True,
            order=1,
            group=MergeListGroup.INFORMATION,
            value=lst_social,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        lst_social_user = (
            target_data.get(ProfileStructure.SOCIAL_USER)
            if target_data.get(ProfileStructure.SOCIAL_USER)
            else []
        )
        if source_data:
            for source_social in source_data.get("field_value"):
                social_user = SocialUserSchema().load(source_social.get("value"))
                # lst_social_user = [
                #     x
                #     for x in target_data.get(ProfileStructure.SOCIAL_USER)
                #     if x.get("social_id") != social_user.get("social_id")
                #     and x.get("social_type") != social_user.get("social_type")
                # ]
                exists_social = next(
                    (
                        x
                        for x in lst_social_user
                        if x.get("social_id") == social_user.get("social_id")
                        and x.get("social_type") == social_user.get("social_type")
                    ),
                    None,
                )
                if not exists_social:
                    lst_social_user.append(social_user)
        target_data[ProfileStructure.SOCIAL_USER] = lst_social_user

    def normalized_value(self, data):
        result = []
        field_data = data.get(self.field_key, [])
        if field_data:
            for row in field_data:
                result.append(
                    CommonHelper().generate_social_unique_key(
                        social_type=row.get("social_type"), social_id=row.get("social_id"),
                    )
                )
        return result

    def get_normalized_value(self, data):
        result = []
        field_data = data.get(self.field_key, [])
        if field_data:
            for row in field_data:
                result.append(
                    CommonHelper().generate_social_unique_key(
                        social_type=row.get("social_type"), social_id=row.get("social_id"),
                    )
                )
        return result

    def get_add_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.ADD not in data:
            data[ProfileHistoryChangeType.ADD] = []
        return [x.get("social_id") for x in data.get(ProfileHistoryChangeType.ADD)]

    def get_remove_data(self, data):
        if not data:
            data = dict()
        if ProfileHistoryChangeType.REMOVE not in data:
            data[ProfileHistoryChangeType.REMOVE] = []
        return [x.get("social_id") for x in data.get(ProfileHistoryChangeType.REMOVE)]
