# API Documentation - Script Execution Endpoints

## Overview

The FastAPI server now provides two new endpoints for executing Python scripts:

- `POST /start` - Executes the `scripts/start.py` script
- `POST /end` - Executes the `scripts/end.py` script

## Usage

### From Web Interface

The web interface can call these endpoints using the existing `sendCommand` function:

```javascript
// Call the start script
const sendCommand = useCallback(async (route: string) => {
    try {
      await fetch(`http://raspberrypi:8000${route}`, {
        method: "POST",
      });
    } catch (err) {
      console.error(`Erreur lors de l'appel à ${route}:`, err);
    }
  }, []);

// Usage:
sendCommand("/start");  // Execute start.py
sendCommand("/end");    // Execute end.py
```

### From Command Line

You can test the endpoints using curl:

```bash
# Execute start script
curl -X POST http://localhost:8000/start

# Execute end script  
curl -X POST http://localhost:8000/end
```

## WebSocket Notifications

When a script is executed, all connected WebSocket clients receive a notification:

```json
{
  "type": "script_status",
  "data": {
    "script": "start",  // or "end"
    "status": "success",
    "output": "Clean exit"  // script output
  }
}
```

## Error Handling

The API handles various error scenarios:

- **Script Execution Failure**: Returns HTTP 500 with error details
- **Timeout**: Returns HTTP 504 if script execution exceeds 10 seconds
- **Other Errors**: Returns HTTP 500 with error message

## Implementation Details

### Key Features

1. **Asynchronous Execution**: Scripts run without blocking the main server
2. **WebSocket Integration**: Clients are notified of script execution status
3. **Error Handling**: Comprehensive error handling and status codes
4. **Timeout Protection**: Prevents hanging scripts from blocking the server

### Security Considerations

- Scripts are executed with the same permissions as the server process
- Only predefined scripts can be executed (no arbitrary command injection)
- Error messages are sanitized before being returned to clients

## Future Improvements

Possible enhancements:

1. **Authentication**: Add API key or token-based authentication
2. **Script Parameters**: Allow passing parameters to scripts
3. **Queue System**: Implement a job queue for script execution
4. **Logging**: Add detailed logging of script executions
5. **Status Monitoring**: Add endpoint to check script execution status

## Example WebSocket Client

```javascript
const socket = new WebSocket('ws://raspberrypi:8000/ws');

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'script_status') {
    console.log(`Script ${data.data.script} executed:`, data.data.status);
    if (data.data.status === 'success') {
      console.log('Output:', data.data.output);
    }
  }
};
```
