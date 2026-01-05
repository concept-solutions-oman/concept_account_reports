from odoo import models, fields
from dateutil.relativedelta import relativedelta
from datetime import date

class ConceptPartnerLedger(models.Model):
    _name = 'concept.outstanding.report'
    _description = 'Concept Outstanding Report'
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
    analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic Account")
    reconciled = fields.Boolean("Reconciled")
    tax_id = fields.Many2one("account.tax", string="Tax")
    tax_base_amount = fields.Monetary("Tax Base Amount")
    tax_amount = fields.Monetary("Tax Amount")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_due_date = fields.Date(string="Due Date")
    due_date = fields.Date("Due Date")
    due_amount = fields.Monetary("Due Amount")
    due_days = fields.Integer("Due Days")
    status = fields.Char("Status") # 'Open', 'Paid', 'Overdue' 
    state = fields.Selection([ # Added state field
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS concept_outstanding_report CASCADE")
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW concept_outstanding_report AS (
                SELECT
                    aml.id AS id,
                    aml.date,
                    aml.journal_id,
                    aml.partner_id,
                    aml.move_id,
                    am.name AS move_name,
                    am.invoice_date AS invoice_date,
                    am.invoice_date_due AS invoice_due_date,
                    am.state AS state,
                    aml.name AS entry_label,
                    aml.debit,
                    aml.credit,
                    aml.debit - aml.credit AS balance,
                    aml.account_id,
                    aml.company_currency_id AS currency_id,
                    aml.reconciled,
                    aml.company_id AS company_id,

                    (
                        SELECT key::int
                        FROM jsonb_each(aml.analytic_distribution::jsonb)
                        LIMIT 1
                    ) AS analytic_account_id,

                    CASE
                        WHEN aml.tax_line_id IS NOT NULL THEN aml.tax_line_id
                        ELSE NULL
                    END AS tax_id,

                    aml.tax_base_amount,

                    CASE
                        WHEN aml.tax_line_id IS NOT NULL THEN aml.balance
                        ELSE 0.0
                    END AS tax_amount,

                    aml.date_maturity AS due_date,

                    CASE
                        WHEN acc.account_type IN ('asset_receivable', 'liability_payable') THEN aml.amount_residual
                        ELSE 0.0
                    END AS due_amount,

                    CASE
                        WHEN acc.account_type IN ('asset_receivable', 'liability_payable') AND aml.date_maturity IS NOT NULL
                            THEN (CURRENT_DATE - aml.date_maturity)
                        ELSE 0
                    END AS due_days,

                    CASE
                        WHEN aml.reconciled = TRUE THEN 'Paid'
                        WHEN aml.reconciled = FALSE AND acc.account_type NOT IN ('asset_receivable', 'liability_payable') THEN 'N/A'
                        WHEN aml.reconciled = FALSE AND aml.date_maturity IS NULL THEN 'Open'
                        WHEN aml.reconciled = FALSE AND aml.date_maturity IS NOT NULL AND aml.date_maturity < CURRENT_DATE THEN 'Overdue'
                        WHEN aml.reconciled = FALSE AND aml.date_maturity IS NOT NULL AND aml.date_maturity >= CURRENT_DATE THEN 'Open'
                        ELSE 'Unknown'
                    END AS status

                FROM account_move_line aml
                JOIN account_move am ON aml.move_id = am.id
                JOIN account_account acc ON aml.account_id = acc.id

                WHERE aml.partner_id IS NOT NULL
                AND aml.amount_residual != 0
                
                AND (
                    acc.account_type IN ('asset_receivable', 'liability_payable')
                    OR (
                        acc.account_type = 'liability_current'
                        AND acc.name::text NOT ILIKE '%VAT%'
                    )
                )

            )
        """)
