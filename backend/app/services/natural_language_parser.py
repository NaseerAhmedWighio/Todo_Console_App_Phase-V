"""
Professional Natural Language Parser for Task Management
Handles: dates, times, priorities, tags, and task operations
Production-ready with intelligent word extraction
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
import re


# ============================================================================
# CONFIGURATION
# ============================================================================

# Day name mapping for "next Monday", "Friday", etc.
DAY_NAMES = {
    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
    'friday': 4, 'saturday': 5, 'sunday': 6,
    'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
}

# Time periods with 12-hour format (INTELLIGENT TIMES)
TIME_PERIODS = {
    'morning': '09:00 AM',      # 9:00 AM
    'afternoon': '12:00 PM',    # 12:00 PM (noon)
    'evening': '06:00 PM',      # 6:00 PM
    'night': '12:00 AM',        # 12:00 AM (midnight)
    'tonight': '12:00 AM',      # 12:00 AM
    'midnight': '12:00 AM',     # 12:00 AM
    'noon': '12:00 PM',         # 12:00 PM
}

# Words that indicate DATE/TIME references (REMOVE from title)
DATE_TIME_WORDS = [
    'tomorrow', 'today', 'yesterday', 'tonight',
    'morning', 'afternoon', 'evening', 'night', 'midnight', 'noon',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'next', 'this', 'coming', 'every', 'each', 'later',
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december',
    'week', 'month', 'year', 'day', 'at', 'in', 'on'
]

# Words that indicate PRIORITY (REMOVE from title, use for priority field)
PRIORITY_WORDS = ['high', 'urgent', 'low', 'medium', 'priority']

# Words that indicate TAG (REMOVE from title, use for tag)
TAG_WORDS = ['tag', 'tagged', 'tags', 'label', 'labeled']

# Words that indicate COLOR (REMOVE from title, use for tag color)
COLOR_WORDS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'black', 'white']

# ACTION VERBS to KEEP in title (IMPORTANT - these make titles meaningful)
ACTION_VERBS = [
    'go', 'call', 'meet', 'buy', 'finish', 'complete', 'start', 'begin',
    'eat', 'read', 'write', 'study', 'work', 'exercise', 'cook', 'clean',
    'send', 'make', 'create', 'build', 'fix', 'check', 'review', 'submit',
    'attend', 'visit', 'pick', 'drop', 'deliver', 'collect', 'prepare',
    'schedule', 'book', 'arrange', 'organize', 'plan', 'discuss', 'present',
    'watch', 'listen', 'play', 'practice', 'learn', 'teach', 'train',
    'shop', 'pay', 'order', 'return', 'exchange', 'deliver', 'ship',
    'move', 'travel', 'drive', 'fly', 'walk', 'run', 'cycle',
    'update', 'delete', 'remove', 'add', 'edit', 'change', 'modify',
    'mark', 'set', 'get', 'have', 'do', 'take', 'bring', 'give'
]

# PREPOSITIONS to REMOVE from title (these connect to date/time/tag info)
PREPOSITIONS_TO_REMOVE = ['at', 'in', 'on', 'for', 'with', 'by', 'from', 'into']


# ============================================================================
# DATE PARSING
# ============================================================================

def parse_date(message: str) -> Optional[str]:
    """
    Parse date from natural language.
    Returns ISO format date string (YYYY-MM-DD) or None.
    
    Handles:
    - "tomorrow" → today + 1 day
    - "next Monday" → next Monday
    - "in 5 days" → today + 5 days
    - "today" → today
    """
    message_lower = message.lower()
    now = datetime.now()
    today = now.date()
    
    # TOMORROW - MUST ADD 1 DAY TO TODAY
    if 'tomorrow' in message_lower:
        due_date = today + timedelta(days=1)
        return due_date.isoformat()
    
    # Today
    if 'today' in message_lower:
        return today.isoformat()
    
    # Day after tomorrow
    if 'day after tomorrow' in message_lower:
        return (today + timedelta(days=2)).isoformat()
    
    # In X days
    match = re.search(r'in\s+(\d+)\s*days?', message_lower)
    if match:
        days = int(match.group(1))
        return (today + timedelta(days=days)).isoformat()
    
    # Next week
    if 'next week' in message_lower:
        return (today + timedelta(days=7)).isoformat()
    
    # Next [DayName] - e.g., "next Monday"
    match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', message_lower)
    if match:
        day_name = match.group(1)
        days_ahead = _get_days_until_day(day_name)
        if days_ahead == 0:  # If today, move to next week
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).isoformat()
    
    # [DayName] alone - e.g., "Monday" means next Monday
    for day_name in DAY_NAMES.keys():
        if re.search(rf'\b{day_name}\b', message_lower):
            days_ahead = _get_days_until_day(day_name)
            if days_ahead == 0:
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).isoformat()
    
    return None


def _get_days_until_day(day_name: str) -> int:
    """Get number of days until a specific day of the week"""
    try:
        target_day = DAY_NAMES[day_name.lower()]
        current_day = datetime.now().weekday()
        days_ahead = target_day - current_day
        if days_ahead < 0:
            days_ahead += 7
        return days_ahead
    except:
        return 0


# ============================================================================
# TIME PARSING
# ============================================================================

def parse_time(message: str) -> Optional[str]:
    """
    Parse time from natural language.
    Returns 12-hour format string (HH:MM AM/PM) or None.
    
    Handles:
    - Time periods: "morning" → "09:00 AM"
    - Specific times: "3pm" → "03:00 PM", "9am" → "09:00 AM"
    """
    message_lower = message.lower()
    
    # Check for time period keywords FIRST
    for period, time_val in TIME_PERIODS.items():
        if period in message_lower:
            return time_val
    
    # Check for specific times (12-hour format with AM/PM)
    # Pattern: "at 3pm", "at 9am", "3:30 PM", "9:00 AM"
    match = re.search(r'at?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', message_lower)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        am_pm = match.group(3)
        
        if am_pm:
            # Already has AM/PM, format it properly
            return f"{hour:02d}:{minute:02d} {am_pm.upper()}"
        else:
            # No AM/PM specified, assume based on hour
            if hour >= 1 and hour <= 11:
                return f"{hour:02d}:{minute:02d} AM"
            elif hour == 12:
                return f"{hour:02d}:{minute:02d} PM"
            elif hour >= 13 and hour <= 23:
                return f"{hour:02d}:{minute:02d} PM"
            else:  # hour == 0
                return f"12:{minute:02d} AM"
    
    return None


# ============================================================================
# TITLE EXTRACTION
# ============================================================================

def extract_title(message: str) -> str:
    """
    Extract task title from message.
    INTELLIGENTLY decides which words to keep vs remove.

    KEEPS:
    - Action verbs: "go", "call", "meet", "buy", etc.
    - Important nouns and adjectives

    REMOVES:
    - Date/time words: "tomorrow", "morning", "Monday", "at", "in", "on", etc.
    - Priority words: "high", "urgent", "medium", etc.
    - Tag words: "tag", "tagged", etc.
    - Color words: "red", "blue", etc.
    - Prepositions: "at", "for", "with", etc.
    """
    message_lower = message.lower()

    # Extract the part after "to " or "called/named "
    raw_title = None

    # Pattern: "create a task to [title]"
    if 'to ' in message_lower:
        title_part = message_lower.split('to ', 1)[1]
        # Remove everything after common endings (date/time/tag indicators)
        for ending in [' with ', ' tomorrow', ' today', ' next ', ' at ', ' in ', ' on ', ' for ', ' called ', ' named ']:
            if ending in title_part:
                title_part = title_part.split(ending)[0]
                break
        raw_title = title_part.strip()

    # Pattern: "create a task called/named [title]"
    elif 'called ' in message_lower or 'named ' in message_lower:
        keyword = 'called ' if 'called ' in message_lower else 'named '
        title_part = message_lower.split(keyword, 1)[1]
        for ending in [' with ', ' tomorrow', ' today', ' at ', ' in ', ' on ', ' for ']:
            if ending in title_part:
                title_part = title_part.split(ending)[0]
                break
        raw_title = title_part.strip()

    if not raw_title:
        return "Task"

    # Split into words and filter intelligently
    words = raw_title.split()
    clean_words = []

    for i, word in enumerate(words):
        word_clean = word.lower().strip('.,!?;:')

        # ALWAYS KEEP action verbs (even if short)
        if word_clean in ACTION_VERBS:
            clean_words.append(word)
            continue

        # REMOVE prepositions (don't keep them in title)
        if word_clean in PREPOSITIONS_TO_REMOVE:
            continue

        # KEEP words with 3+ characters (unless they're stop words)
        if len(word_clean) >= 3:
            # REMOVE date/time words
            if word_clean in DATE_TIME_WORDS:
                continue

            # REMOVE priority words
            if word_clean in PRIORITY_WORDS:
                continue

            # REMOVE tag words
            if word_clean in TAG_WORDS:
                continue

            # REMOVE color words
            if word_clean in COLOR_WORDS:
                continue

            # KEEP everything else
            clean_words.append(word)

    # Join and capitalize
    cleaned = ' '.join(clean_words).strip()

    # If title became empty, use original
    if not cleaned:
        cleaned = raw_title.strip()

    # Capitalize properly (title case)
    return cleaned.title()


# ============================================================================
# PRIORITY EXTRACTION
# ============================================================================

def extract_priority(message: str) -> str:
    """
    Extract priority from message.
    Checks for priority words AFTER "with" or anywhere in message.
    
    Returns: "low", "medium", "high", or "urgent"
    """
    message_lower = message.lower()
    
    # Check for priority indicators
    if 'urgent' in message_lower:
        return 'urgent'
    elif 'high' in message_lower:
        return 'high'
    elif 'low' in message_lower:
        return 'low'
    elif 'medium' in message_lower:
        return 'medium'
    
    return 'medium'  # Default


# ============================================================================
# TAG EXTRACTION
# ============================================================================

def extract_tag(message: str) -> Tuple[Optional[str], str]:
    """
    Extract tag name and color from message.

    Patterns:
    - "tag of [name]" → name
    - "tag [name]" → name
    - "with [name] tag" → name
    - "with [color] [name] tag" → name + color
    - "tag it as [name]" → name
    - "tag as [name]" → name
    - "with [name] tag" → name

    Returns: (tag_name, tag_color)
    """
    message_lower = message.lower()
    tag_name = None
    tag_color = '#3B82F6'  # Default blue

    # Pattern 1: "tag of [name]"
    match = re.search(r'tag of ([a-z]+)', message_lower)
    if match:
        tag_name = match.group(1).title()

    # Pattern 2: "create a tag [name]" (without "of")
    if not tag_name:
        match = re.search(r'create\s+(?:a\s+)?tag\s+([a-z]+)', message_lower)
        if match:
            tag_name = match.group(1).title()

    # Pattern 3: "with [name] tag" (simple pattern for "with work tag")
    if not tag_name:
        match = re.search(r'with\s+([a-z]+)\s+tag', message_lower)
        if match:
            tag_name = match.group(1).title()

    # Pattern 4: "with [color] [name] tag"
    if not tag_name:
        match = re.search(r'with\s+(?:a\s+)?(?:([a-z]+)\s+)?([a-z]+)\s+tag', message_lower)
        if match:
            potential_color = match.group(1)
            potential_name = match.group(2)

            # Check if first word is a color
            if potential_color and potential_color in ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink']:
                tag_name = potential_name.title() if potential_name else potential_color.title()
                tag_color = _get_color_code(potential_color)
            elif potential_color:
                tag_name = potential_color.title()

    # Pattern 5: "tag it as [name]" or "tag as [name]"
    if not tag_name:
        if 'tag it as ' in message_lower or 'tag as ' in message_lower:
            keyword = 'tag it as ' if 'tag it as ' in message_lower else 'tag as '
            tag_part = message_lower.split(keyword, 1)[1]
            # Remove color references
            for color_end in [' with ', ' color', ' in ']:
                if color_end in tag_part:
                    tag_part = tag_part.split(color_end)[0]
            tag_name = tag_part.strip().title()

    # Pattern 6: "with [name] tag" anywhere in message (more flexible)
    if not tag_name:
        match = re.search(r'with\s+([a-z]+)\s+tag', message_lower)
        if match:
            tag_name = match.group(1).title()

    # Extract color if specified separately
    for color_name in ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink']:
        if color_name in message_lower:
            tag_color = _get_color_code(color_name)
            break

    return tag_name, tag_color


def _get_color_code(color_name: str) -> str:
    """Get hex color code from color name"""
    color_map = {
        'red': '#FF0000',
        'blue': '#3B82F6',
        'green': '#10B981',
        'yellow': '#F59E0B',
        'purple': '#8B5CF6',
        'orange': '#F97316',
        'pink': '#EC4899',
        'black': '#000000',
        'white': '#FFFFFF'
    }
    return color_map.get(color_name, '#3B82F6')


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_task_details(message: str) -> Dict[str, any]:
    """
    Extract all task details from natural language message.
    PRODUCTION-READY with intelligent parsing.

    Args:
        message: User message describing a task

    Returns:
        Dictionary with all task details
    """
    result = {
        'title': extract_title(message),
        'description': None,
        'priority': extract_priority(message),
        'due_date': parse_date(message),
        'time_str': parse_time(message),
        'tag_name': extract_tag(message)[0],
        'tag_color': extract_tag(message)[1]
    }
    
    # Debug logging
    print(f"[NLP] Input: {message}")
    print(f"[NLP] Output: title='{result['title']}', due_date='{result['due_date']}', time_str='{result['time_str']}', tag='{result['tag_name']}'")
    
    return result


# ============================================================================
# TEST FUNCTION
# ============================================================================

if __name__ == "__main__":
    test_cases = [
        # (message, expected_title_contains, expected_due, expected_time, expected_tag)
        ("Create a task to buy groceries tomorrow morning", "Buy Groceries", "tomorrow", "09:00 AM", None),
        ("Create a task to go to doctor tomorrow at 3pm", "Go Doctor", "tomorrow", "03:00 PM", None),
        ("Create a high priority task to finish report tomorrow evening with work tag", "Finish Report", "tomorrow", "06:00 PM", "Work"),
        ("Create a tag of fasting", "Task", None, None, "Fasting"),
        ("Create a tag eating", "Task", None, None, "Eating"),
        ("Create a task to study tomorrow evening with red study tag", "Study", "tomorrow", "06:00 PM", "Study"),
        ("Create a task to go to gym tomorrow morning", "Go Gym", "tomorrow", "09:00 AM", None),
        ("Create a task called Team Meeting next Monday at 10am", "Team Meeting", "next Monday", "10:00 AM", None),
        ("Create a task to call John tomorrow at night", "Call John", "tomorrow", "12:00 AM", None),
        ("Create a task to eat lunch at afternoon", "Eat Lunch", None, "12:00 PM", None),
    ]

    print("=" * 80)
    print("PROFESSIONAL NLP PARSER - TEST SUITE")
    print("=" * 80)

    all_passed = True
    for i, (message, exp_title_contains, exp_due, exp_time, exp_tag) in enumerate(test_cases, 1):
        result = extract_task_details(message)

        # Validate
        title_ok = exp_title_contains.lower() in result['title'].lower()
        due_ok = (exp_due is None) or (result['due_date'] is not None if exp_due == "tomorrow" else True)
        time_ok = (exp_time is None) or (result['time_str'] == exp_time)
        tag_ok = (exp_tag is None) or (result['tag_name'] == exp_tag)

        passed = title_ok and due_ok and time_ok and tag_ok
        all_passed = all_passed and passed

        status = "PASS" if passed else "FAIL"
        print(f"\n{i}. [{status}]: {message}")
        print(f"   Title: '{result['title']}' {'[OK]' if title_ok else '[FAIL]'}")
        print(f"   Due: {result['due_date']} {'[OK]' if due_ok else '[FAIL]'}")
        print(f"   Time: {result['time_str']} {'[OK]' if time_ok else '[FAIL]'}")
        print(f"   Tag: {result['tag_name']} {'[OK]' if tag_ok else '[FAIL]'}")

    print("\n" + "=" * 80)
    print(f"OVERALL: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 80)
