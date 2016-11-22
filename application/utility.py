def find_key_gap(l, start = 1):
    if len(l) == 0:
        return start
    end = max(l)
    check_set = set(range(start, end + 1))
    l = set(l)
    diff_set = check_set.difference(l)

    if len(diff_set) == 0:
        return end+1
    else:
        return min(diff_set)