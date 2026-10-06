# Copyright 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models
from odoo.tools import SQL


class ProductTemplate(models.Model):
    _inherit = ["multi.company.abstract", "product.template"]
    _name = "product.template"

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        compute="_compute_company_id",
        search="_search_company_id",
        inverse="_inverse_company_id",
        compute_sql="_compute_sql_company_id",
        compute_sudo=False,
    )

    def _compute_sql_company_id(self, table):
        company = (
            self.env.context.get("_check_company_source_id")
            or self.env.context.get("force_company")
            or self.env.company.id
        )
        if isinstance(company, models.BaseModel):
            company = company.id
        company_field = self._fields["company_ids"]
        rel = SQL.identifier(company_field.relation)
        column1 = SQL.identifier(company_field.column1)
        column2 = SQL.identifier(company_field.column2)
        return SQL(
            """CASE WHEN EXISTS (
                SELECT 1 FROM %s rel
                WHERE rel.%s = %s AND rel.%s = %s
            ) THEN %s ELSE (
                SELECT rel.%s FROM %s rel
                WHERE rel.%s = %s
                ORDER BY rel.%s
                LIMIT 1
            ) END""",
            rel,
            column1,
            table.id,
            column2,
            company or 0,
            company or 0,
            column2,
            rel,
            column1,
            table.id,
            column2,
        )
