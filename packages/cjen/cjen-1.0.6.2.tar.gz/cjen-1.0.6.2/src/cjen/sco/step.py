from cjen import BigTangerine


def call(*, stepName: str, argName: str):
    def __wrapper__(func):
        def __inner__(ins: BigTangerine, *args, **kwargs):
            # resp =
            ins.step_definitions.call_back(stepName, **{f'{argName}': kwargs.get(argName)})
            return func(ins, *args, **kwargs)

        return __inner__

    return __wrapper__
