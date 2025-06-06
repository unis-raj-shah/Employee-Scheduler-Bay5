"""Configuration settings for the warehouse scheduler application."""

import os
from typing import List, Dict, Any

# API Settings
WISE_API_HEADERS = {
    "authorization": os.getenv("WISE_API_KEY", "af6e1f16-943a-49ba-ba45-a135c85d4bd0"),
    "wise-company-id": os.getenv("WISE_COMPANY_ID", "ORG-1"),
    "wise-facility-id": os.getenv("WISE_FACILITY_ID", "F1"),
    "content-type": "application/json;charset=UTF-8",
    "user": os.getenv("WISE_USER", "rshah")
}

# Email Configuration
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.office365.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", "raj.shah@unisco.com"),
    "sender_password": os.getenv("SENDER_PASSWORD", "Raj@UNIS123"),
    "default_recipients": os.getenv("DEFAULT_RECIPIENTS", "raj.shah@unisco.com,mark.tuttle@unisco.com,john.diaz@unisco.com,steven.balbas@unisco.com,steven.garcia@unisco.com").split(',')
}

# Database Settings
DB_PATH = os.getenv("DB_PATH", "./chroma_db_vitacoco")

# Customer Settings
DEFAULT_CUSTOMER_ID = os.getenv("DEFAULT_CUSTOMER_ID", "ORG-34557")

# Role mappings for consistent matching
ROLE_MAPPINGS = {
    'forklift_driver': ['forklift', 'forklift driver', 'forklift operator', 'lift driver', 'Level 1 Forklift Driver', 'Level 2 Forklift Driver', 'Level 3 Forklift Driver'],
    'picker/packers': ['picker', 'packer', 'picker/packer', 'order picker', 'warehouse picker', 'General Labor', 'Quality Control'],
    'bendi_driver': ['bendi', 'bendi driver', 'bendi operator', 'reach truck'],
    'consolidation': ['consolidation', 'consolidator', 'inventory', 'inventory control'],
    'lumper': ['lumper', 'Lumper'],
    'receiver': ['receiver', 'receiving', 'inbound worker', 'dock worker'],
    'general labor': ['general labor', 'general worker', 'warehouse worker', 'laborer', 'picker', 'packer']
}

# Efficiency factor for workforce calculations (as a decimal)
WORKFORCE_EFFICIENCY = 0.85

# Work hours per shift
HOURS_PER_SHIFT = 7.5

# Default metrics summaries
DEFAULT_METRICS = {
    "inbound": {
        "avg_offload_time": 2.5,  # minutes per pallet
        "avg_scan_time": 0.15,     # minutes per pallet
        "avg_putaway_time": 2.5    # minutes per pallet
    },
    "picking": {
        "avg_pick_time": 3.0,   # minutes per case
        "avg_scan_time": 0.15,       # minutes per case
        "avg_wrap_time": 0.75        # minutes per pallet
    },
    "load": {
        "avg_load_time_per_pallet": 3.0  # minutes per pallet
    }
}

# Cases per pallet ratio
CASES_PER_PALLET = 75

# Default shift schedule
DEFAULT_SHIFT = {
    "start_time": "6:00 AM",
    "end_time": "2:30 PM",
    "lunch_duration": "30 Mins",
    "location": "Buena Park, CA"
}