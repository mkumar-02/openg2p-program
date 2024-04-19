from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestG2PManualEntitlementInKindWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manual_inkind_entitlement_model = cls.env["g2p.manual.entitlement.inkind.wizard"]
        cls.inkind_entitlement_wiz_item_model = cls.env["g2p.manual.entitlement.inkind.item.wizard"]
        cls.product_model = cls.env["product.product"]
        cls.program_model = cls.env["g2p.program"]
        cls.uom_model = cls.env["uom.uom"]
        cls.partner_model = cls.env["res.partner"]
        cls.cycle_membership_model = cls.env["g2p.cycle.membership"]
        cls.cycle_model = cls.env["g2p.cycle"]

    def test_prepare_entitlements(self):
        # Create necessary data
        program = self.program_model.create({"name": "Test Program"})
        partner = self.partner_model.create({"name": "Test Partner"})
        cycle = self.cycle_model.create(
            {
                "name": "Test Cycle",
                "program_id": program.id,  # Set the program_id to associate the cycle with the program
                "start_date": fields.Datetime.now(),
                "end_date": fields.Datetime.now() + timedelta(days=7),
            }
        )
        membership = self.cycle_membership_model.create({"cycle_id": cycle.id, "partner_id": partner.id})

        product = self.env["product.product"].create(
            {
                "name": "RICE",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_kgm").id,
                "uom_po_id": self.env.ref("uom.product_uom_kgm").id,
            }
        )

        wizard = self.manual_inkind_entitlement_model.create({"cycle_id": cycle.id})

        # Create wizard item
        wizard_item = self.inkind_entitlement_wiz_item_model.create(
            {
                "inkind_ent_id": wizard.id,
                "product_id": product.id,
                "qty": 1,
            }
        )

        # Prepare entitlements
        entitlement_created = wizard.prepare_entitlements(cycle, membership)
        self.assertTrue(entitlement_created, "Entitlement creation should be successful")

        # Check if entitlements are created
        entitlements = self.env["g2p.entitlement.inkind"].search([("cycle_id", "=", cycle.id)])
        self.assertTrue(entitlements, "Entitlements should be created")

        # Check entitlement details
        for entitlement in entitlements:
            self.assertEqual(
                entitlement.partner_id.id, partner.id, "Entitlement partner should match membership"
            )
            self.assertEqual(
                entitlement.product_id.id, product.id, "Entitlement product should match wizard item product"
            )
            self.assertEqual(
                entitlement.qty, wizard_item.qty, "Entitlement quantity should match wizard item quantity"
            )
