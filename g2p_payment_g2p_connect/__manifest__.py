{
    "name": "OpenG2P Program Payment: G2P Connect Payment Manager",
    "category": "G2P",
    "version": "17.0.0.0.0",
    "sequence": 1,
    "author": "OpenG2P",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": [
        "base",
        "g2p_registry_membership",
        "g2p_programs",
        "g2p_payment_files",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/payment_manager_view.xml",
        "views/registrant_view.xml",
        "views/payment_view.xml",
        "views/summary_report.xml"
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
