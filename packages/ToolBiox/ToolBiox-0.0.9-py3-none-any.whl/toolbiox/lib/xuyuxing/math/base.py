import math


def base_translate(num, base_num):
    if num < base_num:
        return [num]
    else:
        n = int(math.log10(num) / math.log10(base_num)) + 1
        output_list = []
        for i in range(n):
            num_add = num // (base_num ** (n - i - 1))
            output_list.append(num_add)
            num = num - num_add * (base_num ** (n - i - 1))
        return output_list