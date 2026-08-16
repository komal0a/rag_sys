# Frontend

React + Vite frontend for RAG Platform.

## Development

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:3000` with hot reload.

## Production Build

```bash
npm run build
npm run preview
```

Build output in `dist/` directory.

## Configuration

Backend API URL is configured via environment variable:

**Development:** Uses relative paths by default (localhost)

**Production:** Set `VITE_API_URL` environment variable:

```bash
VITE_API_URL=https://api.example.com npm run build
```

Or via `.env` file:

```
VITE_API_URL=https://api.example.com
```

Vite loads environment variables from `.env*` files during build.

## Docker

Development:

```bash
docker build -f Dockerfile -t rag-frontend:dev --target builder .
docker run -p 3000:3000 rag-frontend:dev npm run dev
```

Production:

```bash
docker build -f Dockerfile -t rag-frontend:prod .
docker run -p 3000:3000 rag-frontend:prod
```

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
