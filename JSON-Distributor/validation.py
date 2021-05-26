
def Validate_Member(member):

    # List keys and values for later indexing
    key_list = list(member.keys())
    val_list = list(member.values())

    # General Validation of required fields
    validation_fields = [member['first_name'], 
                        member['last_name'], 
                        member['agency'], 
                        member['agency_abbrev'], 
                        member['title'], 
                        member['portrait_file_name'], 
                        member['bio']]

    errors = []
    for value in validation_fields:
        none_val = Not_None_Validator(value)
        if none_val[0] == True:
            errors.append({ key_list[val_list.index(value)]: none_val[1] })

        empty_val = Not_Empty_String_Validator(value)
        if empty_val[0] == True:
            errors.append({ key_list[val_list.index(value)]: empty_val[1] })

    return errors


def Not_None_Validator(value):
    if value is None:
        error = 'Value must not be "None".'
        return [True, error]
    else:
        return [False]

def Not_Empty_String_Validator(value):
    if len(value) < 1:
        error = 'Length must be greater than 0.'
        return [True, error]
    else:
        return [None]

def Max_Length_Validator(value, max_length):
    if len(value) > max_length:
        error = f'Length must not exceed {max_length}'
        return [True, error]
    else:
        return [False]