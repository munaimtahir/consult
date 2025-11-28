"""
Core Constants
Shared constants used across the application.
"""

# Urgency level colors for UI display
URGENCY_COLORS = {
    'EMERGENCY': 'red',
    'URGENT': 'orange',
    'ROUTINE': 'blue'
}

# Status colors for UI display
STATUS_COLORS = {
    'PENDING': 'yellow',
    'ACKNOWLEDGED': 'blue',
    'IN_PROGRESS': 'indigo',
    'COMPLETED': 'green',
    'CANCELLED': 'gray'
}


def get_urgency_color(urgency):
    """Returns the color code for an urgency level.

    Args:
        urgency: The urgency level string.

    Returns:
        Color code string (for frontend styling).
    """
    return URGENCY_COLORS.get(urgency, 'gray')


def get_status_color(status):
    """Returns the color code for a status.

    Args:
        status: The status string.

    Returns:
        Color code string (for frontend styling).
    """
    return STATUS_COLORS.get(status, 'gray')
