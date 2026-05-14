def pre_init_hook(env):
    """Reuse an existing Floorings category instead of creating a duplicate."""
    env.cr.execute(
        """
        SELECT id
          FROM product_category
         WHERE name = %s
         LIMIT 1
        """,
        ("Floorings",),
    )
    category = env.cr.fetchone()
    if not category:
        return

    env.cr.execute(
        """
        SELECT 1
          FROM ir_model_data
         WHERE module = %s
           AND name = %s
         LIMIT 1
        """,
        ("flooring_box_qty", "product_category_floorings"),
    )
    if env.cr.fetchone():
        return

    env.cr.execute(
        """
        INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            "flooring_box_qty",
            "product_category_floorings",
            "product.category",
            category[0],
            True,
        ),
    )
