# API Specification

## Overview

This document specifies all APIs for the GPU Resource Pool system, including REST APIs for backend services, WebSocket APIs for real-time communication, and blockchain transaction specifications.

## Table of Contents

1. [Pool Gateway API](#pool-gateway-api)
2. [Worker Manager API](#worker-manager-api)
3. [Contribution Tracker API](#contribution-tracker-api)
4. [Blockchain Interface API](#blockchain-interface-api)
5. [ML Optimizer API](#ml-optimizer-api)
6. [WebSocket APIs](#websocket-apis)
7. [Authentication](#authentication)
8. [Error Handling](#error-handling)

## Pool Gateway API

Base URL: `https://pool-gateway.example.com/api/v1`

### Inference Endpoints

#### Submit Inference Request

Submit an AI inference request to the pool.

```
POST /inference/submit
```

**Headers:**
- `Authorization: Bearer <jwt_token>`
- `Content-Type: application/json`
- `X-Client-ID: <client_identifier>`

**Request Body:**
```json
{
  "model": "llama-3-70b",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 150,
  "stream": false,
  "metadata": {
    "request_id": "unique-request-id",
    "priority": "normal"
  }
}
```

**Response (200 OK):**
```json
{
  "request_id": "unique-request-id",
  "model": "llama-3-70b",
  "worker_id": "worker-abc123",
  "response": {
    "content": "The capital of France is Paris.",
    "finish_reason": "stop"
  },
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 8,
    "total_tokens": 20
  },
  "latency_ms": 342,
  "attestation": {
    "verified": true,
    "measurement": "abcd1234..."
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid or missing token
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: No workers available
- `504 Gateway Timeout`: Request timeout

#### Stream Inference Request

Submit a streaming inference request.

```
POST /inference/stream
```

**Request Body:** Same as submit endpoint with `"stream": true`

**Response:** Server-Sent Events (SSE) stream

```
event: token
data: {"token": "The", "token_id": 123}

event: token
data: {"token": " capital", "token_id": 456}

event: done
data: {"usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20}}
```

### Worker Management Endpoints

#### List Available Workers

Get list of active workers in the pool.

```
GET /workers
```

**Query Parameters:**
- `status` (optional): Filter by status (active, inactive, degraded)
- `model` (optional): Filter by supported model
- `page` (default: 1): Page number
- `limit` (default: 50): Results per page

**Response (200 OK):**
```json
{
  "workers": [
    {
      "worker_id": "worker-abc123",
      "participant_address": "EQD...",
      "status": "active",
      "gpu_model": "NVIDIA H100",
      "gpu_count": 4,
      "supported_models": ["llama-3-70b", "mixtral-8x7b"],
      "current_load": 0.65,
      "avg_latency_ms": 280,
      "uptime_percentage": 99.8,
      "last_heartbeat": "2025-11-30T20:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 23,
    "pages": 1
  }
}
```

#### Get Worker Details

Get detailed information about a specific worker.

```
GET /workers/:worker_id
```

**Response (200 OK):**
```json
{
  "worker_id": "worker-abc123",
  "participant_address": "EQD...",
  "status": "active",
  "hardware": {
    "gpu_model": "NVIDIA H100",
    "gpu_count": 4,
    "vram_gb": 320,
    "cpu_cores": 64,
    "ram_gb": 512
  },
  "capabilities": {
    "supported_models": ["llama-3-70b", "mixtral-8x7b"],
    "max_context_length": 8192,
    "batch_size": 32
  },
  "metrics": {
    "current_load": 0.65,
    "avg_latency_ms": 280,
    "requests_processed_24h": 1523,
    "tokens_processed_24h": 450000,
    "error_rate_24h": 0.002,
    "uptime_percentage": 99.8
  },
  "attestation": {
    "tee_type": "Intel TDX",
    "measurement": "abcd1234...",
    "last_verified": "2025-11-30T20:45:00Z"
  }
}
```

### Pool Statistics Endpoints

#### Get Pool Stats

Get aggregate statistics for the entire pool.

```
GET /pool/stats
```

**Response (200 OK):**
```json
{
  "pool_id": "pool-001",
  "status": "active",
  "participants": {
    "total": 23,
    "active": 21,
    "inactive": 2
  },
  "resources": {
    "total_gpus": 87,
    "active_gpus": 82,
    "total_vram_gb": 6960,
    "total_stake_ton": 2300
  },
  "performance": {
    "requests_24h": 45000,
    "tokens_24h": 12500000,
    "avg_latency_ms": 310,
    "p95_latency_ms": 520,
    "p99_latency_ms": 780,
    "uptime_percentage": 99.7
  },
  "economics": {
    "revenue_24h_ton": 45.2,
    "operator_fees_24h_ton": 2.26,
    "avg_participant_revenue_ton": 1.97
  },
  "current_epoch": {
    "epoch_id": 156,
    "start_time": "2025-11-25T00:00:00Z",
    "end_time": "2025-12-02T00:00:00Z",
    "accumulated_rewards_ton": 287.3
  }
}
```

## Worker Manager API

Base URL: `https://worker-manager.example.com/api/v1`

### Deployment Endpoints

#### Deploy New Worker

Deploy a new Cocoon worker instance for a participant.

```
POST /workers/deploy
```

**Headers:**
- `Authorization: Bearer <admin_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "participant_address": "EQD...",
  "gpu_indices": [0, 1, 2, 3],
  "worker_coefficient": 1000,
  "models": ["llama-3-70b", "mixtral-8x7b"],
  "config": {
    "max_batch_size": 32,
    "max_context_length": 8192,
    "worker_threads": 16
  }
}
```

**Response (202 Accepted):**
```json
{
  "deployment_id": "deploy-xyz789",
  "status": "pending",
  "estimated_completion_sec": 120,
  "worker_id": "worker-abc123"
}
```

#### Get Deployment Status

Check status of worker deployment.

```
GET /workers/deploy/:deployment_id
```

**Response (200 OK):**
```json
{
  "deployment_id": "deploy-xyz789",
  "worker_id": "worker-abc123",
  "status": "completed",
  "progress": 100,
  "stages": [
    {
      "stage": "download_worker_image",
      "status": "completed",
      "duration_sec": 45
    },
    {
      "stage": "verify_checksum",
      "status": "completed",
      "duration_sec": 2
    },
    {
      "stage": "configure_worker",
      "status": "completed",
      "duration_sec": 5
    },
    {
      "stage": "initialize_tee",
      "status": "completed",
      "duration_sec": 30
    },
    {
      "stage": "register_with_gateway",
      "status": "completed",
      "duration_sec": 3
    }
  ],
  "worker_url": "https://worker-abc123.pool.example.com",
  "created_at": "2025-11-30T20:30:00Z",
  "completed_at": "2025-11-30T20:31:25Z"
}
```

### Health Monitoring Endpoints

#### Get Worker Health

Get health status of a worker.

```
GET /workers/:worker_id/health
```

**Response (200 OK):**
```json
{
  "worker_id": "worker-abc123",
  "status": "healthy",
  "health_checks": {
    "http_probe": {
      "status": "passing",
      "latency_ms": 12,
      "last_check": "2025-11-30T20:45:00Z"
    },
    "gpu_availability": {
      "status": "passing",
      "gpus_online": 4,
      "gpus_total": 4
    },
    "attestation": {
      "status": "passing",
      "last_verified": "2025-11-30T20:44:00Z"
    },
    "memory_usage": {
      "status": "passing",
      "used_gb": 180,
      "total_gb": 320,
      "percentage": 56.25
    }
  },
  "metrics": {
    "cpu_usage_percent": 45,
    "memory_usage_percent": 56,
    "gpu_utilization_percent": 68,
    "disk_usage_percent": 23
  }
}
```

#### Restart Worker

Restart a worker instance.

```
POST /workers/:worker_id/restart
```

**Headers:**
- `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "graceful": true,
  "drain_timeout_sec": 60
}
```

**Response (202 Accepted):**
```json
{
  "worker_id": "worker-abc123",
  "restart_initiated": true,
  "expected_downtime_sec": 45
}
```

## Contribution Tracker API

Base URL: `https://contribution-tracker.example.com/api/v1`

### Contribution Endpoints

#### Record Task Completion

Record completion of an inference task.

```
POST /contributions/task
```

**Headers:**
- `Authorization: Bearer <worker_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "worker_id": "worker-abc123",
  "participant_address": "EQD...",
  "task_id": "task-xyz789",
  "model": "llama-3-70b",
  "tokens": {
    "prompt": 50,
    "completion": 120,
    "total": 170
  },
  "latency_ms": 340,
  "success": true,
  "timestamp": "2025-11-30T20:45:00Z"
}
```

**Response (201 Created):**
```json
{
  "contribution_id": "contrib-123",
  "recorded": true
}
```

#### Get Participant Contributions

Get contribution data for a participant.

```
GET /contributions/participant/:address
```

**Query Parameters:**
- `epoch_id` (optional): Filter by epoch
- `start_date` (optional): Start date (ISO 8601)
- `end_date` (optional): End date (ISO 8601)

**Response (200 OK):**
```json
{
  "participant_address": "EQD...",
  "contributions": {
    "current_epoch": {
      "epoch_id": 156,
      "tasks_completed": 1523,
      "tokens_processed": 450000,
      "uptime_seconds": 580000,
      "uptime_percentage": 99.8,
      "contribution_score": 45230,
      "estimated_rewards_ton": 1.97
    },
    "all_time": {
      "total_tasks": 123500,
      "total_tokens": 38000000,
      "total_uptime_seconds": 45000000,
      "total_rewards_ton": 156.8,
      "avg_quality_score": 875
    }
  }
}
```

#### Submit Heartbeat

Worker submits heartbeat signal.

```
POST /contributions/heartbeat
```

**Headers:**
- `Authorization: Bearer <worker_token>`

**Request Body:**
```json
{
  "worker_id": "worker-abc123",
  "participant_address": "EQD...",
  "status": "active",
  "metrics": {
    "current_load": 0.65,
    "queue_length": 3,
    "gpu_utilization": 68
  },
  "timestamp": "2025-11-30T20:45:00Z"
}
```

**Response (200 OK):**
```json
{
  "acknowledged": true,
  "next_heartbeat_sec": 30
}
```

## Blockchain Interface API

Base URL: `https://blockchain-api.example.com/api/v1`

### Transaction Endpoints

#### Submit Transaction

Submit a transaction to TON blockchain.

```
POST /transactions/submit
```

**Headers:**
- `Authorization: Bearer <admin_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "contract": "pool_operator",
  "operation": "pool_update_params",
  "params": {
    "pool_fee_bps": 500,
    "min_participant_stake": "100000000000"
  },
  "sender_wallet": "EQD...",
  "gas_limit": 100000
}
```

**Response (202 Accepted):**
```json
{
  "transaction_id": "tx-abc123",
  "status": "pending",
  "estimated_confirmation_sec": 10
}
```

#### Get Transaction Status

Check status of a blockchain transaction.

```
GET /transactions/:transaction_id
```

**Response (200 OK):**
```json
{
  "transaction_id": "tx-abc123",
  "hash": "0xabcd1234...",
  "status": "confirmed",
  "confirmations": 3,
  "contract": "pool_operator",
  "operation": "pool_update_params",
  "gas_used": 85000,
  "fee_ton": "0.0085",
  "submitted_at": "2025-11-30T20:40:00Z",
  "confirmed_at": "2025-11-30T20:40:15Z"
}
```

### Contract Query Endpoints

#### Get Pool Info

Query pool information from PoolOperator contract.

```
GET /contracts/pool_operator/info
```

**Response (200 OK):**
```json
{
  "pool_id": 1,
  "owner_address": "EQD...",
  "cocoon_root_address": "EQC...",
  "pool_state": 0,
  "pool_fee_bps": 500,
  "min_participant_stake": "100000000000",
  "active_participant_count": 23,
  "total_pooled_stake": "2300000000000",
  "participant_registry_address": "EQP...",
  "reward_distribution_address": "EQR..."
}
```

#### Get Participant Info

Query participant information from ParticipantRegistry contract.

```
GET /contracts/participant_registry/participant/:address
```

**Response (200 OK):**
```json
{
  "participant_address": "EQD...",
  "worker_contract_address": "EQW...",
  "stake_amount": "150000000000",
  "status": 0,
  "total_contribution_score": 450000,
  "total_tasks_completed": 123500,
  "total_tokens_processed": 38000000,
  "total_uptime_seconds": 45000000,
  "reputation_score": 875,
  "last_heartbeat_timestamp": 1732998300,
  "join_timestamp": 1700000000
}
```

#### Get Epoch Info

Query epoch information from RewardDistribution contract.

```
GET /contracts/reward_distribution/epoch/:epoch_id
```

**Response (200 OK):**
```json
{
  "epoch_id": 156,
  "start_timestamp": 1700000000,
  "end_timestamp": 1700604800,
  "total_rewards": "287300000000",
  "operator_fee": "14365000000",
  "participant_rewards": "272935000000",
  "distribution_status": 1,
  "participants_paid": 0,
  "total_participants": 23
}
```

### Event Subscription Endpoints

#### Subscribe to Events

Subscribe to blockchain events via WebSocket.

```
WS /events/subscribe
```

**Subscribe Message:**
```json
{
  "action": "subscribe",
  "events": [
    "participant_registered",
    "reward_distributed",
    "epoch_finalized"
  ],
  "filters": {
    "contract": "pool_operator"
  }
}
```

**Event Message:**
```json
{
  "event": "participant_registered",
  "contract": "pool_operator",
  "data": {
    "participant_address": "EQD...",
    "stake_amount": "150000000000"
  },
  "block_number": 12345678,
  "transaction_hash": "0xabcd...",
  "timestamp": "2025-11-30T20:45:00Z"
}
```

## ML Optimizer API

Base URL: `https://ml-optimizer.example.com/api/v1`

### Profitability Endpoints

#### Get Profitability Forecast

Get revenue forecast for models.

```
GET /profitability/forecast
```

**Query Parameters:**
- `horizon_days` (default: 7): Forecast horizon
- `models` (optional): Comma-separated list of models

**Response (200 OK):**
```json
{
  "forecast_date": "2025-11-30",
  "horizon_days": 7,
  "models": [
    {
      "model": "llama-3-70b",
      "forecasts": [
        {
          "date": "2025-12-01",
          "estimated_requests": 2500,
          "estimated_tokens": 750000,
          "estimated_revenue_ton": 3.2,
          "confidence_interval": [2.8, 3.6]
        }
      ],
      "total_estimated_revenue_ton": 22.4,
      "recommendation": "increase_capacity",
      "optimal_worker_coefficient": 1050
    },
    {
      "model": "mixtral-8x7b",
      "forecasts": [...],
      "total_estimated_revenue_ton": 18.6,
      "recommendation": "maintain",
      "optimal_worker_coefficient": 1000
    }
  ]
}
```

### Optimization Endpoints

#### Get Worker Assignment

Get optimal worker assignment for a task.

```
POST /optimization/assign
```

**Request Body:**
```json
{
  "model": "llama-3-70b",
  "estimated_tokens": 200,
  "priority": "normal",
  "client_location": "us-east"
}
```

**Response (200 OK):**
```json
{
  "assigned_worker": "worker-abc123",
  "reasoning": {
    "latency_score": 0.92,
    "load_balance_score": 0.85,
    "capability_score": 1.0,
    "cost_efficiency_score": 0.88,
    "total_score": 0.91
  },
  "alternatives": [
    {
      "worker_id": "worker-def456",
      "total_score": 0.87
    }
  ],
  "estimated_latency_ms": 280
}
```

#### Update Optimization Model

Trigger retraining of optimization models.

```
POST /optimization/retrain
```

**Headers:**
- `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "model_type": "task_distribution",
  "training_data_days": 30,
  "force": false
}
```

**Response (202 Accepted):**
```json
{
  "training_job_id": "train-xyz",
  "status": "started",
  "estimated_duration_minutes": 45
}
```

## WebSocket APIs

### Real-Time Metrics Stream

Connect to real-time metrics stream.

```
WS /ws/metrics
```

**Subscribe Message:**
```json
{
  "action": "subscribe",
  "metrics": [
    "pool_throughput",
    "worker_status",
    "queue_depth"
  ],
  "interval_sec": 5
}
```

**Metric Update Message:**
```json
{
  "metric": "pool_throughput",
  "value": 125.5,
  "unit": "requests_per_second",
  "timestamp": "2025-11-30T20:45:00Z"
}
```

### Worker Status Updates

Receive real-time worker status changes.

```
WS /ws/workers
```

**Status Update Message:**
```json
{
  "event": "status_changed",
  "worker_id": "worker-abc123",
  "old_status": "active",
  "new_status": "degraded",
  "reason": "high_error_rate",
  "timestamp": "2025-11-30T20:45:00Z"
}
```

## Authentication

### JWT Token Authentication

Most endpoints require JWT authentication.

**Obtaining a Token:**

```
POST /auth/token
```

**Request Body:**
```json
{
  "wallet_address": "EQD...",
  "signature": "0xabcd...",
  "message": "Login request at 2025-11-30T20:45:00Z"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Using the Token:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### API Key Authentication

For backend services and workers.

**Request Header:**
```
X-API-Key: your-api-key-here
```

### Rate Limiting

Rate limits are applied per API key/token:

| Endpoint Type | Rate Limit |
|---------------|------------|
| Inference requests | 100 req/min |
| Query endpoints | 1000 req/min |
| Admin operations | 10 req/min |
| Worker heartbeats | 120 req/hour |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1732998600
```

**Rate Limit Exceeded Response (429):**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again in 45 seconds.",
  "retry_after_sec": 45
}
```

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "request_id": "req-xyz789",
    "timestamp": "2025-11-30T20:45:00Z"
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `invalid_request` | Request validation failed |
| 400 | `invalid_model` | Requested model not supported |
| 401 | `unauthorized` | Missing or invalid authentication |
| 403 | `forbidden` | Insufficient permissions |
| 404 | `not_found` | Resource not found |
| 409 | `conflict` | Resource conflict (e.g., duplicate) |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_error` | Server error |
| 502 | `bad_gateway` | Upstream service error |
| 503 | `service_unavailable` | Service temporarily unavailable |
| 504 | `gateway_timeout` | Request timeout |

### Retry Logic

Clients should implement exponential backoff for retries:

```
retry_delay = min(base_delay * (2 ^ attempt), max_delay)
```

Recommended values:
- `base_delay`: 1 second
- `max_delay`: 60 seconds
- `max_attempts`: 5

Retry on status codes: 408, 429, 500, 502, 503, 504

## Versioning

API versioning is done via URL path:
- Current version: `/api/v1`
- Beta features: `/api/v1beta1`

Breaking changes will increment the major version (`v2`, `v3`, etc.).

## Pagination

List endpoints support cursor-based pagination:

**Request:**
```
GET /workers?limit=50&cursor=eyJpZCI6MTIzfQ==
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTczfQ==",
    "has_more": true,
    "total": 234
  }
}
```

## Webhooks

Pool operators can configure webhooks for important events.

### Webhook Configuration

```
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": [
    "participant_joined",
    "participant_left",
    "epoch_finalized",
    "distribution_completed"
  ],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload

```json
{
  "event": "epoch_finalized",
  "data": {
    "epoch_id": 156,
    "total_rewards_ton": "287.3"
  },
  "timestamp": "2025-11-30T20:45:00Z",
  "signature": "sha256=abcd1234..."
}
```

Signature verification:
```
HMAC-SHA256(payload, webhook_secret) == signature
```

## SDK Support

Official SDKs available for:
- **JavaScript/TypeScript**: `@gpu-pool/sdk-js`
- **Python**: `gpu-pool-sdk`
- **Go**: `github.com/gpu-pool/sdk-go`

Example usage (TypeScript):
```typescript
import { GPUPoolClient } from '@gpu-pool/sdk-js';

const client = new GPUPoolClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://pool-gateway.example.com'
});

const result = await client.inference.submit({
  model: 'llama-3-70b',
  messages: [{ role: 'user', content: 'Hello!' }]
});
```
