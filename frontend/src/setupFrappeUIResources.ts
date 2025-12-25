// Placed in separate file to setup frappe resource fetcher before loading the app.
import { frappeRequest, setConfig } from "frappe-ui";

// Configure resource fetcher to use frappeRequest
// frappeRequest uses relative URLs by default
// In development, Vite proxy will redirect /api/* requests to port 8000
// In production, requests go to the same origin as the frontend
setConfig("resourceFetcher", frappeRequest);