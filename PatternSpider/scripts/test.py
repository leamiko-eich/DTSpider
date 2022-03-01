import ast
import time
import datetime


def get_minute_diff(time_a, time_b):
    if time_a <= time_b:
        return 0

    ta = time.strptime(time_a, "%H:%M:%S")
    tb = time.strptime(time_b, "%H:%M:%S")
    y, m, d, H, M, S = ta[0:6]
    date_time_a = datetime.datetime(y, m, d, H, M, S)
    y, m, d, H, M, S = tb[0:6]
    date_time_b = datetime.datetime(y, m, d, H, M, S)

    second_diff = (date_time_a - date_time_b).seconds
    minute_diff = int(round(second_diff / 60, 1))

    return minute_diff

def judge_time_interval(pre_date, next_date):
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    pre_time = int(time.mktime(time.strptime("{} {}".format(now_date, pre_date), '%Y-%m-%d %H:%M:%S')))
    next_time = int(time.mktime(time.strptime("{} {}".format(now_date, next_date), '%Y-%m-%d %H:%M:%S')))
    now_time = int(time.time())
    if pre_time < now_time < next_time:
        return True
    return False


def get_image() -> tuple:
    """ 获取ECS镜像 """
    ms = [
        (1, "image_id", "windows 2019", "07:30:00,10:30:00,13:30:00,16:30:00,19:30:00", "aliyun"),
        (2, "image_id", "windows 2019", "08:30:00,11:30:00,14:30:00,17:30:00,20:30:00", "aliyun"),
        (3, "image_id", "windows 2019", "09:30:00,12:30:00,15:30:00,18:30:00,21:30:00", "aliyun")
    ]
    now_time = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
    time_diff = {}
    for idx, m in enumerate(ms):
        itv = m[3]  # interval
        # itv = ast.literal_eval(interval)    # please use ast.literal_eval() instead of eval() for safety sake
        itv_list = itv.split(',')
        for i in range(len(itv_list) - 1):
            cur_val = itv_list[i].strip()
            next_val = itv_list[i + 1].strip()
            if cur_val < now_time < next_val:
                minute_diff = get_minute_diff(next_val, now_time)
                if minute_diff > 10:
                    time_diff[idx] = minute_diff

    if time_diff:
        diff_order = sorted(time_diff.items(), key=lambda x: x[1], reverse=False)
        return ms[diff_order[0][0]] + (diff_order[0][1],)  # 将时间差放入元组中
    else:
        return None


if __name__ == '__main__':
    print(get_image())
