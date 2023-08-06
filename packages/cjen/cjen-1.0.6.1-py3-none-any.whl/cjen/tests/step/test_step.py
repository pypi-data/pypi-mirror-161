import cjen
from cjen import BigTangerine
from cjen.sco.scenario import Scenario
from cjen.tests.aiai.test_http import MockService
from cjen.tests.step.ok_response import OKResponse
from cjen.tests.step.ok_step import OkStep
from cjen.tests.step.other_step import OtherStep


class StepMockService(BigTangerine):
    @cjen.http.base_url(uri="http://127.0.0.1:5000")
    def __init__(self):
        super().__init__()

    @cjen.headers.contentType(value="application/json")
    @cjen.http.post_mapping(uri="post_method_json", json_clazz=OKResponse)
    @cjen.step.call(stepName=OkStep.Name, argName="ok")
    @cjen.step.call(stepName=OtherStep.Name, argName="ok")
    def post_method_json(self, *, data, ok: OKResponse = None, resp=None, **kwargs): ...


def test_one_step():
    mock = StepMockService()
    OkStep(mock, None).run()
    OkStep(mock, None).run()
    # mock.post_method_json(data=dict(username="xx", pwd="yyy"))


def test_two_step():
    mock = StepMockService()
    OkStep(mock, None).run()
    OtherStep(mock, None).run()


# 验证在没有执行之前，Step 是不会注册进入Service的
def test_register():
    mock = StepMockService()
    steps = [OkStep(mock, None), OtherStep(mock, None)]
    for i, step in enumerate(steps):
        step.run()
        assert len(mock.step_definitions) == i + 1


def test_new_scenario():
    scenario = Scenario("", MockService())
    scenario.add_step(OkStep)
    scenario.add_step(OtherStep)
    scenario.run()


def test_compatible_old_scenario():
    scenario = Scenario("")
    service = MockService()
    scenario.append_step(OkStep, service)
    scenario.append_step(OtherStep, service)
    scenario.run()