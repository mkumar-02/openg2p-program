# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    inkind_entitlements_count = fields.Integer(
        string="# In-kind Entitlements",
        compute="_compute_inkind_entitlements_count",
        readonly=True,
    )

    def _compute_inkind_entitlements_count(self):
        for rec in self:
            entitlements_count = self.env["g2p.entitlement.inkind"].search_count([("cycle_id", "=", rec.id)])
            rec.update({"inkind_entitlements_count": entitlements_count})

    def create_manual_inkind_entitlement(self):
        return {
            "name": _("Create Entitlement"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.manual.entitlement.inkind.wizard",
            "view_mode": "form",
            "view_type": "form",
            "context": {
                "default_cycle_id": self.id,
            },
            "target": "new",
        }
