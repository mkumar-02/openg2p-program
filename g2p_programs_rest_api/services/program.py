from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component
from odoo.addons.g2p_registry_rest_api.models.individual_search_param import IndividualSearchParam

from ..models.program import ProgramInfoOut


class ProgramApiService(Component):
    _inherit = ["base.rest.service"]
    _name = "program.rest.service"
    _usage = "program"
    _collection = "base.rest.program.services"
    _description = """
        Program API Services
    """

    @restapi.method(
        [
            (
                [
                    "/<int:id>",
                ],
                "GET",
            )
        ],
        output_param=PydanticModel(ProgramInfoOut),
        auth="user",
        cors="*",
    )
    def get(self, _id):
        """
        Get program's information
        """
        program = self.env["g2p.program"].sudo().search([("id", "=", _id)])
        return ProgramInfoOut.from_orm(program)

    @restapi.method(
        [(["/", "/search"], "GET")],
        input_param=PydanticModel(IndividualSearchParam),
        output_param=PydanticModelList(ProgramInfoOut),
        auth="user",
        cors="*",
    )
    def search(self, partner_search_param):

        programs = self.env["g2p.program"].sudo()
        active_programs = programs.search([("state", "=", "active")])

        res = []

        for program in active_programs:
            res.append(ProgramInfoOut.from_orm(program))

        return res
