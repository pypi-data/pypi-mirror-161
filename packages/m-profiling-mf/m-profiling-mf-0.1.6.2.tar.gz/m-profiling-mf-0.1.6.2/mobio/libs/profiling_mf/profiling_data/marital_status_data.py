def df_get_marital_status_data():
    lst = []
    marital_status_data = [
        {
            "id": 1,
            "name": "Độc thân",
            'display_in_form': True
        },
        {
            "id": 2,
            "name": "Đã đính hôn",
            'display_in_form': True
        },
        {
            "id": 3,
            "name": "Đã kết hôn",
            'display_in_form': True
        },
        {
            "id": 4,
            "name": "Ly thân",
            'display_in_form': True
        },
        {
            "id": 5,
            "name": "Đã ly hôn",
            'display_in_form': True
        },
        {
            "id": 6,
            "name": "Quả phụ",
            'display_in_form': True
        },
        {
            "id": 7,
            "name": "Góa vợ",
            'display_in_form': True
        }
    ]
    for marital in marital_status_data:
        marital["display_in_form"] = True
        lst.append(marital)
    return lst
