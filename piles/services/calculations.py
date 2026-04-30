def calculate_pile(pile):
    """
    Core calculation engine
    Replace this gradually with your full Excel logic
    """

    Le = pile.design_depth_m - pile.cutoff

    # --- ZONING ---
    if pile.cage_type.lower() == "zoned":
        top_zone = 0.4 * Le
        bottom_zone = 0.6 * Le
    else:
        top_zone = Le
        bottom_zone = Le

    # --- SIMPLE BAR LOGIC (placeholder) ---
    total_length = top_zone + bottom_zone

    # --- WEIGHT (approx: kg/m rule) ---
    # later replace with real formula: d^2/162
    total_weight = total_length * 100

    return {
        "Le": Le,
        "top_zone": top_zone,
        "bottom_zone": bottom_zone,
        "total_length": total_length,
        "total_weight": total_weight
    }

    