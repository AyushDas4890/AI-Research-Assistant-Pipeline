"""Ad QA configuration knobs.

Everything here is a *starting point*, not ground truth: real banned-word
lists, platform specs, and disclaimer rules should be customized for your
brand and the platforms you actually run ads on, and cross-checked against
each platform's current policy pages before this is trusted for real
submissions.
"""

PLATFORM_SPECS = {
    "google_display": {
        "label": "Google Display Ads",
        "valid_sizes_px": [
            (300, 250), (336, 280), (728, 90), (300, 600), (160, 600),
            (320, 50), (970, 250), (250, 250), (200, 200), (320, 100),
        ],
        "max_file_size_kb": 150,
        "allowed_formats": ["jpg", "jpeg", "png", "gif"],
    },
    "meta": {
        "label": "Meta (Facebook/Instagram) Feed Ads",
        "min_resolution_px": (1080, 1080),
        "recommended_ratios": ["1:1", "4:5", "1.91:1"],
        "max_file_size_mb": 30,
        "allowed_formats": ["jpg", "jpeg", "png"],
    },
    "linkedin": {
        "label": "LinkedIn Single Image Ads",
        "valid_sizes_px": [(1200, 627), (1080, 1080), (1080, 1350)],
        "max_file_size_mb": 5,
        "allowed_formats": ["jpg", "jpeg", "png"],
    },
}

DEFAULT_PLATFORM = "google_display"

# Copy length limits many platforms enforce (characters).
COPY_LIMITS = {
    "google_display": {"headline": 30, "body_copy": 90},
    "meta": {"headline": 40, "body_copy": 125},
    "linkedin": {"headline": 70, "body_copy": 150},
}

# Fast, deterministic red flags in ad copy, checked before the LLM call so
# obvious problems don't depend on model availability.
BANNED_OR_RISKY_TERMS = [
    "guaranteed", "guarantee", "cure", "miracle", "risk-free", "no risk",
    "100% free", "act now", "limited time only", "#1 rated", "best in the world",
    "clinically proven", "doctor recommended", "fda approved",
]

# Claim categories that typically require a disclaimer/disclosure. This is a
# coarse keyword trigger, not a legal compliance check.
DISCLAIMER_TRIGGER_KEYWORDS = {
    "testimonial": ["results may vary", "individual results"],
    "earnings": ["not typical", "no guarantee of income"],
    "health": ["consult your doctor", "individual results may vary"],
    "finance": ["terms apply", "subject to approval", "not financial advice"],
}
