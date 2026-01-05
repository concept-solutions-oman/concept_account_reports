{
    'name': 'Concept Additional Reports',
    'version': '17.1',
    'depends': ['account','analytic'],
    'category': 'Accounting',
    'description': """
        This module generate additional accounting reports such as:
        - General Ledger
        - Partners Ledger 
        """,
    'author': 'Concept Solutions',
    'company': 'Concept Solutions',
    'maintainer': 'Concept Solutions',
    'website': 'https://www.csloman.com',
    'data': [ 
        'security/ir.model.access.csv', 
        'reports/general_ledger_report.xml',
        'reports/partner_ledger_report.xml',
        'reports/outstanding_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'concept_account_reports/static/src/css/tree_group_highlight.css'
        ],
    },
    "installable": True,
    "application": False,
    "license": "OPL-1",
    "price": 50.00,
    "currency": "USD",
}
