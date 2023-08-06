
def dict_to_in(data_dict, name_output_file: str):
    '''
    Function that converts a dictionary into a .in file for DAKOTA

    :param data_dict, dict - contains all keys and values
    :param name_output_file, str - name of the .in file
    '''

    def __fill_up_level(level: int, string: str):
        '''
        Helper function that fills up a string with a tabular, according to the level
        '''
        filler = ''.join(map(str,([' ']*level*4)))
        return filler + string

    def __flatten_list(list: list):
        '''
        Helper function that reduces a list to a single string, separated by one space
        '''
        list = ["'"+x+"'" if type(x)==str else x for x in list]
        return ' '.join(map(str,list))

    def __construct_string(data, key):
        '''
        Helper function that constructs a string from data values, based on the type
        '''
        # If data value is empty/false: ignore
        if not data[key]:
            return ''

        # If string: fill only with data value
        if type(data[key]) == str:
            string = f"{key} = '{data[key]}' \n"
        # If list: return list flattened to a single line
        elif type(data[key]) == list:
            string = f"{key} = {__flatten_list(data[key])} \n"
        # If bool: return only key, without it's value
        elif type(data[key]) == bool:
            string = f"{key} \n"
        # All other types: return key and value
        else:
            string = f"{key} = {data[key]} \n"
        # Convention: If key is marked as a type, we ignore the key and just return the value
        if 'type' in key:
            string = f"{data[key]} \n"
        return string

    # Actual function that writes the .in file
    with open(name_output_file, 'w') as in_file:
        # Loop through all DAKOTA key words
        for key in data_dict.keys():
            in_file.write(f'{key} \n')
            # Loop through all sub-keys in each category
            for subkey in data_dict[key].keys():
                if type(data_dict[key][subkey])==dict:
                    for subsubkey in data_dict[key][subkey].keys():
                        string = __construct_string(data_dict[key][subkey], subsubkey)
                        if string: in_file.write(__fill_up_level(2, string))
                else:
                    string = __construct_string(data_dict[key], subkey)
                    if string: in_file.write(__fill_up_level(1, string))

    return