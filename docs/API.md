# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The system uses TON Wallet authentication for frontend access. API keys can be used for programmatic access.

## Endpoints

### Workers

#### List Workers

```http
GET /api/v1/workers
```

Query Parameters:
- `participant_id` (optional): Filter by participant
- `is_active` (optional): Filter by active status

Response:
```json
[
  {
    "id": 1,
    "participant_id": 1,
    "worker_name": "Worker-0",
    "instance_number": 0,
    "host": "localhost",
    "stats_port": 12000,
    "is_active": true,
    "latest_status": "healthy",
    "latest_gpu_utilization": 87.5,
    "latest_revenue_ton": 65.3
  }
]
```

#### Get Worker

```http
GET /api/v1/workers/{worker_id}
```

#### Create Worker

```http
POST /api/v1/workers
```

Request Body:
```json
{
  "participant_id": 1,
  "worker_name": "Worker-0",
  "instance_number": 0,
  "host": "localhost",
  "stats_port": 12000,
  "price_coefficient": 1.0
}
```

#### Update Worker

```http
PATCH /api/v1/workers/{worker_id}
```

Request Body:
```json
{
  "is_active": false,
  "price_coefficient": 1.2
}
```

#### Get Worker Metrics

```http
GET /api/v1/workers/{worker_id}/metrics?hours=24
```

#### Get Worker Stats

```http
GET /api/v1/workers/{worker_id}/stats
```

### Participants

#### List Participants

```http
GET /api/v1/participants
```

#### Get Participant

```http
GET /api/v1/participants/{participant_id}
```

Response:
```json
{
  "id": 1,
  "ton_wallet_address": "UQAbc...xyz",
  "username": "user123",
  "is_active": true,
  "total_workers": 2,
  "active_workers": 2,
  "total_revenue_ton": 125.50,
  "total_payouts": 5
}
```

#### Create Participant

```http
POST /api/v1/participants
```

Request Body:
```json
{
  "ton_wallet_address": "UQAbc...xyz",
  "telegram_user_id": 123456789,
  "username": "user123",
  "email": "user@example.com"
}
```

#### Get Participant by Wallet

```http
GET /api/v1/participants/wallet/{wallet_address}
```

### Payouts

#### List Payouts

```http
GET /api/v1/payouts?participant_id=1&limit=100
```

#### Get Payout

```http
GET /api/v1/payouts/{payout_id}
```

#### Create Payout

```http
POST /api/v1/payouts
```

Request Body:
```json
{
  "participant_id": 1,
  "transaction_hash": "abc123...",
  "amount_ton": 25.5,
  "amount_usd": 89.25,
  "from_address": "UQPool...",
  "to_address": "UQParticipant...",
  "transaction_time": "2025-01-15T10:30:00Z",
  "period_start": "2025-01-08T00:00:00Z",
  "period_end": "2025-01-15T00:00:00Z"
}
```

#### Get Payout Summary

```http
GET /api/v1/payouts/participant/{participant_id}/summary
```

#### Export Tax Report

```http
GET /api/v1/payouts/export/tax-report?participant_id=1&year=2025
```

Returns CSV file for tax reporting.

## Prometheus Metrics

```http
GET /metrics
```

Available metrics:
- `cocoon_worker_status` - Worker health status
- `cocoon_gpu_utilization` - GPU utilization percentage
- `cocoon_gpu_memory_used_gb` - GPU memory usage
- `cocoon_gpu_temperature_celsius` - GPU temperature
- `cocoon_revenue_ton` - Revenue in TON
- `cocoon_inference_requests_total` - Total inference requests
- `cocoon_worker_errors_total` - Worker errors

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message description"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 100 requests per minute per IP for read endpoints
- 20 requests per minute per IP for write endpoints

## WebSocket (Future)

Real-time updates will be available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics');
ws.onmessage = (event) => {
  const metrics = JSON.parse(event.data);
  console.log(metrics);
};
```
