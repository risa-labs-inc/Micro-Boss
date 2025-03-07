/**
 * Microboss Web Interface - Main JavaScript
 */

// Initialize Socket.IO connection when page loads
let socket;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Socket.IO connection
    initSocketIO();

    // Initialize tooltips
    initTooltips();

    // Initialize code copy buttons
    initCodeCopyButtons();
});

/**
 * Initialize Socket.IO connection
 */
function initSocketIO() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to Socket.IO server');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from Socket.IO server');
    });
    
    socket.on('error', (error) => {
        console.error('Socket.IO error:', error);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize code copy buttons
 */
function initCodeCopyButtons() {
    // Add copy buttons to all pre elements
    document.querySelectorAll('pre').forEach(pre => {
        // Create button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-code';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy to clipboard';
        copyButton.type = 'button';
        copyButton.ariaLabel = 'Copy code to clipboard';
        
        // Add click event
        copyButton.addEventListener('click', () => {
            const code = pre.querySelector('code')?.textContent || pre.textContent;
            navigator.clipboard.writeText(code).then(() => {
                // Change button text temporarily
                copyButton.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                }, 1500);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                copyButton.innerHTML = '<i class="fas fa-times"></i>';
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                }, 1500);
            });
        });
        
        // Add to pre element
        pre.appendChild(copyButton);
    });
}

/**
 * Format a timestamp as a human-readable date and time
 * @param {number} timestamp - Unix timestamp in seconds
 * @returns {string} Formatted date and time
 */
function formatDateTime(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

/**
 * Format a duration in seconds as a human-readable string
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }
}

/**
 * Create a dependency graph visualization
 * @param {string} elementId - ID of the container element
 * @param {Array} nodes - Array of node objects
 * @param {Array} edges - Array of edge objects
 */
function createDependencyGraph(elementId, nodes, edges) {
    const container = document.getElementById(elementId);
    if (!container) return;
    
    // Create nodes array for visualization
    const nodeData = nodes.map(node => ({
        id: node.id,
        label: node.label || node.id,
        title: node.description || node.id,
        color: getStatusColor(node.status)
    }));
    
    // Create edges array for visualization
    const edgeData = edges.map(edge => ({
        from: edge.from,
        to: edge.to,
        arrows: 'to'
    }));
    
    // Create network
    const data = {
        nodes: new vis.DataSet(nodeData),
        edges: new vis.DataSet(edgeData)
    };
    
    const options = {
        layout: {
            hierarchical: {
                direction: 'UD', // Up to down
                sortMethod: 'directed',
                levelSeparation: 100,
                nodeSpacing: 150
            }
        },
        physics: {
            enabled: false
        },
        nodes: {
            shape: 'box',
            margin: 10,
            font: {
                size: 14
            }
        },
        edges: {
            smooth: {
                type: 'cubicBezier',
                forceDirection: 'vertical'
            }
        }
    };
    
    new vis.Network(container, data, options);
}

/**
 * Get color for a task status
 * @param {string} status - Task status
 * @returns {object} Color configuration for the node
 */
function getStatusColor(status) {
    switch (status) {
        case 'pending':
            return { background: '#ecf0f1', border: '#bdc3c7' };
        case 'running':
            return { background: '#3498db', border: '#2980b9' };
        case 'completed':
            return { background: '#2ecc71', border: '#27ae60' };
        case 'failed':
            return { background: '#e74c3c', border: '#c0392b' };
        default:
            return { background: '#95a5a6', border: '#7f8c8d' };
    }
} 