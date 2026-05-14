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
    box_qty = fields.Integer(string="Boxes", readonly=True)
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

    def _get_box_sqft_values(self, product, requested_sqft):
        sqft_per_box = product.sqft_per_box
        if (
            not product.use_box_sqft_calculation
            or sqft_per_box <= 0
            or requested_sqft <= 0
        ):
            return {}

        boxes = math.ceil(requested_sqft / sqft_per_box)
        return {
            "box_qty": boxes,
            "product_uom_qty": boxes * sqft_per_box,
        }

    @api.onchange("product_id", "requested_sqft", "sqft_per_box")
    def _onchange_flooring_requested_sqft(self):
        for line in self:
            values = line._get_box_sqft_values(line.product_id, line.requested_sqft)
            for field_name, value in values.items():
                line[field_name] = value

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product_id = vals.get("product_id")
            requested_sqft = vals.get("requested_sqft")
            if product_id and requested_sqft:
                product = self.env["product.product"].browse(product_id)
                vals.update(self._get_box_sqft_values(product, requested_sqft))
        return super().create(vals_list)

    def write(self, vals):
        if len(self) == 1 and {"product_id", "requested_sqft"} & set(vals):
            product = self.env["product.product"].browse(
                vals.get("product_id", self.product_id.id)
            )
            requested_sqft = vals.get("requested_sqft", self.requested_sqft)
            vals = dict(vals)
            vals.update(self._get_box_sqft_values(product, requested_sqft))
        return super().write(vals)


class StockMove(models.Model):
    _inherit = "stock.move"

    received_box_qty = fields.Integer(string="Received Boxes")
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

    @api.onchange("product_id", "received_box_qty")
    def _onchange_received_box_qty(self):
        for move in self:
            if (
                not move.product_id.use_box_sqft_calculation
                or move.sqft_per_box <= 0
                or move.received_box_qty <= 0
            ):
                continue

            move.quantity = move.received_box_qty * move.sqft_per_box
