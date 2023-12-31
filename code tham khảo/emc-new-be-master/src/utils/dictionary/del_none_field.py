def del_none_field(data):
    del_data = [key for key in data.keys()  if not data[key]]
    for i in del_data:
        data.pop(i)

    return data