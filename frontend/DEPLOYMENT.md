# Deployment Guide for Todo App Frontend

## Environment Variables

For successful deployment, you need to set the following environment variables:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-frontend-domain.com
```

### Variable Descriptions:

- `NEXT_PUBLIC_API_BASE_URL`: The base URL of your backend API server. This is used for all API calls from the frontend.
- `NEXT_PUBLIC_BETTER_AUTH_URL`: The URL of your frontend application, used for authentication redirects.

## Build Process

The application uses Next.js 14.0.4 and can be built with:

```bash
npm run build
```

After building, the application will be available in the `out/` directory for static hosting.

## Deployment Steps

1. Set the required environment variables
2. Install dependencies: `npm install`
3. Build the application: `npm run build`
4. Serve the contents of the `out/` directory using a static server or CDN

## Important Notes

- The application connects to a WebSocket for real-time updates, so ensure your deployment supports WebSocket connections
- The API base URL is used for both REST API calls and WebSocket connections
- Authentication tokens are stored in localStorage and used for protected API calls
- The application has a floating AI chat assistant that communicates with the backend API

## Troubleshooting

- If API calls fail, verify that `NEXT_PUBLIC_API_BASE_URL` is correctly set and accessible
- If WebSocket connections fail, ensure your deployment environment supports WebSocket connections
- For authentication issues, check that both environment variables are properly configured