from odoo.addons.base_rest.controllers import main


class ProgramApiController(main.RestController):
    _root_path = "/api/v1/program/"
    _collection_name = "base.rest.program.services"
    _default_auth = "user"
