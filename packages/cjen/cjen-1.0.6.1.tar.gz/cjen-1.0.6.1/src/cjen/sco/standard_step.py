def Testing(*, test_clazz, test_method):
    """
    执行测试用力装饰器，一般加在step 的call_back上
    test_clazz: 测试用例的执行类
    test_method: 测试用例的执行方法
    PS: 测试的数据是存放在service.context 中， Step 可定义TO(TestObject简写)关键字，来获取
    """

    def __wrapper__(func):
        def __inner__(ins: StandardStep, *args, **kwargs):
            func(ins, *args, **kwargs)
            if ins.scenario.is_run_test and test_clazz in ins.scenario.regsiter_test_classes:
                tester = test_clazz(ins.scenario)
                getattr(tester, test_method)(ins.service.context[ins.TO])

        return __inner__

    return __wrapper__


class StandardStep:

    def __init__(self, service, scenario):
        self.service = service
        self.scenario = scenario

    # 请求的json数据
    def data(self): ...

    # 请求中的url参数
    def path_variable(self): ...

    # 请求返回后的回调处理
    def call_back(self, **kwargs): ...

    # 请求的前置操作
    def _pre_processor(self): ...

    # 请求的后置操作
    def _post_processor(self): ...

    # 调用请求
    # 因为需要注册请求，所以子类覆写的时候需要条用super
    def _execute(self): self.service.register_step(self)

    # 忽略请求的条件，默认是要执行
    def ignore(self): return False

    # 运行step
    def run(self):
        self._pre_processor()
        if not self.ignore():
            self._execute()
        self._post_processor()
