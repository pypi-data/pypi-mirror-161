def read_int():
    # noinspection PyGlobalUndefined
    global this_variable_is_keeping_inputs
    try:
        this_variable_is_keeping_inputs = this_variable_is_keeping_inputs
    except:
        this_variable_is_keeping_inputs = None
    if not this_variable_is_keeping_inputs:
        this_variable_is_keeping_inputs = input().strip().split(' ')[::-1]
    return int(this_variable_is_keeping_inputs.pop())


if __name__ == '__main__':
    '''
5 5
5 4 2 3 5
2 0 3
1 1 1
2 0 3
1 3 1
2 0 5
    '''
    m = read_int()
    n = read_int()
    print(m, n)

    arr = [read_int() for _ in range(m)]
    print(arr)
    for i in range(n):
        row = [read_int(), read_int(), read_int()]
        print(row)
