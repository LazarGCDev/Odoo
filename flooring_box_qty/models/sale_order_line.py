import math

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sqft_per_box = fields.Float(string="Sq Ft per Box")


class ProductProduct(models.Model):
    _inherit = "product.product"

    sqft_per_box = fields.Float(
        related="product_tmpl_id.sqft_per_box",
        string="Sq Ft per Box",
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

    @api.onchange("product_id", "requested_sqft")
    def _onchange_flooring_requested_sqft(self):
        flooring_category = self.env.ref(
            "flooring_box_qty.product_category_floorings",
            raise_if_not_found=False,
        )
        if not flooring_category:
            return

        for line in self:
            product = line.product_id
            requested_sqft = line.requested_sqft
            sqft_per_box = product.sqft_per_box

            if (
                product.categ_id != flooring_category
                or sqft_per_box <= 0
                or requested_sqft <= 0
            ):
                continue

            line.product_uom_qty = math.ceil(requested_sqft / sqft_per_box)
