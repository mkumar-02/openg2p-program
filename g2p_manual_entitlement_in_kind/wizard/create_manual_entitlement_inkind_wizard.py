# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class G2PManualEntitlementInKindWizard(models.TransientModel):
    _name = "g2p.manual.entitlement.inkind.wizard"
    _description = "Manual In-Kind Entitlement Wizard"

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

    products_item_ids = fields.One2many(
        "g2p.manual.entitlement.inkind.item.wizard", "inkind_ent_id", required=True
    )

    cycle_id = fields.Many2one("g2p.cycle")

    program_membership_ids = fields.Many2many(
        "g2p.cycle.membership", required=True, domain="[('cycle_id','=',cycle_id)]"
    )

    state = fields.Selection(
        [("step1", "Beneficiary List"), ("step2", "Products Items")],
        "Status",
        default="step1",
        readonly=True,
    )

    evaluate_single_item = fields.Boolean("Evaluate one item", default=False)

    manage_inventory = fields.Boolean(default=False)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=_default_warehouse_id,
        check_company=True,
    )
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company)

    def next_step(self):
        if not self.program_membership_ids:
            raise ValidationError(_("Please add beneficiary."))
        if self.state == "step1":
            self.state = "step2"
        return self._reopen_self()

    def prev_step(self):
        if not self.products_item_ids:
            raise ValidationError(_("Choose the entitlement products."))
        if self.state == "step2":
            self.state = "step1"
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def create_entitlement(self):
        if not self.program_membership_ids and not self.products_item_ids:
            raise ValidationError(_("Fill mandatory fields for create inkind entitlement"))
        else:
            self.prepare_entitlements(self.cycle_id, self.program_membership_ids)

    def prepare_entitlements(self, cycle, beneficiaries):
        if not self.products_item_ids:
            raise UserError(_("There are no items entered for this entitlement."))

        all_beneficiaries_ids = beneficiaries.mapped("partner_id.id")
        for rec in self.products_item_ids:
            if rec.condition:
                # Filter res.partner based on entitlement condition and get ids
                domain = [("id", "in", all_beneficiaries_ids)]
                domain += self.env["base.programs.manager"]._safe_eval(rec.condition)
                beneficiaries_ids = self.env["res.partner"].search(domain).ids

                # Check if single evaluation
                if self.evaluate_single_item:
                    # Remove beneficiaries_ids from all_beneficiaries_ids
                    for bid in beneficiaries_ids:
                        if bid in all_beneficiaries_ids:
                            all_beneficiaries_ids.remove(bid)
            else:
                beneficiaries_ids = all_beneficiaries_ids

            # Get beneficiaries_with_entitlements to prevent generating
            # the same entitlement for beneficiaries
            beneficiaries_with_entitlements = (
                self.env["g2p.entitlement.inkind"]
                .search(
                    [
                        ("cycle_id", "=", cycle.id),
                        ("partner_id", "in", beneficiaries_ids),
                        ("product_id", "=", rec.product_id.id),
                    ]
                )
                .mapped("partner_id.id")
            )
            entitlements_to_create = [
                beneficiaries_id
                for beneficiaries_id in beneficiaries_ids
                if beneficiaries_id not in beneficiaries_with_entitlements
            ]

            entitlement_start_validity = cycle.start_date
            entitlement_end_validity = cycle.end_date

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(entitlements_to_create)
            entitlements = []

            for beneficiary_id in beneficiaries_with_entitlements_to_create:
                multiplier = 1
                if rec.multiplier_field:
                    # Get the multiplier value from multiplier_field else return the default multiplier=1
                    multiplier = beneficiary_id.mapped(rec.multiplier_field.name)
                    if multiplier:
                        multiplier = multiplier[0] or 1
                if rec.max_multiplier > 0 and multiplier > rec.max_multiplier:
                    multiplier = rec.max_multiplier
                qty = multiplier * rec.qty

                entitlement_fields = {
                    "cycle_id": cycle.id,
                    "partner_id": beneficiary_id.id,
                    "total_amount": rec.product_id.list_price * qty,
                    "product_id": rec.product_id.id,
                    "qty": qty,
                    "unit_price": rec.product_id.list_price,
                    "uom_id": rec.uom_id.id,
                    "manage_inventory": self.manage_inventory,
                    "warehouse_id": self.warehouse_id and self.warehouse_id.id or None,
                    "state": "draft",
                    "valid_from": entitlement_start_validity,
                    "valid_until": entitlement_end_validity,
                }
                entitlements.append(entitlement_fields)

            if entitlements:
                self.env["g2p.entitlement.inkind"].sudo().create(entitlements)


class G2PManualEntitlementInKindItemWizard(models.TransientModel):
    _name = "g2p.manual.entitlement.inkind.item.wizard"
    _description = "Manual In-Kind Entitlement Item Wizard"

    inkind_ent_id = fields.Many2one("g2p.manual.entitlement.inkind.wizard", "New Program", required=True)

    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")], required=True
    )

    condition = fields.Char("Condition Domain")
    multiplier_field = fields.Many2one(
        "ir.model.fields",
        "Multiplier",
        domain=[("model_id.model", "=", "res.partner"), ("ttype", "=", "integer")],
    )
    max_multiplier = fields.Integer(
        default=0,
        string="Maximum number",
        help="0 means no limit",
    )

    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", related="product_id.uom_id")
