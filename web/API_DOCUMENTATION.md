# API Documentation - Raspberry Pi Control Server

## Overview

The FastAPI server provides endpoints for controlling the Raspberry Pi, executing scripts, and receiving real-time updates via WebSocket.

## Endpoints

### POST /start
Executes the `scripts/start.py` script.

**Response:**
```json
{
  "status": "success",
  "message": "start executed"
}
```

### POST /end
Executes the `scripts/end.py` script.

**Response:**
```json
{
  "status": "success",
  "message": "end executed"
}
```

### POST /start_receiver
Starts the receiver script in a background thread.

**Response:**
```json
{
  "status": "started"  // or "already_running"
}
```

### POST /stop_receiver
Stops the currently running receiver thread.

**Response:**
```json
{
  "status": "stopping"  // or "not_running"
}
```

## WebSocket Connection

### /ws
Establishes a WebSocket connection for real-time updates.

**Messages:**
```json
{
  "type": "servo_update",
  "data": {
    "12": 0.0,
    "13": 0.0,
    "19": 0.0,
    "18": 0.0
  }
}
```

The WebSocket sends updates whenever servo positions change.

## Usage Examples

### From Web Interface

```javascript
// Execute a script
const response = await fetch('http://raspberrypi:8000/start', {
  method: 'POST'
});

// Start receiver
const response = await fetch('http://raspberrypi:8000/start_receiver', {
  method: 'POST'
});

// WebSocket connection
const socket = new WebSocket('ws://raspberrypi:8000/ws');
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'servo_update') {
    console.log('Servo positions:', data.data);
  }
};
```

### From Command Line

```bash
# Execute start script
curl -X POST http://localhost:8000/start

# Start receiver
curl -X POST http://localhost:8000/start_receiver

# Stop receiver
curl -X POST http://localhost:8000/stop_receiver
```

## Error Handling

The API returns appropriate HTTP status codes:
- **200 OK**: Successful execution
- **500 Internal Server Error**: Script execution failed with error details

## Implementation Details

### Key Features

1. **Script Execution**: Runs predefined scripts with proper error handling
2. **Receiver Control**: Start/stop background receiver thread
3. **WebSocket Updates**: Real-time servo position updates
4. **CORS Support**: Configured for development environment

### Servo State Management

The server maintains servo positions in memory and notifies all connected WebSocket clients when positions change through a dirty flag mechanism.

## Security Considerations

- Scripts are executed with server process permissions
- Only predefined scripts can be executed
- CORS is restricted to specific development origins
