import random
import pandas as pd
import numpy as np


def gen_fake_name(number=10):
    """ 根据姓，名两个列表，生成n个假名字"""
    names = []
    for i in range(number):
        last_name = '赵钱孙李周吴郑王'
        sur_name = '丽国媛燕强飞侠平山峰婷凤凰华正近玉勇茂群益一兴'

        # 生成姓
        x = random.choices(last_name, k=1)

        # 生成名 1~2个汉字
        y = random.choices(sur_name, k=random.randrange(1, 3))
        # 性+名 得到名字，加入一个list
        names.append("".join(x + y))
    return names


def gen_fake_mark(lowe=40, high=100, number=10):
    """生成lowe 到 high 之间的 number个数字 ,成绩得分
    """
    return np.random.randint(lowe, high, number)


def gen_fake_students(n=10):
    students = pd.Series(gen_fake_mark(number=n), index=gen_fake_name(n), name="Marks")
    return students


students = gen_fake_students()
print(students)