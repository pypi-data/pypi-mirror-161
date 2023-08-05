from typing import List

from ..enums.fieldsEnum import FieldsEnum

def validateFields(fields: List[str]) -> bool:
    """ Validate the fields provided.

    Parameters
    -----------
    fields: :class:`List[str]`
         List of fields.

    Returns
    -----------
    bool: :class:`bool`
    """
    
    for field in fields:
        flag = False

        for index in range(len(FieldsEnum)):
            if(field == FieldsEnum(index).name):
                flag = True

        if(not flag):
            raise ValueError(f"'{field}' is not a valid field!")

    return True