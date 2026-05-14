import math

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    use_box_sqft_calculation = fields.Boolean(string="Use Box Sq Ft Calculation")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sqft_per_box = fields.Float(string="Sq Ft per Box")
    use_box_sqft_calculation = fields.Boolean(
        string="Use Box Sq Ft Calculation",
        compute="_compute_use_box_sqft_calculation",
    )

    @api.depends("categ_id", "categ_id.use_box_sqft_calculation", "categ_id.parent_path")
    def _compute_use_box_sqft_calculation(self):
        for template in self:
            category = template.categ_id
            template.use_box_sqft_calculation = False
            while category:
                if category.use_box_sqft_calculation:
                    template.use_box_sqft_calculation = True
                    break
                category = category.parent_id


class ProductProduct(models.Model):
    _inherit = "product.product"

    sqft_per_box = fields.Float(
        related="product_tmpl_id.sqft_per_box",
        string="Sq Ft per Box",
        readonly=True,
    )
    use_box_sqft_calculation = fields.Boolean(
        related="product_tmpl_id.use_box_sqft_calculation",
        string="Use Box Sq Ft Calculation",
        readonly=True,
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    requested_sqft = fields.Float(string="Requested Sq Ft")
    sqft_per_box = fields.Float(
        related="product_id.sqft_per_box",
        string="Sq Ft per Box",
        readonly=True,
    )
    use_box_sqft_calculation = fields.Boolean(
        related="product_id.use_box_sqft_calculation",
        string="Use Box Sq Ft Calculation",
        readonly=True,
    )

    @api.onchange("product_id", "requested_sqft")
    def _onchange_flooring_requested_sqft(self):
        for line in self:
            product = line.product_id
            requested_sqft = line.requested_sqft
            sqft_per_box = product.sqft_per_box

            if (
                not product.use_box_sqft_calculation
                or sqft_per_box <= 0
                or requested_sqft <= 0
            ):
                continue

            line.product_uom_qty = math.ceil(requested_sqft / sqft_per_box)
