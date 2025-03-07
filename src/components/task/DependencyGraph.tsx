"use client";

import { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
import { GraphData, GraphNode, GraphEdge, TaskStatus } from '@/lib/types';

interface DependencyGraphProps {
  graphData: GraphData | null | undefined;
  height?: string;
  onNodeClick?: (nodeId: string) => void;
}

const DependencyGraph = ({ graphData, height = '500px', onNodeClick }: DependencyGraphProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isReady, setIsReady] = useState(false);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    // Only proceed if we have both the container and graph data
    if (!containerRef.current || !graphData || !graphData.nodes || !graphData.nodes.length) {
      return;
    }

    try {
      // Configure node colors based on status
      const getNodeColor = (status?: TaskStatus) => {
        switch (status) {
          case 'completed': return '#28a745'; // Green
          case 'running': return '#007bff';   // Blue
          case 'failed': return '#dc3545';    // Red
          case 'pending':
          default: return '#6c757d';          // Gray
        }
      };

      // Format nodes with proper colors and styles
      const formattedNodes = graphData.nodes.map((node: GraphNode) => ({
        id: node.id,
        label: node.label || node.id,
        title: node.description || node.id,
        color: {
          background: getNodeColor(node.status),
          border: '#333333',
          highlight: { 
            background: getNodeColor(node.status), 
            border: '#000000' 
          }
        },
        font: { color: '#ffffff', size: 12 },
        shape: 'box',
        margin: 10,
        shadow: true
      }));

      // Format edges
      const formattedEdges = graphData.edges.map((edge: GraphEdge) => ({
        id: edge.id,
        from: edge.from,
        to: edge.to,
        arrows: edge.arrows || 'to',
        smooth: { type: 'cubicBezier', roundness: 0.5 }
      }));

      // Create data sets
      const nodes = new DataSet(formattedNodes);
      const edges = new DataSet(formattedEdges);

      // Default options for the network
      const options = {
        layout: {
          hierarchical: {
            direction: 'UD', // Up to Down
            sortMethod: 'directed',
            levelSeparation: 100,
            nodeSpacing: 150,
            edgeMinimization: true
          }
        },
        physics: {
          enabled: false
        },
        edges: {
          arrows: 'to',
          smooth: {
            type: 'cubicBezier',
            roundness: 0.5
          },
          color: '#666666',
          width: 1
        },
        interaction: {
          dragNodes: true,
          navigationButtons: true,
          keyboard: true,
          hover: true
        }
      };

      // Create the network
      networkRef.current = new Network(
        containerRef.current,
        { nodes, edges },
        options
      );

      // Add click event handler if provided
      if (onNodeClick) {
        networkRef.current.on('click', function(params) {
          if (params.nodes.length > 0) {
            onNodeClick(params.nodes[0]);
          }
        });
      }

      // Fit to container after stabilization
      networkRef.current.on('stabilizationIterationsDone', () => {
        if (networkRef.current) {
          networkRef.current.fit();
          setIsReady(true);
        }
      });

      // Clean up on unmount
      return () => {
        if (networkRef.current) {
          networkRef.current.destroy();
          networkRef.current = null;
        }
      };
    } catch (error) {
      console.error('Error initializing dependency graph:', error);
    }
  }, [graphData, onNodeClick]);

  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="text-center py-10 text-gray-500 border border-dashed border-gray-300 rounded-md">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
        <p className="mt-2">No dependency graph available yet.</p>
        <p className="mt-1 text-sm">The graph will appear here once task decomposition is complete.</p>
      </div>
    );
  }

  return (
    <div className="relative rounded-md shadow-sm">
      <div
        ref={containerRef}
        className="bg-white rounded-md border border-gray-200"
        style={{ height, width: '100%' }}
      ></div>
      
      {!isReady && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80 rounded-md">
          <div className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-3 text-gray-600">Generating graph...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DependencyGraph; 