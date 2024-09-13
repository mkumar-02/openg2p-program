# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

import logging
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PPayment(models.Model):
    _inherit = ["g2p.payment"]

    disbursement_envelope_id = fields.Char("Disbursement Envelope ID", related="cycle_id.disbursement_envelope_id")
    disbursement_id = fields.Char("Disbursement ID", required=False)
    dispatch_status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("sent", "Sent"),
        ],
        string="Dispatch Status",
        required=True,
        default="pending",
    )
    remittance_reference_number = fields.Char(required=False)
    remittance_statement_id = fields.Char(required=False)
    remittance_entry_sequence = fields.Char(required=False)
    remittance_entry_date = fields.Char(required=False)
    reversal_statement_id = fields.Char(required=False)
    reversal_entry_sequence = fields.Char(required=False)
    reversal_entry_date = fields.Char(required=False)
    reversal_reason = fields.Char(required=False)
    beneficiary_id = fields.Char("Beneficiary ID", required=False)


