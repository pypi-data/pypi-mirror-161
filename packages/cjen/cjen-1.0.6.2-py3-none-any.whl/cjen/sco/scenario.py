import os
import json


def Tester(Clazzes=[]):
    """
    设置 该装饰器后，Scenario下的step会执行带有Testing标签的测试用例。
    """

    def __wrapper__(func):
        def __inner__(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.is_run_test = True
            for clazz in Clazzes:
                self.register_test_classes.add(clazz)

        return __inner__

    return __wrapper__


class Scenario:
    # 为了兼容已有的代码
    # 所以增加的参数service 默认为None
    def __init__(self, scenario_dir, service=None):
        self.scenario_dir = scenario_dir
        self.data = dict()
        self.__load()
        self.steps = []
        self.service = service
        self.is_run_test = False
        self.register_test_classes = set()

    def __load(self):
        for root, dirs, files in os.walk(self.scenario_dir):
            for filename in files:
                if filename.endswith(".json"):
                    with open(os.path.join(root, filename), 'r', encoding="UTF-8") as f:
                        self.data[os.path.splitext(filename)[0]] = json.loads(f.read())

    def append_sub_scenario(self, sub_scenario):
        self.steps.append(sub_scenario)

    # Deprecated
    # 为了兼容已有的代码
    # 所以增加了self.service is None 的判断
    def append_step(self, step_class, service):
        if self.service is None:
            self.service = service
        self.steps.append(step_class(self.service, self))

    def add_step(self, step_class):
        self.steps.append(step_class(self.service, self))

    def run(self):
        for step in self.steps:
            step.run()

    def get(self, key):
        return self.data.get(key)


if __name__ == '__main__':
    scenario = Scenario("D:\\github\\eclinical\\eclinical\\standard\\scenarios\\new_study")
    print(scenario.data)
