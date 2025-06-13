def get_status_label(level: float) -> str:
    if level < 70:
        return "dehydrated"
    elif level < 85:
        return "slightly_dehydrated"
    else:
        return "hydrated"

def format_status_for_coach(status: str) -> str:
    return f"Status changed to {status.replace('_', ' ').capitalize()}"