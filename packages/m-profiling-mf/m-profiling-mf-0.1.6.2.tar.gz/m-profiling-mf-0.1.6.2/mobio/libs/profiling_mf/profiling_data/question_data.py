def df_get_question_data():
    question_data = [
        {
            "id": 1,
            "question": "Có hợp đồng bảo hiểm trên 1 năm không?",
            "type": 1,
            "answer_template": {
                "answers": [
                    {
                        "int_result": 1,
                        "string_result": "Có"
                    },
                    {
                        "int_result": 0,
                        "string_result": "Không"
                    }
                ]
            },
            "group_code": "VPBANK_PERSONAL_QUESTION_1"
        },
        {
            "id": 2,
            "question": "Có sở hữu ô tô không?",
            "type": 1,
            "answer_template": {
                "answers": [
                    {
                        "int_result": 1,
                        "string_result": "Có"
                    },
                    {
                        "int_result": 0,
                        "string_result": "Không"
                    }
                ]
            },
            "group_code": "VPBANK_PERSONAL_QUESTION_1"
        },
        {
            "id": 3,
            "question": "Có sở hữu Bất động sản không?",
            "type": 1,
            "answer_template": {
                "answers": [
                    {
                        "int_result": 1,
                        "string_result": "Có"
                    },
                    {
                        "int_result": 0,
                        "string_result": "Không"
                    }
                ]
            },
            "group_code": "VPBANK_PERSONAL_QUESTION_1"
        }
    ]
    return question_data


def df_get_question_data_by_group_code(group_code):
    return [x for x in df_get_question_data() if x.get('group_code') == group_code]
