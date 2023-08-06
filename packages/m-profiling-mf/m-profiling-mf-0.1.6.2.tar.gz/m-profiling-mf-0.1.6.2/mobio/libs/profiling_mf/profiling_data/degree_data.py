def df_get_degree_data():
    degree_data = [
        {
            'id': 1,
            'name': 'Sau đại học',
            'display_in_form': True
        },
        {
            'id': 2,
            'name': 'Đại học',
            'display_in_form': True
        },
        {
            'id': 3,
            'name': ' Cao đẳng',
            'display_in_form': True
        },
        {
            'id': 4,
            'name': 'Phổ thông',
            'display_in_form': True
        },
        {
            'id': 5,
            'name': 'Trung cấp',
            'display_in_form': True
        }
    ]
    lst = []
    for degree in degree_data:
        degree["display_in_form"] = True
        lst.append(degree)
    return lst
