# 12-dimension compatibility vector, each 0-100. Order matters: 4 dims per category.
TRAITS = [
    # financial
    "spending_style",        # 0 frugal .. 100 lavish
    "financial_planning",    # 0 spontaneous .. 100 disciplined
    "provider_expectation",  # 0 strict 50/50 .. 100 traditional provider dynamic
    "wealth_priority",       # 0 low .. 100 high
    # nightlife
    "nightlife_frequency",   # 0 never .. 100 every weekend
    "social_energy",         # 0 introvert .. 100 extrovert
    "party_comfort",         # 0 avoids alcohol/clubs .. 100 very comfortable
    "spontaneity",           # 0 planner .. 100 spontaneous
    # goals
    "career_ambition",
    "family_orientation",
    "commitment_seriousness",
    "relationship_exclusivity",  # 0 open/flexible .. 100 strictly exclusive
]
DIM = len(TRAITS)
CATEGORIES = {"financial": (0, 4), "nightlife": (4, 8), "goals": (8, 12)}
WEIGHTS = {"financial": 0.35, "nightlife": 0.25, "goals": 0.40}
