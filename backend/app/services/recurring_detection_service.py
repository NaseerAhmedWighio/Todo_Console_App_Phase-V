"""
Smart Recurring Task Detection Service
Automatically detects if a task should recur based on content analysis
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class RecurringDetectionService:
    """Service for detecting recurring task patterns"""

    # Keyword patterns for different recurrence types
    # Each pattern has keywords and a confidence boost
    PATTERNS = {
        "minutely": {
            "keywords": [
                # Time indicators
                "every minute",
                "minutely",
                "each minute",
                # Monitoring/checking
                "check",
                "monitor",
                "watch",
                "track",
                "poll",
                "refresh",
                "update",
                "sync",
                "fetch",
                # Alerts
                "alert",
                "notification",
                "reminder",
                "alarm",
                # Testing
                "test",
                "ping",
                "heartbeat",
                "status check",
                # Data
                "log",
                "record",
                "capture",
                "sample",
            ],
            "pattern": "minutely",
            "interval": 1,
            "confidence_boost": 0.15,
        },
        "daily": {
            "keywords": [
                # Routine keywords
                "every day",
                "daily",
                "each morning",
                "each evening",
                "every morning",
                "every evening",
                "every night",
                # Activities
                "breakfast",
                "lunch",
                "dinner",
                "brunch",
                "exercise",
                "walk",
                "run",
                "jog",
                "gym",
                "workout",
                "meditate",
                "meditation",
                "yoga",
                "stretch",
                "read",
                "reading",
                "journal",
                "journaling",
                "sleep",
                "bedtime",
                "wake up",
                "morning routine",
                "night routine",
                "skincare",
                "brush teeth",
                "practice",
                "study",
                "learn",
                "code",
                "coding",
                "write",
                "writing",
                "draw",
                "drawing",
                "pray",
                "prayer",
                "worship",
                # Health
                "medicine",
                "medication",
                "pills",
                "vitamins",
                "supplements",
                "insulin",
                "blood pressure",
                # Pets
                "feed dog",
                "feed cat",
                "walk dog",
                "pet feeding",
                # Household
                "clean",
                "tidy",
                "dishes",
                "laundry",
                "trash",
            ],
            "pattern": "daily",
            "interval": 1,
            "confidence_boost": 0.1,
        },
        "weekly": {
            "keywords": [
                # Time indicators
                "every week",
                "weekly",
                "every monday",
                "every tuesday",
                "every wednesday",
                "every thursday",
                "every friday",
                "every saturday",
                "every sunday",
                "weekend",
                "every weekday",
                "monday morning",
                "friday evening",
                # Activities
                "meeting",
                "standup",
                "sync",
                "review",
                "planning",
                "grocery",
                "shopping",
                "market",
                "costco",
                "trader",
                "church",
                "temple",
                "mosque",
                "sunday service",
                "date night",
                "family time",
                "game night",
                "clean house",
                "deep clean",
                "vacuum",
                "mop",
                "haircut",
                "hair cut",
                "barber",
                "salon",
                "therapy",
                "counseling",
                "session",
                "call mom",
                "call dad",
                "call parents",
                "family call",
                # Work
                "sprint",
                "scrum",
                "retrospective",
                "demo",
                "report",
                "status",
                "update",
            ],
            "pattern": "weekly",
            "interval": 1,
            "confidence_boost": 0.1,
        },
        "monthly": {
            "keywords": [
                # Time indicators
                "every month",
                "monthly",
                "beginning of month",
                "end of month",
                "start of month",
                "1st of month",
                "bill",
                "bills",
                "payment",
                "payments",
                "pay",
                "rent",
                "mortgage",
                "lease",
                "subscription",
                "subscriptions",
                "subscribe",
                "insurance",
                "premium",
                "policy",
                "loan",
                "loans",
                "credit card",
                "creditcard",
                "electricity",
                "electric",
                "water",
                "gas",
                "utilities",
                "internet",
                "wifi",
                "phone",
                "mobile",
                "cell phone",
                "streaming",
                "netflix",
                "spotify",
                "hulu",
                "disney",
                "gym membership",
                "club membership",
                "salary",
                "paycheck",
                "pay day",
                "payday",
                "invoice",
                "billing",
                "statement",
                "tax",
                "taxes",
                "vat",
                "deduction",
                "donation",
                "charity",
                "tithe",
                "storage",
                "cloud storage",
                "icloud",
                "dropbox",
                "software",
                "saas",
                "license",
                "renewal",
            ],
            "pattern": "monthly",
            "interval": 1,
            "confidence_boost": 0.15,  # Bills are usually monthly
        },
        "yearly": {
            "keywords": [
                # Time indicators
                "every year",
                "yearly",
                "annual",
                "annually",
                # Events
                "anniversary",
                "birthday",
                "anniversary",
                "tax return",
                "tax filing",
                "income tax",
                "renewal",
                "registration",
                "license",
                "certification",
                "certifications",
                "credentials",
                "checkup",
                "medical checkup",
                "dental",
                "eye exam",
                "inspection",
                "service",
                "maintenance",
                "vacation",
                "holiday",
                "trip",
                "travel",
                "gift",
                "presents",
                "christmas",
                "thanksgiving",
                "new year",
                "resolution",
                "car registration",
                "vehicle registration",
                "insurance renewal",
                "policy renewal",
                "membership",
                "association",
                "dues",
            ],
            "pattern": "yearly",
            "interval": 1,
            "confidence_boost": 0.1,
        },
    }

    # One-time task indicators (these override recurring patterns)
    ONE_TIME_INDICATORS = [
        # Purchase actions
        "buy",
        "purchase",
        "order",
        "book",
        "reserve",
        "schedule",
        # One-time qualifiers
        "one-time",
        "once",
        "single",
        "new",
        "first time",
        # Project-based
        "project",
        "launch",
        "release",
        "deploy",
        "migration",
        # Events
        "appointment",
        "interview",
        "exam",
        "test",
        "presentation",
        "concert",
        "show",
        "movie",
        "event",
        "conference",
        # Travel
        "flight",
        "hotel",
        "airbnb",
        "ticket",
        "visa",
        "passport",
        # Shopping
        "laptop",
        "phone",
        "computer",
        "camera",
        "tv",
        "furniture",
        "car",
        "bike",
        "vehicle",
        "appliance",
        # Documents
        "apply",
        "submit",
        "register",
        "enroll",
        "sign up",
        # Medical
        "surgery",
        "operation",
        "procedure",
        "vaccination",
        # Home
        "repair",
        "fix",
        "install",
        "replace",
        "renovate",
        # Career
        "resume",
        "cv",
        "portfolio",
        "application",
        "cover letter",
    ]

    def detect_recurring(
        self, title: str, description: Optional[str] = None, due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analyze task to determine if it should recur

        Args:
            title: Task title
            description: Optional task description
            due_date: Optional due date

        Returns:
            Dictionary with detection results:
            {
                'is_recurring': bool,
                'confidence': float (0.0 - 1.0),
                'pattern': str | None,
                'interval': int,
                'reason': str,
                'matched_keywords': List[str],
                'suggested': bool
            }
        """
        # Combine title and description for analysis
        text = f"{title} {(description or '')}".lower()

        # Step 1: Check for one-time indicators (these override recurring)
        one_time_matches = []
        for indicator in self.ONE_TIME_INDICATORS:
            if indicator in text:
                one_time_matches.append(indicator)

        # If we found one-time indicators with good confidence, don't suggest recurring
        if len(one_time_matches) >= 1:
            return {
                "is_recurring": False,
                "confidence": 0.85,
                "pattern": None,
                "interval": 0,
                "reason": f"Detected one-time task indicator: '{', '.join(one_time_matches)}'",
                "matched_keywords": one_time_matches,
                "suggested": False,
            }

        # Step 2: Check for recurring patterns
        best_match = None
        best_score = 0
        all_matched_keywords = []

        for pattern_type, config in self.PATTERNS.items():
            score = 0
            matched_keywords = []

            for keyword in config["keywords"]:
                if keyword in text:
                    score += 1
                    matched_keywords.append(keyword)

            # Apply confidence boost for certain patterns
            if matched_keywords:
                score += config.get("confidence_boost", 0)

            if score > best_score:
                best_score = score
                best_match = {"pattern_type": pattern_type, "config": config, "matched_keywords": matched_keywords}
                all_matched_keywords = matched_keywords

        # Step 3: If we found a match with sufficient confidence
        if best_match and best_score >= 1.0:
            # Calculate confidence based on number of matches
            confidence = min(0.5 + (best_score * 0.1), 0.95)

            return {
                "is_recurring": True,
                "confidence": confidence,
                "pattern": best_match["config"]["pattern"],
                "interval": best_match["config"]["interval"],
                "reason": f"Matched recurring keywords: {', '.join(best_match['matched_keywords'][:3])}",
                "matched_keywords": all_matched_keywords,
                "suggested": True,
            }

        # Step 4: Check due date patterns (if no keyword matches)
        if due_date:
            due_pattern = self._analyze_due_date_pattern(due_date)
            if due_pattern:
                return {
                    "is_recurring": True,
                    "confidence": 0.60,  # Lower confidence for date-based detection
                    "pattern": due_pattern["pattern"],
                    "interval": due_pattern["interval"],
                    "reason": "Inferred from due date context",
                    "matched_keywords": [],
                    "suggested": True,
                }

        # Step 5: Default - not recurring
        return {
            "is_recurring": False,
            "confidence": 0.75,
            "pattern": None,
            "interval": 0,
            "reason": "No recurring pattern detected",
            "matched_keywords": [],
            "suggested": False,
        }

    def _analyze_due_date_pattern(self, due_date: datetime) -> Optional[Dict]:
        """
        Analyze if due date suggests a recurring pattern

        Args:
            due_date: Task due date

        Returns:
            Pattern info or None
        """
        now = datetime.now()
        days_until_due = (due_date - now).days

        # If due date is far in future, might be monthly/yearly
        if days_until_due > 365:
            return {"pattern": "yearly", "interval": 1}
        elif days_until_due > 28:
            return {"pattern": "monthly", "interval": 1}

        return None

    def get_pattern_suggestions(self) -> Dict[str, List[str]]:
        """
        Get example keywords for each pattern (useful for UI hints)

        Returns:
            Dictionary mapping pattern names to example keywords
        """
        suggestions = {}
        for pattern_type, config in self.PATTERNS.items():
            # Get top 5 keywords as examples
            suggestions[pattern_type] = config["keywords"][:5]
        return suggestions


# Global instance
recurring_detection_service = RecurringDetectionService()


def get_recurring_detection_service() -> RecurringDetectionService:
    """Get the recurring detection service instance"""
    return recurring_detection_service
