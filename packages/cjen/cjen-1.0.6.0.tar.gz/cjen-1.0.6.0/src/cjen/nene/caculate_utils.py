class CaculateUtils:
    @staticmethod
    def total_pip(total: int, percents=[]):
        values =[int(total * percent) for percent in percents]
        for value in values:
            print(value)


if __name__ == '__main__':
    stage = {
        "SIT 冒烟":0.13 ,
        "SIT 第一轮": 0.2,
        "SIT 第二轮": 0.15,
        "SIT 第三轮":  0.07,
        "UAT 第一轮": 0.11,
        "UAT 第二轮": 0.10,
        "UAT 第三轮": 0.11,
        "UAT 交叉测试": 0.12,
        "验收测试": 0.01,
    }
    print(sum(stage.values()))
    CaculateUtils.total_pip(63, list(stage.values()))

