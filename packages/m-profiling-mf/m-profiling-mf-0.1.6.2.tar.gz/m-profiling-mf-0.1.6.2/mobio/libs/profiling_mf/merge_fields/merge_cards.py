from mobio.libs.profiling_mf.merge_fields.base_merge import BaseMerge, MergeListGroup


class MergeCards(BaseMerge):
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
        lst_cards = list()
        profile_data = profile_data if profile_data is not None else []
        for card in profile_data:
            lst_cards.append(
                self.__build_value__(value=card, suggest=True, predict=predict),
            )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=False,
            order=1,
            group=MergeListGroup.LOYALTY,
            value=lst_cards,
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
        origin_data = []
        lst_cards = []
        for card in origin_data:
            lst_cards.append(
                self.__build_value__(value=card, suggest=True),
            )
        suggest_data[self.field_key] = self.build_merge_data(
            translate_key=translate_key,
            field_property=field_property,
            display_type=display_type,
            displayable=False,
            editable=False,
            mergeable=False,
            order=1,
            group=MergeListGroup.LOYALTY,
            value=lst_cards,
        )

    def merge_data(self, target_data, source_data, is_master_data=False):
        target_data[self.field_key] = target_data.get(self.field_key) if target_data.get(self.field_key) else []
        set_data = set([x.get("card_id") for x in target_data.get(self.field_key)])
        if source_data:
            for data in source_data.get("field_value"):
                suggest = data.get("suggest")
                value = data.get("value")
                if (
                    suggest
                    and value is not None
                    and value.get("card_id") not in set_data
                ):
                    set_data.add(value.get("card_id"))
                    target_data[self.field_key].append(value)
