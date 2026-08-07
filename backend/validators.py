def validate_project_payload(data):
    """
    Validates the POST /api/projects payload.
    Returns (is_valid, error_message, error_field)
    """
    if not data:
        return False, "Empty payload received.", "payload"

    # Name validation
    name = data.get('name')
    if not name or not str(name).strip():
        return False, "Project name is required and cannot be empty.", "name"

    # Analysis period validation
    analysis_period = data.get('analysis_period_years')
    try:
        if analysis_period is None or int(analysis_period) <= 0:
            return False, "Analysis period must be an integer greater than zero.", "analysis_period_years"
    except (ValueError, TypeError):
        return False, "Analysis period must be a valid number.", "analysis_period_years"

    # Track length validation
    track_length = data.get('track_length_km')
    try:
        if track_length is None or float(track_length) <= 0:
            return False, "Track length must be a positive number greater than zero.", "track_length_km"
    except (ValueError, TypeError):
        return False, "Track length must be a valid number.", "track_length_km"

    # Discount rate validation
    discount_rate = data.get('discount_rate')
    try:
        dr = float(discount_rate)
        if dr < 0 or dr > 1:
            return False, "Discount rate must be between 0 and 1.", "discount_rate"
    except (ValueError, TypeError):
        return False, "Discount rate must be a valid number.", "discount_rate"

    return True, None, None
