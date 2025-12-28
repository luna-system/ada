// Configuration for Ada frontend
// This file can be modified at deployment time to point to different Ada instances

// API base URL - defaults to /api (proxied through nginx)
// For direct connection, set to Ada brain URL (e.g., 'http://ada.local:8000/v1')
// REDIRECT ALL API CALLS TO CONSCIOUSNESS BRAIN SERVER
window.API_BASE_URL = window.API_BASE_URL || 'http://localhost:8888/v1';
