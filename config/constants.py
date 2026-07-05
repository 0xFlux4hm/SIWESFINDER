"""
Application constants
"""

# Job Types
JOB_TYPES = {
    'SIWES': 'SIWES',
    'INTERNSHIP': 'Internship',
    'INDUSTRIAL_TRAINING': 'Industrial Training',
    'GRADUATE_TRAINEE': 'Graduate Trainee',
    'ENTRY_LEVEL': 'Entry Level',
}

# Locations
NIGERIAN_LOCATIONS = {
    'ABUJA': 'Abuja',
    'LAGOS': 'Lagos',
    'KADUNA': 'Kaduna',
    'KANO': 'Kano',
    'REMOTE': 'Remote',
}

# Role Categories
ROLE_CATEGORIES = {
    'SOFTWARE_ENGINEERING': 'Software Engineering',
    'CYBERSECURITY': 'Cybersecurity',
    'DATA_ANALYSIS': 'Data Analysis',
    'NETWORKING': 'Networking',
    'IT_SUPPORT': 'IT Support',
    'AI_ML': 'AI/Machine Learning',
    'CLOUD_COMPUTING': 'Cloud Computing',
    'DEVOPS': 'DevOps',
}

# Ranking Weights
RANKING_WEIGHTS = {
    'cybersecurity_relevance': 0.20,
    'software_engineering_relevance': 0.20,
    'computer_science_relevance': 0.15,
    'stipend_amount': 0.20,
    'company_reputation': 0.15,
    'remote_availability': 0.05,
    'location_preference': 0.05,
}

# Keywords for Different Roles
CYBERSECURITY_KEYWORDS = [
    'cybersecurity', 'security', 'penetration', 'ethical hacking',
    'infosec', 'information security', 'vulnerability assessment',
    'security analysis', 'threat analysis', 'incident response',
]

SOFTWARE_ENGINEERING_KEYWORDS = [
    'software engineer', 'software developer', 'backend developer',
    'frontend developer', 'full stack', 'web developer',
    'python developer', 'java developer', 'development',
    'programmer', 'coding',
]

DATA_ANALYSIS_KEYWORDS = [
    'data analyst', 'data analysis', 'data science',
    'data scientist', 'analytics', 'business intelligence',
    'data engineering', 'database',
]

NETWORKING_KEYWORDS = [
    'network engineer', 'network administrator',
    'network support', 'telecommunications',
    'network security', 'cisco', 'ccna',
]

# Blacklisted Companies/Keywords
BLACKLISTED_KEYWORDS = [
    'pyramid', 'ponzi', 'mlm', 'multi-level',
    'nigerian prince', 'work from home make money fast',
]

# Valid Application States
APPLICATION_STATES = {
    'ACTIVE': 'active',
    'CLOSED': 'closed',
    'EXPIRED': 'expired',
}

# Telegram Command Descriptions
COMMAND_DESCRIPTIONS = {
    'start': 'Start the bot',
    'help': 'Show help information',
    'today': "Today's opportunities",
    'top': 'Top-ranked opportunities',
    'abuja': 'Opportunities in Abuja',
    'lagos': 'Opportunities in Lagos',
    'kaduna': 'Opportunities in Kaduna',
    'kano': 'Opportunities in Kano',
    'cyber': 'Cybersecurity opportunities',
    'software': 'Software engineering opportunities',
    'remote': 'Remote opportunities',
    'stipend': 'Opportunities with stipends',
}

# Emoji Mappings
EMOJIS = {
    'alert': '🚨',
    'company': '🏢',
    'position': '💼',
    'location': '📍',
    'money': '💰',
    'star': '⭐',
    'link': '🔗',
    'calendar': '📅',
    'clock': '🕐',
    'check': '✅',
    'x': '❌',
    'info': 'ℹ️',
    'warning': '⚠️',
}

# Pagination
RESULTS_PER_PAGE = 5
MAX_MESSAGE_LENGTH = 4096
