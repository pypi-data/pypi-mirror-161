def read_to_dict(path: str, multi: int=1, fill: int=1) -> dict:
    """
    Reads a .txt file into a dictionary. The .txt file must be TAB separated.
    The first entry in each line will be the key and the remaining items will
    be collected as a list.
    Multi=0 means you read only the first two items {key:value}.
    The fill kwarg fills in the end of lines shorter than the head with None.
    """
    result = {}
    if fill != 0:
        with open(path, 'r') as f:
            head = f.readline()
            head = head.strip().split('\t')
    with open(path, 'r') as f:
        if multi == 0:
            for line in f:
                x = line.strip().split('\t')
                if len(x) < 2:
                    continue
                result[x[0]] = x[1]
        else:
            for line in f:
                x = line.strip().split('\t')
                if len(x) == 1:
                    result[x[0]] = None
                result[x[0]] = x[1:]
                if fill != 0:
                    while len(result[x[0]]) < len(head)-1:
                        result[x[0]].append(None)

    return result


def read_to_list(path: str, fill: int=1) -> list:
    """
    Reads a TAB separated .txt file into a list of lists.
    The fill keyword appends None to the end of every line shorter than the header
    """
    result = []
    with open(path, 'r') as f:    
        if fill == 0:
            for line in f:
                temp = line.strip()
                temp = temp.split('\t')
                result.append(temp)
        else:
            for line in f:
                temp = line.strip()
                temp = temp.split('\t')
                result.append(temp)
                while len(result[-1]) < len(result[0]):
                    result[-1].append(None)

    return result


def list_printer(source_list: list, output_filename: str) -> str:
    """
    Prints a list into a tab sparated .txt file. Also returns the contents
    of the file as a string.
    """
    printer = ''
    for row in source_list:
        for cell in row:
            if type(cell) == list:
                printer += str(cell[0])
                continue
            printer += str(cell)
            printer += '\t'
        printer += '\n'

    with open(f'{output_filename}.txt', 'w') as f:
        f.write(printer)

    return printer


def dict_printer(source_dict: dict, output_filename: str):
    """
        the source dict values must be either lists, tuples, or numbers
    """
    printer = ''
    for key in source_dict:
        printer += key + '\t'
        if type(source_dict[key])==tuple or type(source_dict[key])==list:
            for item in source_dict[key]:
                printer += item
                printer += '\t'
        else:
            printer += source_dict[key]
            printer += '\t'
        printer += '\n'

    with open(f'{output_filename}.txt', 'w') as f:
        f.write(printer)



def read_tabstring(string):
    temp = string.strip().split('\n')
    temp_dict = {}
    for item in temp:
        x = item.split('\t')
        temp_dict[x[0]] = item.split('\t')[1:]
    return temp_dict


def list_add_from_dict(x: list, y: dict, list_index: int = 0):
    result = []
    for item in x:
        temp = item
        if item[list_index] not in y:
            continue
        temp.append(y[item[list_index]])
        result.append(temp)
    return None
