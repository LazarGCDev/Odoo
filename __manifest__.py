{
    "name": "Flooring Box Quantity",
    "version": "19.0.1.1.0",
    "category": "Sales/Sales",
    "summary": "Calculate flooring sale quantities from requested square feet.",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "product",
        "stock",
    ],
    "data": [
        "data/product_category.xml",
        "views/sale_order_views.xml",
        "views/sale_order_report_views.xml",
        "views/stock_picking_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "application": False,
}
