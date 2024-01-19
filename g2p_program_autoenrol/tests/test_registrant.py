from odoo.tests import common


class TestG2PRegistrant(common.TransactionCase):
    def setUp(self):
        super(TestG2PRegistrant, self).setUp()
        self.program = self.env["g2p.program"].create(
            {
                "name": "Test Program",
                "state": "active",
                "auto_enrol_partners": True,
                "auto_enrol_partners_domain": "[('country_id', '=', 233)]",
            }
        )

    def test_create_auto_enroll(self):
        registrant = self.env["res.partner"].create(
            {"name": "Test Registrant", "country_id": 233}
        )

        # Assert registrant creation
        self.assertEqual(registrant.name, "Test Registrant")

        # Assert membership creation and enrollment
        member = self.env["g2p.program_membership"].search(
            [("partner_id", "=", registrant.id), ("program_id", "=", self.program.id)]
        )
        self.assertEqual(member.state, "enrolled")

    def test_ineligible_registrant(self):
        registrant = self.env["res.partner"].create(
            {"name": "Ineligible Registrant", "country_id": 235}
        )

        # Assert no membership created
        self.assertFalse(
            self.env["g2p.program_membership"].search(
                [
                    ("partner_id", "=", registrant.id),
                    ("program_id", "=", self.program.id),
                ]
            )
        )