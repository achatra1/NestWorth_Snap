/** Base URL of the backend API, e.g. "http://localhost:8000". Override via VITE_API_BASE_URL. */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/** Base URL for versioned API routes, e.g. "http://localhost:8000/api/v1". */
export const API_V1_URL = `${API_BASE_URL}/api/v1`;
