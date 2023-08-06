def df_get_frequently_data():
    lst = []
    frequently_demand_data = [
        {
            "id": 1,
            "name": "Đi du lịch",
            "name_en": "Travel",
            "display_in_form": True
        },
        {
            "id": 2,
            "name": "Mua sắm online",
            "name_en": "Online Shopping",
            "display_in_form": True
        },
        {
            "id": 3,
            "name": "Mua sắm siêu thị",
            "name_en": "Offline Shopping",
            "display_in_form": True
        },
        {
            "id": 4,
            "name": "Ăn uống nhà hàng",
            "name_en": "Restaurant",
            "display_in_form": True
        },
        {
            "id": 5,
            "name": "Giải trí",
            "name_en": "Entertainment",
            "display_in_form": True
        },
        {
            "id": 6,
            "name": "Đóng tiền học phí",
            "name_en": "Pay tuition fee",
            "display_in_form": True
        }
    ]
    for frequently in frequently_demand_data:
        frequently["display_in_form"] = True
        lst.append(frequently)
    return lst
