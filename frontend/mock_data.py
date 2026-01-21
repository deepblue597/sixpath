"""
Mock data generator for SixPaths application
Generates sample users, connections, and referrals
"""
import random
from datetime import datetime, timedelta

SECTORS = [
    "Technology",
    "Finance",
    "Healthcare",
    "Education",
    "Marketing",
    "Manufacturing"
]

COMPANIES = {
    "Technology": ["TechCorp", "DataSystems", "CloudNine", "CodeFactory", "ByteWorks"],
    "Finance": ["Global Bank", "FinServe", "InvestCo", "Capital Partners", "FinTech Solutions"],
    "Healthcare": ["HealthPlus", "MediCare Systems", "WellBeing Inc", "BioTech Labs", "CareFirst"],
    "Education": ["EduTech", "Learning Hub", "Academy Pro", "Skill Builders", "Knowledge Corp"],
    "Marketing": ["BrandWorks", "AdVantage", "Creative Studios", "Market Pros", "Digital Edge"],
    "Manufacturing": ["BuildCo", "Industrial Works", "ProduceCorp", "Factory Direct", "ManuTech"]
}

FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William",
    "Mia", "James", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper", "Henry", "Evelyn", "Alexander",
    "Abigail", "Michael", "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery", "Sebastian"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

RELATIONSHIP_CONTEXTS = [
    "Met at conference",
    "Former colleague",
    "University connection",
    "LinkedIn introduction",
    "Mutual friend",
    "Industry event",
    "Client relationship",
    "Mentor/mentee",
    "Professional group",
    "Project collaboration"
]

POSITIONS = [
    "Software Engineer", "Product Manager", "Data Analyst", "Marketing Manager",
    "Sales Director", "HR Manager", "Financial Analyst", "Operations Manager",
    "Business Development", "Consultant", "Team Lead", "Senior Developer",
    "VP of Engineering", "Account Executive", "Project Manager"
]


def generate_user_data(username="John Doe"):
    """Generate mock user profile data"""
    return {
        "id": 1,
        "name": username,
        "email": f"{username.lower().replace(' ', '.')}@example.com",
        "company": "TechCorp",
        "sector": "Technology",
        "phone": "+1 (555) 123-4567",
        "linkedin": f"linkedin.com/in/{username.lower().replace(' ', '-')}",
        "position": "Senior Product Manager"
    }


def generate_connections(num_connections=25):
    """Generate mock connection data"""
    connections = []
    used_names = set()
    
    for i in range(num_connections):
        # Generate unique name
        while True:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            if full_name not in used_names:
                used_names.add(full_name)
                break
        
        sector = random.choice(SECTORS)
        company = random.choice(COMPANIES[sector])
        
        # Generate random date within last 2 years
        days_ago = random.randint(1, 730)
        last_interaction = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        connection = {
            "id": i + 2,  # Start from 2 (user is 1)
            "name": full_name,
            "company": company,
            "sector": sector,
            "position": random.choice(POSITIONS),
            "phone": f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "linkedin": f"linkedin.com/in/{full_name.lower().replace(' ', '-')}",
            "email": f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com",
            "how_i_know_them": random.choice(RELATIONSHIP_CONTEXTS),
            "relationship_strength": round(random.uniform(3, 10), 1),
            "notes": f"Great professional contact in {sector}. {random.choice(['Very responsive', 'Helpful', 'Industry expert', 'Good communicator', 'Reliable partner'])}.",
            "last_interaction": last_interaction
        }
        connections.append(connection)
    
    return connections


def generate_referrals(connections, num_referrals=8):
    """Generate mock referral data from connections"""
    if not connections:
        return []
    
    referrals = []
    selected_connections = random.sample(connections, min(num_referrals, len(connections)))
    
    statuses = ["Pending", "Interview Scheduled", "Applied", "Rejected", "Accepted", "Under Review"]
    
    for i, connection in enumerate(selected_connections):
        days_ago = random.randint(1, 90)
        application_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        referral = {
            "id": i + 1,
            "referrer_id": connection["id"],
            "referrer_name": connection["name"],
            "company": connection["company"],
            "sector": connection["sector"],
            "position": random.choice(POSITIONS),
            "application_date": application_date,
            "status": random.choice(statuses),
            "notes": f"Referral for {random.choice(POSITIONS)} position. {random.choice(['Strong endorsement', 'Good fit', 'Excellent opportunity', 'Fast-growing company', 'Great team culture'])}.",
            "last_interaction": connection["last_interaction"]
        }
        referrals.append(referral)
    
    return referrals


def get_sector_color(sector):
    """Return consistent color for each sector"""
    colors = {
        "Technology": "#3B82F6",  # Blue
        "Finance": "#10B981",     # Green
        "Healthcare": "#EF4444",  # Red
        "Education": "#F59E0B",   # Amber
        "Marketing": "#8B5CF6",   # Purple
        "Manufacturing": "#6B7280" # Gray
    }
    return colors.get(sector, "#94A3B8")
