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
    prev = start
    summa = 0
    for i in range(len(ls)):
        cur = convert_to_secs(ls[i])
        if finish < cur:
            break
        if flag:
            summa += ls[i][-1]*12*(cur-prev)
            prev = cur
            continue
        if finish < cur:
            break
        if start <= cur:
            summa += ls[i][-1] * 12 * (cur - prev)
            prev = cur
            flag = 1
    kwatts_per_hour = summa / 36 * 10
    return (kwatts_per_hour)