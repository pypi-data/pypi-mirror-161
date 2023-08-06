from cjen.sco.scenario import Scenario
from cjen.sco.standard_step import StandardStep


class OtherStep(StandardStep):
    Name = "other_step.py"

    def __init__(self, service, scenario: Scenario):
        super().__init__(service, scenario)

    def _pre_processor(self): ...

    def call_back(self, **kwargs): assert kwargs.get("ok").name() == "yyy"

    def _execute(self):
        super()._execute()
        self.service.post_method_json(data=dict(username="xx", pwd="yyy"))
