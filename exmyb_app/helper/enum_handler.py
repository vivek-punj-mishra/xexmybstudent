from enum import Enum, unique


@unique
class ProjectStatus(Enum):
    DRAFT = 'draft'
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DROP = 'drop'
    ACTIVE = 'active'
    CLOSED = 'closed'


@unique
class LeadStatus(Enum):
    PENDING = 'Pending'
    NOT_QUALIFIED = 'Not Qualified'
    LOST_LEAD = 'Lost Lead'
    JUNK_LEAD = 'Junk Lead'
    CONTACTED = 'Contacted'
    CONTACT_IN_FUTURE = 'Contact in Future'
    ATTEMPTED_TO_CONTACT = 'Attempted to Contact'


@unique
class DealStage(Enum):
    QUALIFICATION = 'Qualification'
    IDENTIFICATION_OF_DECISION_MAKERS = 'Identification of Decision Makers'
    SCOPING = 'Scoping'
    SUPPLY_ALIGNMENT = 'supply alignment'
    VENDOR_CALLS = 'vendor calls'
    PROPOSAL = 'Proposal'
    NEGOTIATION = 'Negotiation'
    DOCUMENTATION = 'Documentation'
    CLOSED_LOST = 'Closed-Lost'
    CLOSED_WON = 'Closed-Won'
    REQUIREMENT_GATHERING = 'Requirement Gathering'
    ANALYSIS = 'Analysis'
    DESIGN = 'Design'
    DEPLOYMENT = 'Deployment'
    MAINTENANCE = 'Maintenance'
    IDENTIFY_DECISION_MAKERS = 'Identify Decision Makers'


@unique
class ReportIssue(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    CRITICAL = 'critical'
    IN_PROGRESS = 'in_progress'
    REJECTED = 'rejected'
    CLOSED = 'closed'
