# Microboss Documentation

## Note on Frontend Removal

The standalone Next.js frontend implementation (microboss-frontend) has been removed from this project due to implementation issues. The current web interface is built directly into the microboss backend using Flask templates and can be accessed through the Flask web server.

## Accessing the Web Interface

The web interface can be accessed by running the microboss web server:

```
python -m microboss.web.app
```

This will start the Flask web server, and you can access the interface at `http://localhost:5000` by default. 