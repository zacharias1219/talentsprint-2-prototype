# API Documentation

## Overview

This document describes the API endpoints for the AI-Powered Financial Advisor system.

## Endpoints

### User Profile API

#### Create User Profile
- **Endpoint**: `POST /api/user/profile`
- **Description**: Create a new user profile
- **Request Body**: User profile data
- **Response**: Created profile object

#### Get User Profile
- **Endpoint**: `GET /api/user/profile/{user_id}`
- **Description**: Get user profile by ID
- **Response**: User profile object

### Recommendations API

#### Generate Recommendations
- **Endpoint**: `POST /api/recommendations/generate`
- **Description**: Generate personalized recommendations
- **Request Body**: User ID and optional context
- **Response**: List of recommendations

### Chat API

#### Send Message
- **Endpoint**: `POST /api/chat/message`
- **Description**: Send a chat message and get response
- **Request Body**: User ID and message text
- **Response**: Response text and metadata

## Authentication

Currently, the API uses user IDs for identification. In production, implement proper authentication (JWT tokens, API keys, etc.).

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Default limits:
- 60 requests per minute per user
- 1000 requests per day per user

## Error Handling

All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

Error responses include a JSON object with error details:
```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

