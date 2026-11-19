# CivicPulse

> **Community Problem Intelligence Platform**

CivicPulse is a civic-tech platform designed to help communities report, validate, prioritize, assign, and track local civic problems through a connected citizen platform and administrative application.

Instead of treating every complaint as an isolated report, CivicPulse connects community participation with administrative decision-making to create a structured civic issue management workflow.

## Core Workflow

**REPORT → DETECT → VALIDATE → PRIORITIZE → ASSIGN → TRACK → LEARN**

## Key Features

### Citizen Platform

- Citizen registration and login
- Civic issue reporting
- Issue categories
- Description and image submission
- Location-based issue reporting
- Interactive map
- Nearby complaint discovery
- Community support/voting
- Complaint history
- Complaint status tracking
- Public issue visibility
- Civic statistics and transparency

### Administrative Application

- Secure administrator login
- Complaint management
- Complaint verification
- Duplicate complaint review
- Geographic duplicate detection
- Priority assessment
- Department assignment
- Complaint status management
- Resolution tracking
- Evidence and update management
- Geographic overview
- Administrative analytics
- Role-based access control

## Intelligent Processing

### Duplicate Detection

CivicPulse uses a combination of:

- Text similarity
- Geographic proximity

Potential duplicate complaints are identified for administrative review before they are merged or treated as duplicates.

### Priority Intelligence

CivicPulse uses a weighted scoring approach to help administrators prioritize issues.

The proposed priority factors are:

- Severity
- Community support
- Waiting time
- Area repetition

Proposed initial weighting:

| Factor | Weight |
|---|---:|
| Severity | 40% |
| Community Support | 25% |
| Waiting Time | 20% |
| Area Repetition | 15% |

The final decision remains under administrative control.

## Complaint Lifecycle

```text
Submitted
    ↓
Under Review
    ↓
Accepted
    ↓
In Progress
    ↓
Resolved
```

Additional paths may include:

```text
Submitted → Rejected
Resolved → Reopened
```

## System Architecture

```text
┌──────────────────────────┐
│     Citizen Website      │
│     HTML / CSS / JS      │
└────────────┬─────────────┘
             │
             │ REST API
             ▼
┌──────────────────────────┐
│      FastAPI Backend     │
│     Python REST API      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       PostgreSQL         │
│         Database         │
└──────────────────────────┘
             ▲
             │
             │ REST API
             │
┌────────────┴─────────────┐
│    Admin Desktop App     │
│       PySide6            │
│     Windows + macOS      │
└──────────────────────────┘
```

Both client applications communicate with the backend through APIs. Client applications do not directly access the database.

## Technology Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- FastAPI
- REST API

### Database

- PostgreSQL

### Admin Application

- Python
- PySide6
- Windows
- macOS

### Maps

- Leaflet
- OpenStreetMap

### Security

- Secure password hashing
- Authentication
- Role-based access control
- Input validation
- File-upload validation
- SQL injection protection
- Rate limiting
- HTTPS in deployment
- Audit logging
- Secure error handling
- Privacy-aware data exposure

## API

The backend is designed around RESTful API endpoints for communication between the citizen website, administrative application, and central database.

Planned API areas include:

```text
/auth
/users
/complaints
/votes
/duplicates
/priorities
/departments
/assignments
/status
/analytics
```

## Database

The proposed database contains entities such as:

- Users
- Complaints
- Categories
- Locations
- Votes/Support
- Duplicate Candidates
- Departments
- Assignments
- Status History
- Evidence
- Audit Logs

## Scalability

CivicPulse is initially designed for deployment within a single municipality.

The architecture is designed to support future expansion to:

- Multiple municipalities
- Multiple administrative organizations
- Larger complaint volumes
- Additional departments
- Government API integrations
- Cross-municipality analytics

## Future Scope

Potential future developments include:

- Government system/API integration
- Multi-municipality deployment
- Advanced analytics
- Improved duplicate detection
- Automated administrative insights
- Additional notification systems
- Broader civic data integration

## Project Status

CivicPulse is being developed as a prototype for **PRASUNEX INNOVATION 2026** by **Team CODE4CE** at **Academy of Technology**.

### Team

- Shreyan Biswas — Team Leader
- Tamanna Sarwar
- Souvik Roy Chowdhury
- Titlee Dalal

## Project Vision

CivicPulse aims to make community problems more visible, structured, measurable, and actionable by connecting citizen participation with administrative workflows.

**A Better Community Starts with Being Heard.**