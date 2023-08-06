from django.utils.text import smart_split
import shlex


def split_contents(value):
    split = []
    bits = smart_split(value)

    for bit in bits:
        if bit.startswith(('_("', "_('")):
            sentinel = bit[2] + ')'
            trans_bit = [bit]

            while not bit.endswith(sentinel):
                bit = next(bits)
                trans_bit.append(bit)
            bit = ' '.join(trans_bit)

        split.append(bit)

    return split


def handle_args(value):
    args = []
    kwargs = {}

    for bit in split_contents(value):
        e = bit.find('=')

        if e > -1:
            q = bit.find("'")
            if q > e:
                key = bit[:e]
                value = shlex.split(bit[e + 1:])[0]
                kwargs[key] = value
            else:
                q = bit.find('"')
                if q > e:
                    key = bit[:e]
                    value = shlex.split(bit[e + 1:])[0]
                    kwargs[key] = value
        else:
            bit = shlex.split(bit)
            args.append(bit[0])

    return tuple(args), kwargs
