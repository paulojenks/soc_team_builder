"""Job Skills"""
PYTHON = 'Python'
DJANGO = 'Django'
FLASK = 'Flask'
CSS = 'css'
JAVASCRIPT = 'JavaScript'

SKILLS = (
    (None, ''),
    (PYTHON, 'Python'),
    (DJANGO, 'Django'),
    (FLASK, 'Flask'),
    (CSS, 'CSS'),
    (JAVASCRIPT, 'JavaScript')
)

"""Job Position Statuses"""
FILLED = 'filled'
OPEN = 'open'

STATUS = (
    (FILLED, 'Filled'),
    (OPEN, 'Open')
)

"""Application Status"""
APPROVED = 'approved'
DENIED = 'denied'
UNDECIDED = 'undecided'

APP_STATUS = (
    (APPROVED, 'Approved'),
    (DENIED, 'Denied'),
    (UNDECIDED, 'Undecided')
)