def count_watts(filename: str, begin: str, end: str):
    def convert_to_secs(date: list):
        return date[3] + 60 * (date[2] + 60 * (date[1] + 24 * date[0]))

    begin = list(map(int, begin.split(',')))
    end = list(map(int, end.split(',')))
    ls = open(filename, 'r').read().split('\n')[:-1]
    ls = list(map(lambda x: list(map(int, x.split(','))), ls))
    flag = 0
    start = convert_to_secs(begin)
    finish = convert_to_secs(end)
    summa = 0
    for _ in ls:
        cur = convert_to_secs(_)
        if finish < cur:
            break
        if flag:
            summa += _[-1]
            continue
        if finish < cur:
            break
        if start <= cur:
            summa += _[4]
            flag = 1
    return (summa)