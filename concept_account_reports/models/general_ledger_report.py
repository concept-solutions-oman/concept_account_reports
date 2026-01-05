from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date

class ConceptGeneralLedger(models.Model):
    _name = 'concept.general.ledger'
    _description = 'Concept General Ledger'
    _auto = False
    _order = 'date desc'

    date = fields.Date("Date")
    journal_id = fields.Many2one("account.journal", "Journal")
    partner_id = fields.Many2one("res.partner", "Partner")
    move_id = fields.Many2one("account.move", "Move")
    move_name = fields.Char("Move Name")
    entry_label = fields.Char("Entry Label")
    debit = fields.Monetary("Debit")
    credit = fields.Monetary("Credit")
    balance = fields.Monetary("Balance")
    account_id = fields.Many2one("account.account", "Account")
    currency_id = fields.Many2one('res.currency', string='Currency') 
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account"
    )
    invoice_date = fields.Date(string="Invoice Date")
    due_date = fields.Date(string="Due Date")
    reconciled = fields.Boolean("Reconciled")
    state = fields.Selection([ # Added state field
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)


    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS concept_general_ledger CASCADE")
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW concept_general_ledger AS (
                SELECT
                    aml.id AS id,
                    aml.date AS date,
                    aml.journal_id,
                    aml.partner_id,
                    aml.move_id,
                    am.invoice_date AS invoice_date,
                    am.invoice_date_due AS due_date,
                    am.name AS move_name,
                    am.state AS state,
                    aml.name AS entry_label,
                    aml.debit AS debit,
                    aml.credit AS credit,
                    aml.debit - aml.credit AS balance,
                    aml.account_id,
                    aml.company_currency_id AS currency_id,
                    aml.reconciled AS reconciled, 
                    aml.company_id AS company_id,
                    (
                        SELECT key::int
                        FROM jsonb_each(aml.analytic_distribution::jsonb)
                        WHERE key ~ '^\d+$'
                        LIMIT 1
                    ) AS analytic_account_id

                FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                WHERE am.state = 'posted'
            )
        """)



 