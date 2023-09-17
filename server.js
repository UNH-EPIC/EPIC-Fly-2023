const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const readline = require('readline');

const app = express();
const port = 4000;

// Set up a simple route
app.get('/', (req, res) => {
    res.send('Hello, World!');
});

// Create an HTTP server using the Express app
const server = http.createServer(app);

// Create a WebSocket server
const wss = new WebSocket.Server({ server });

// Store connected clients and assign them unique IDs
const clients = new Map();
let clientIdCounter = 0;

// WebSocket connection event
wss.on('connection', (ws) => {
    // Generate a unique ID for the client
    const clientId = clientIdCounter++;
    clients.set(ws, clientId);

    // Send a welcome message to the client when they connect
    ws.send(`Connected to the WebSocket server. Your client ID is: ${clientId}`);

    // Handle incoming messages from clients
    ws.on('message', (message) => {
        console.log(`Received message from client ${clientId}:`, message.toString());

        // Broadcast the message to all connected clients
        wss.clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(`[Client ${clientId}] ${message}`);
            }
        });
    });

    // Handle client disconnection
    ws.on('close', () => {
        clients.delete(ws);
    });
});

// Start the server
server.listen(port, () => {
    console.log(`Server is listening on port ${port}`);
});

// Set up readline to read input from terminal
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

// Read and send messages from the server to clients in real-time
rl.on('line', (input) => {
    console.log('Sending message to clients:', input); // Add this log to verify that the message is being sent
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(`[Server] ${input}`);
        }
    });
});
