import React, { useState, useEffect } from 'react'
import Network3D from './components/Network3D'
import SidePanel from './components/SidePanel'
import Dashboard from './components/Dashboard'
import { io } from 'socket.io-client'

const socket = io('http://localhost:5000')

function App() {
  const [selectedNode, setSelectedNode] = useState(null)
  const [networkData, setNetworkData] = useState({ nodes: [], edges: [], threats: [] })
  const [stats, setStats] = useState({ attack_type_distribution: {}, anomaly_scores: [] })

  useEffect(() => {
    // Fetch initial data with error handling
    const fetchData = async () => {
      try {
        const [nodesRes, edgesRes, threatsRes, statsRes] = await Promise.all([
          fetch('http://localhost:5000/api/nodes').catch(() => null),
          fetch('http://localhost:5000/api/edges').catch(() => null),
          fetch('http://localhost:5000/api/threats').catch(() => null),
          fetch('http://localhost:5000/api/stats').catch(() => null)
        ])

        if (nodesRes && nodesRes.ok) {
          const data = await nodesRes.json()
          setNetworkData(prev => ({ ...prev, nodes: data }))
        }

        if (edgesRes && edgesRes.ok) {
          const data = await edgesRes.json()
          setNetworkData(prev => ({ ...prev, edges: data }))
        }

        if (threatsRes && threatsRes.ok) {
          const data = await threatsRes.json()
          setNetworkData(prev => ({ ...prev, threats: data }))
        }

        if (statsRes && statsRes.ok) {
          const data = await statsRes.json()
          setStats(data)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      }
    }

    fetchData()

    // Listen for real-time updates
    socket.on('threat_update', (data) => {
      if (data.node) {
        setNetworkData(prev => {
          const nodes = [...prev.nodes]
          const nodeIndex = nodes.findIndex(n => n.id === data.node.id || n.ip === data.node.ip)
          if (nodeIndex >= 0) {
            nodes[nodeIndex] = data.node
          } else {
            nodes.push(data.node)
          }
          return { ...prev, nodes }
        })
      }
      if (data.edge) {
        setNetworkData(prev => ({
          ...prev,
          edges: [...prev.edges, data.edge].slice(-500) // Keep last 500 edges
        }))
      }
      if (data.is_threat) {
        fetch('http://localhost:5000/api/threats')
          .then(res => res.json())
          .then(threats => setNetworkData(prev => ({ ...prev, threats })))
      }
    })

    // Periodic stats update
    const statsInterval = setInterval(() => {
      fetch('http://localhost:5000/api/stats')
        .then(res => res.json())
        .then(data => setStats(data))
    }, 5000)

    return () => {
      socket.off('threat_update')
      clearInterval(statsInterval)
    }
  }, [])

  const handleNodeClick = (node) => {
    setSelectedNode(node)
  }

  const handleClosePanel = () => {
    setSelectedNode(null)
  }

  return (
    <div className="relative w-screen h-screen bg-cyber-darker">
      <Network3D 
        nodes={networkData.nodes} 
        edges={networkData.edges}
        onNodeClick={handleNodeClick}
        selectedNode={selectedNode}
      />
      
      <Dashboard stats={stats} threats={networkData.threats} />
      
      {selectedNode && (
        <SidePanel 
          node={selectedNode} 
          onClose={handleClosePanel}
        />
      )}
    </div>
  )
}

export default App
