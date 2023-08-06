GENDER_DATA = [
    {
        "id": 2,
        "name": "Nam",
        'display_in_form': True
    },
    {
        "id": 3,
        "name": "Nữ",
        'display_in_form': True
    },
    {
        "id": 1,
        "name": "Không xác định",
        'display_in_form': True
    }
]


def df_get_gender_data():
    lst = []
    for gender in GENDER_DATA:
        lst.append(gender)
    return lst
