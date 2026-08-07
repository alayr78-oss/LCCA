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

def validate_asset_payload(data):
    if not data:
        return False, "Empty payload received.", "payload"
    
    project_id = data.get('project_id')
    if not project_id:
        return False, "Project ID is required.", "project_id"

    try:
        start_km = float(data.get('location_start_km', 0))
        end_km = float(data.get('location_end_km', 0))
        if start_km < 0 or end_km < 0:
            return False, "Chainage must be non-negative.", "location_start_km"
        if start_km >= end_km:
            return False, "Start chainage must be less than end chainage.", "location_start_km"
    except (ValueError, TypeError):
        return False, "Chainage must be valid numbers.", "location_start_km"
        
    try:
        year = int(data.get('install_year', 0))
        if year < 1800 or year > 2100:
            return False, "Install year must be realistic.", "install_year"
    except (ValueError, TypeError):
        return False, "Install year must be a valid year.", "install_year"

    return True, None, None

def validate_inspection_payload(data):
    if not data:
        return False, "Empty payload received.", "payload"
        
    if not data.get('asset_id'):
        return False, "Asset ID is required.", "asset_id"
        
    if not data.get('inspector') or not str(data.get('inspector')).strip():
        return False, "Inspector name is required.", "inspector"
        
    try:
        rating = float(data.get('condition_rating', 0))
        if rating < 0 or rating > 100:
            return False, "Condition rating must be between 0 and 100.", "condition_rating"
    except (ValueError, TypeError):
        return False, "Condition rating must be a valid number.", "condition_rating"

    return True, None, None
