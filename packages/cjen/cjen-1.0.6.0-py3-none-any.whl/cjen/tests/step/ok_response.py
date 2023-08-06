import cjen
from cjen import MetaJson


class OKResponse(MetaJson):
    
    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.name")
    def name(self): ...

    @cjen.operate.common.value
    @cjen.operate.json.one(json_path="$.procCode")
    def procCode(self): ...
