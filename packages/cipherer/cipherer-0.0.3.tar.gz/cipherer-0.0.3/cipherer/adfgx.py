# 1. Do the square thing
# 2. Get thing into table with second key
# 3. Rearrange table by key's alphabetical order
# Germans, U SUCK for making this so hard...
#   A D F G X
# A a b c d e
# D f g h i j
# F k l m n o
# G p q r s t
# X u v w x y
# e.g. "abcdefghijklmnopqrstuvwxy", "oh" -> "FX DF"


def square_thing(alphabet, first_input, adfgx_or_adfgvx):
    square_dict = {}
    alphabet_index = 0
    for column_letter in adfgx_or_adfgvx:
        for row_letter in adfgx_or_adfgvx:
            square_dict[alphabet[alphabet_index]] = column_letter + row_letter
            alphabet_index += 1

    output = ""
    for char in first_input:
        output += square_dict[char]
    return output


# e.g. "jih", "FX DF" -> ["FF", "X", "D"]
def get_table(squareified_thing, key):
    columns = []
    for i in range(len(key)):
        columns.append("")  # ['AAFAFA', 'DAGAGA']
    column = 0
    for char in squareified_thing:
        columns[column] += char
        if column == len(key) - 1:
            column = 0
        else:
            column += 1
    return columns


# First: figure out how to sort string without using built-ins

# Then:
# e.g. "jih", ["FF", "X", "D"] -> ["D", "X", "FF"]
# ["FF", "X", "D"], "jih"
# ["jFF", "iX", "hD"]

def order_table(key, table):
    # hi = "hi"
    # hi = "j" + hi
    # hi == "jhi"
    new_table = []
    for i in range(0, len(table)):
        new_table.append(key[i] + table[i])
    new_table.sort()
    # something = "hiii"
    # something = something[1:]
    new_new_table = []
    for i in range(0, len(table)):
        new_new_table.append(new_table[i][1:])
    return ''.join(new_new_table)


def encrypt(alphabet="abcdefghijklmnopqrstuvwxy", key="cargo", message="", adfgvx=False):
    if adfgvx:
        adfgx_or_adfgvx = "ADFGVX"
    else:
        adfgx_or_adfgvx = "ADFGX"
    squared_thing = square_thing(alphabet, message, adfgx_or_adfgvx)
    unordered_table = get_table(squared_thing, key)
    unspaced_chars = order_table(key, unordered_table)
    output = ""
    for i in range(len(unspaced_chars)):
        if i % 5 == 0 and i != 0:
            output += ' '
        output += unspaced_chars[i]
    return output