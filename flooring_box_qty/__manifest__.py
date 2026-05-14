{
    "name": "Flooring Box Quantity",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Calculate flooring sale quantities from requested square feet.",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "product",
    ],
    "data": [
        "data/product_category.xml",
        "views/sale_order_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "application": False,
}
