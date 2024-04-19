from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestG2PCycle(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.program_model = cls.env["g2p.program"]
        cls.cycle_model = cls.env["g2p.cycle"]

    def test_create_manual_inkind_entitlement(self):
        program = self.program_model.create({"name": "Test Program"})

        cycle = self.cycle_model.create(
            {
                "name": "Test Cycle",
                "program_id": program.id,
                "start_date": fields.Datetime.now(),
                "end_date": fields.Datetime.now() + timedelta(days=7),
            }
        )

        action = cycle.manual_create_entitlement()

        self.assertEqual(
            action["type"], "ir.actions.act_window", "Action type should be ir.actions.act_window"
        )
        self.assertEqual(action["res_model"], "g2p.manual.entitlement.inkind.wizard", "Correct action model")
        self.assertEqual(action["context"]["default_cycle_id"], cycle.id, "Correct default cycle id")
        self.assertEqual(action["target"], "new", "Correct target")
