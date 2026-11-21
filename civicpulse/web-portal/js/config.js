const CONFIG = {
  API_BASE_URL: 'http://127.0.0.1:8000/api',
  USE_MOCK_FALLBACK: true,

  // Default West Bengal Municipality coordinates
  DEFAULT_CENTER: [22.8914, 88.3972],
  DEFAULT_ZOOM: 14,

  CATEGORIES: {
    1: 'Roads & Potholes',
    2: 'Garbage & Sanitation',
    3: 'Drainage & Waterlogging',
    4: 'Streetlights & Electricity',
    5: 'Water Supply',
    6: 'Public Infrastructure',
    7: 'Other Civic Issues',
  },

  STATUS_LABELS: {
    submitted: 'Submitted',
    under_review: 'Under Review',
    accepted: 'Accepted',
    in_progress: 'In Progress',
    resolved: 'Resolved',
    rejected: 'Rejected',
    reopened: 'Reopened',
  },

  // Demo data used only when FastAPI is offline & USE_MOCK_FALLBACK is true
  MOCK_COMPLAINTS: [
    {
      complaint_id: 1042,
      category_id: 1,
      description: 'Severe pothole crater near Station Rd Bus Stand causing traffic congestion',
      latitude: 22.8932,
      longitude: 88.3955,
      status: 'in_progress',
      priority_score: 86.0,
      votes: 42,
      department: 'PWD Roads',
      image_url: null,
      resolution_image_url: null,
      created_at: '2026-11-16T09:15:00Z',
      history: [
        { status: 'submitted', timestamp: '2026-11-16T09:15:00Z', note: 'Citizen submitted report with GPS pin.' },
        { status: 'under_review', timestamp: '2026-11-16T14:20:00Z', note: 'Flagged for municipal verifier inspection.' },
        { status: 'accepted', timestamp: '2026-11-17T10:05:00Z', note: 'Verified by Admin; assigned to PWD Roads.' },
        { status: 'in_progress', timestamp: '2026-11-18T11:30:00Z', note: 'Repair crew dispatched to Station Rd.' },
      ],
    },
    {
      complaint_id: 1038,
      category_id: 3,
      description: 'Blocked storm drain causing street waterlogging outside Ward 08 Market',
      latitude: 22.8901,
      longitude: 88.4004,
      status: 'accepted',
      priority_score: 92.0,
      votes: 68,
      department: 'Drainage Dept',
      image_url: null,
      resolution_image_url: null,
      created_at: '2026-11-15T08:40:00Z',
      history: [
        { status: 'submitted', timestamp: '2026-11-15T08:40:00Z', note: 'Citizen submitted drainage blockage report.' },
        { status: 'accepted', timestamp: '2026-11-15T16:10:00Z', note: 'Verified and escalated to High Priority.' },
      ],
    },
    {
      complaint_id: 1029,
      category_id: 4,
      description: 'Three LED street poles out on College Link Road',
      latitude: 22.8885,
      longitude: 88.3931,
      status: 'resolved',
      priority_score: 74.0,
      votes: 29,
      department: 'Electrical Dept',
      image_url: null,
      resolution_image_url: null,
      created_at: '2026-11-10T18:20:00Z',
      history: [
        { status: 'submitted', timestamp: '2026-11-10T18:20:00Z', note: 'Reported dark pedestrian stretch.' },
        { status: 'in_progress', timestamp: '2026-11-12T10:00:00Z', note: 'Electrical unit replacing faulty ballasts.' },
        { status: 'resolved', timestamp: '2026-11-13T17:45:00Z', note: 'All 3 LED poles restored and tested.' },
      ],
    },
  ],

  MOCK_ANALYTICS: {
    active_reports: 451,
    total_votes: 3820,
    verified_percentage: 89,
    resolved_count: 485,
  },
};