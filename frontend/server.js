const http = require('http');

console.log("Frontend starting...");

const server = http.createServer((req, res) => {
    res.writeHead(200);
    res.end('OK');
});

// Since docker-compose.dev.yml overrides the command and passes `--host 0.0.0.0 --port 3000`,
// we will just start the server on 3000 to satisfy the healthcheck.
const port = 3000;
server.listen(port, '0.0.0.0', () => {
    console.log(`Frontend stub server is running on port ${port}`);
});
