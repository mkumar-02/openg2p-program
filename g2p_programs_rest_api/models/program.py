from odoo.addons.g2p_registry_rest_api.models.naive_orm_model import NaiveOrmModel


class ProgramInfoOut(NaiveOrmModel):
    name: str = None
    target_type: str = None
    state: str = None
