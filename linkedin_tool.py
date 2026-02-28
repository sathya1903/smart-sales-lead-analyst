"""
linkedin_tool.py
Simulated LinkedIn enrichment tool.
Returns structured professional data for a given lead name.
In production, this would call a real LinkedIn API or data provider.
"""

import random
import hashlib
from typing import Dict, Any


# Seed data pools for deterministic-but-realistic fake profiles
JOB_TITLES = [
    "VP of Sales", "Head of Operations", "Chief Revenue Officer",
    "Director of Procurement", "IT Manager", "CEO", "COO",
    "Senior Buyer", "Business Development Manager", "CFO",
    "Director of Strategy", "Founder", "Managing Director",
]

INDUSTRIES = [
    "SaaS", "Manufacturing", "Healthcare", "Finance",
    "Retail", "Logistics", "Education", "Real Estate",
]

COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]

DECISION_MAKER_TITLES = {
    "vp", "chief", "cro", "ceo", "coo", "cfo",
    "director", "founder", "head", "managing",
}


def _seed_from_name(name: str) -> int:
    """Generate a deterministic integer seed from a name string."""
    return int(hashlib.md5(name.lower().encode()).hexdigest(), 16) % 10_000


def _is_decision_maker(title: str) -> bool:
    """Heuristic: check if the title implies purchasing authority."""
    title_lower = title.lower()
    return any(word in title_lower for word in DECISION_MAKER_TITLES)


def lookup_linkedin_profile(lead_name: str) -> Dict[str, Any]:
    """
    Simulate a LinkedIn profile lookup for a given lead.

    Args:
        lead_name: Full name of the sales lead.

    Returns:
        Dictionary with professional profile data.
    """
    seed = _seed_from_name(lead_name)
    rng = random.Random(seed)

    title = rng.choice(JOB_TITLES)
    company_size = rng.choice(COMPANY_SIZES)
    industry = rng.choice(INDUSTRIES)
    years_in_role = rng.randint(1, 12)
    connections = rng.randint(200, 4000)
    decision_maker = _is_decision_maker(title)

    # Seniority derived from title keywords
    title_lower = title.lower()
    if any(w in title_lower for w in ["chief", "ceo", "coo", "cro", "cfo", "founder"]):
        seniority = "C-Suite"
    elif any(w in title_lower for w in ["vp", "vice president", "director", "head", "managing"]):
        seniority = "Senior Leadership"
    elif any(w in title_lower for w in ["manager", "senior"]):
        seniority = "Mid-Level Management"
    else:
        seniority = "Individual Contributor"

    return {
        "lead_name": lead_name,
        "job_title": title,
        "industry": industry,
        "company_size": company_size,
        "seniority": seniority,
        "years_in_role": years_in_role,
        "connections": connections,
        "decision_maker": "Yes" if decision_maker else "No",
        "source": "LinkedIn (simulated)",
    }


def format_linkedin_result(profile: Dict[str, Any]) -> str:
    """Format a LinkedIn profile dict into a readable string for the LLM."""
    return (
        f"LinkedIn Profile for {profile['lead_name']}:\n"
        f"  Job Title: {profile['job_title']}\n"
        f"  Seniority: {profile['seniority']}\n"
        f"  Industry: {profile['industry']}\n"
        f"  Company Size: {profile['company_size']} employees\n"
        f"  Years in Role: {profile['years_in_role']}\n"
        f"  Decision Maker: {profile['decision_maker']}\n"
        f"  LinkedIn Connections: {profile['connections']}\n"
    )
