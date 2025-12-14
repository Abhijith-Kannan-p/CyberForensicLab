import React from 'react'

export default function SidePanel({ node, onClose }) {
  if (!node) return null

  const getSeverityColor = (score, isAnomaly) => {
    if (!isAnomaly) return 'text-cyber-neon'
    if (score < -0.3) return 'text-cyber-red'
    if (score < -0.2) return 'text-cyber-orange'
    return 'text-cyber-yellow'
  }

  const getSeverityLevel = (score, isAnomaly) => {
    if (!isAnomaly) return 'LOW'
    if (score < -0.3) return 'HIGH'
    if (score < -0.2) return 'MEDIUM'
    return 'LOW'
  }

  const severityLevel = getSeverityLevel(node.anomaly_score, node.is_anomaly)
  const severityColor = getSeverityColor(node.anomaly_score, node.is_anomaly)

  return (
    <div className="absolute top-0 right-0 h-full w-96 bg-cyber-dark/95 backdrop-blur-md border-l border-cyber-neon/30 z-20 overflow-y-auto">
      <div className="p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-cyber-neon">Node Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Node Info Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4 border-b border-cyber-neon/30 pb-2">
            Node Information
          </h3>
          <div className="space-y-3">
            <div>
              <label className="text-sm text-gray-400">Node ID</label>
              <p className="text-white font-mono">{node.id}</p>
            </div>
            <div>
              <label className="text-sm text-gray-400">IP Address</label>
              <p className="text-white font-mono">{node.ip}</p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Incoming Traffic</label>
              <p className="text-white">{node.incoming_traffic || 0} KB/s</p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Outgoing Traffic</label>
              <p className="text-white">{node.outgoing_traffic || 0} KB/s</p>
            </div>
          </div>
        </div>

        {/* Attack Info Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4 border-b border-cyber-neon/30 pb-2">
            Attack Information
          </h3>
          <div className="space-y-3">
            <div>
              <label className="text-sm text-gray-400">Attack Type</label>
              <p className="text-white font-semibold text-lg">{node.attack_type || 'Normal'}</p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Confidence</label>
              <div className="mt-1">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-white">{Math.round((node.confidence || 0) * 100)}%</span>
                </div>
                <div className="w-full bg-cyber-darker rounded-full h-2">
                  <div
                    className="bg-cyber-neon h-2 rounded-full transition-all"
                    style={{ width: `${(node.confidence || 0) * 100}%` }}
                  />
                </div>
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-400">Anomaly Score</label>
              <p className={`font-mono text-lg ${severityColor}`}>
                {node.anomaly_score?.toFixed(4) || '0.0000'}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Is Anomaly</label>
              <p className={node.is_anomaly ? 'text-cyber-red font-semibold' : 'text-cyber-neon'}>
                {node.is_anomaly ? 'TRUE' : 'FALSE'}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Severity Level</label>
              <p className={`font-bold text-lg ${severityColor}`}>
                {severityLevel}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-400">Timestamp</label>
              <p className="text-white text-sm font-mono">
                {node.timestamp ? new Date(node.timestamp).toLocaleString() : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Visual Indicators */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-4 border-b border-cyber-neon/30 pb-2">
            Visual Indicators
          </h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div
                className="w-6 h-6 rounded-full"
                style={{
                  backgroundColor: node.attack_type === 'Normal' ? '#00aaff' :
                    node.attack_type === 'Exploits' ? '#9966ff' :
                    node.attack_type === 'Reconnaissance' ? '#00ff88' :
                    node.attack_type === 'Worms' ? '#ff3366' :
                    node.attack_type === 'DoS' ? '#ff8844' : '#ffcc00',
                  boxShadow: node.is_anomaly ? `0 0 20px ${node.attack_type === 'Normal' ? '#00aaff' :
                    node.attack_type === 'Exploits' ? '#9966ff' :
                    node.attack_type === 'Reconnaissance' ? '#00ff88' :
                    node.attack_type === 'Worms' ? '#ff3366' :
                    node.attack_type === 'DoS' ? '#ff8844' : '#ffcc00'}` : 'none'
                }}
              />
              <span className="text-sm text-gray-300">Node Color = Attack Type</span>
            </div>
            {node.is_anomaly && (
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 rounded-full bg-cyber-neon animate-pulse" />
                <span className="text-sm text-gray-300">Pulsing Glow = Active Threat</span>
              </div>
            )}
            <div className="flex items-center space-x-3">
              <div
                className="w-6 h-6 rounded-full"
                style={{
                  opacity: Math.abs(node.anomaly_score || 0) * 2
                }}
              />
              <span className="text-sm text-gray-300">Glow Intensity = Anomaly Severity</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 pt-6 border-t border-cyber-neon/30">
          <button
            onClick={onClose}
            className="w-full bg-cyber-neon/20 hover:bg-cyber-neon/30 text-cyber-neon py-2 px-4 rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

