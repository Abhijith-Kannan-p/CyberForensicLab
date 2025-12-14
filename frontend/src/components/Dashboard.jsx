import React, { useState, useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

const COLORS = {
  'Normal': '#00aaff',
  'Exploits': '#9966ff',
  'Reconnaissance': '#00ff88',
  'Worms': '#ff3366',
  'DoS': '#ff8844',
  'Fuzzers': '#ffcc00'
}

export default function Dashboard({ stats, threats }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [sortField, setSortField] = useState('timestamp')
  const [sortOrder, setSortOrder] = useState('desc')

  // Prepare pie chart data
  const pieData = useMemo(() => {
    if (!stats.attack_type_distribution) return []
    return Object.entries(stats.attack_type_distribution).map(([name, value]) => ({
      name,
      value
    }))
  }, [stats])

  // Prepare anomaly graph data
  const anomalyData = useMemo(() => {
    if (!stats.anomaly_scores || stats.anomaly_scores.length === 0) return []
    return stats.anomaly_scores.map((score, index) => ({
      time: index,
      score: score
    }))
  }, [stats])

  // Filter and sort threats
  const filteredThreats = useMemo(() => {
    let filtered = threats

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(t => 
        t.ip?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.attack_type?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      const aVal = a[sortField]
      const bVal = b[sortField]
      
      if (sortField === 'timestamp') {
        return sortOrder === 'asc' 
          ? new Date(aVal) - new Date(bVal)
          : new Date(bVal) - new Date(aVal)
      }
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal
      }
      
      return sortOrder === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal))
    })

    return filtered
  }, [threats, searchQuery, sortField, sortOrder])

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('asc')
    }
  }

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null
    return sortOrder === 'asc' ? '↑' : '↓'
  }

  return (
    <div className="absolute bottom-0 right-0 w-96 h-[60vh] bg-cyber-dark/95 backdrop-blur-md border-t border-l border-cyber-neon/30 z-10 overflow-hidden flex flex-col">
      <div className="p-4 border-b border-cyber-neon/30">
        <h2 className="text-xl font-bold text-cyber-neon mb-4">Dashboard</h2>
        
        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search by IP, ID, or Attack Type..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-cyber-darker border border-cyber-neon/30 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyber-neon"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Attack Type Distribution */}
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Attack Type Distribution</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="40%"
                  labelLine={true}
                  label={({ name, percent, cx, cy, midAngle, innerRadius, outerRadius }) => {
                    const RADIAN = Math.PI / 180;
                    const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
                    const x = cx + radius * Math.cos(-midAngle * RADIAN);
                    const y = cy + radius * Math.sin(-midAngle * RADIAN);
                    const pct = (percent * 100).toFixed(0);
                    
                    // Truncate long names but show more characters
                    const displayName = name.length > 15 ? `${name.substring(0, 13)}...` : name;
                    
                    return (
                      <text 
                        x={x} 
                        y={y} 
                        fill="white" 
                        textAnchor={x > cx ? 'start' : 'end'} 
                        dominantBaseline="central"
                        fontSize="11"
                        fontWeight="500"
                      >
                        {displayName}
                        <tspan x={x} y={y + 13} fontSize="10" fill="#00ffff">
                          {pct}%
                        </tspan>
                      </text>
                    );
                  }}
                  outerRadius={55}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#00aaff'} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0a0e27', 
                    border: '1px solid #00ffff',
                    borderRadius: '4px',
                    padding: '8px',
                    color: '#ffffff'
                  }}
                  labelStyle={{ 
                    color: '#00ffff',
                    marginBottom: '4px',
                    fontWeight: 'bold',
                    fontSize: '13px'
                  }}
                  itemStyle={{ 
                    color: '#ffffff',
                    fontSize: '12px'
                  }}
                  formatter={(value, name, props) => {
                    const total = pieData.reduce((sum, item) => sum + item.value, 0);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return [
                      <span key="tooltip">
                        <span style={{ color: '#00ffff', fontWeight: 'bold' }}>{props.payload.name}:</span>{' '}
                        <span style={{ color: '#ffffff' }}>{value}</span>{' '}
                        <span style={{ color: '#00ffff' }}>({percentage}%)</span>
                      </span>,
                      ''
                    ];
                  }}
                />
                <Legend 
                  verticalAlign="bottom"
                  height={60}
                  wrapperStyle={{ 
                    fontSize: '11px', 
                    paddingTop: '15px',
                    color: '#ffffff'
                  }}
                  formatter={(value) => {
                    // Show full names in legend, truncate only if very long
                    return value.length > 20 ? `${value.substring(0, 18)}...` : value;
                  }}
                  iconType="circle"
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-500">
              No data available
            </div>
          )}
        </div>

        {/* Live Anomaly Graph */}
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Live Anomaly Scores</h3>
          {anomalyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={anomalyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#00ffff20" />
                <XAxis dataKey="time" stroke="#00ffff80" />
                <YAxis stroke="#00ffff80" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0a0e27', border: '1px solid #00ffff' }}
                  labelStyle={{ color: '#00ffff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#00ffff" 
                  strokeWidth={2}
                  dot={{ fill: '#00ffff', r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-36 flex items-center justify-center text-gray-500">
              No anomaly data available
            </div>
          )}
        </div>

        {/* Threat Log Table */}
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Threat Log</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-cyber-neon/30">
                  <th 
                    className="text-left py-2 px-2 text-cyber-neon cursor-pointer hover:text-white"
                    onClick={() => handleSort('timestamp')}
                  >
                    Time <SortIcon field="timestamp" />
                  </th>
                  <th 
                    className="text-left py-2 px-2 text-cyber-neon cursor-pointer hover:text-white"
                    onClick={() => handleSort('ip')}
                  >
                    IP <SortIcon field="ip" />
                  </th>
                  <th 
                    className="text-left py-2 px-2 text-cyber-neon cursor-pointer hover:text-white"
                    onClick={() => handleSort('attack_type')}
                  >
                    Type <SortIcon field="attack_type" />
                  </th>
                  <th 
                    className="text-left py-2 px-2 text-cyber-neon cursor-pointer hover:text-white"
                    onClick={() => handleSort('anomaly_score')}
                  >
                    Score <SortIcon field="anomaly_score" />
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredThreats.slice(0, 10).map((threat, index) => (
                  <tr 
                    key={index} 
                    className="border-b border-cyber-neon/10 hover:bg-cyber-neon/10"
                  >
                    <td className="py-2 px-2 text-gray-300 text-xs">
                      {threat.timestamp ? new Date(threat.timestamp).toLocaleTimeString() : 'N/A'}
                    </td>
                    <td className="py-2 px-2 text-white font-mono text-xs">
                      {threat.ip || threat.id}
                    </td>
                    <td className="py-2 px-2">
                      <span 
                        className="text-xs px-2 py-1 rounded"
                        style={{ 
                          backgroundColor: `${COLORS[threat.attack_type] || '#00aaff'}30`,
                          color: COLORS[threat.attack_type] || '#00aaff'
                        }}
                      >
                        {threat.attack_type || 'Normal'}
                      </span>
                    </td>
                    <td className="py-2 px-2">
                      <span 
                        className={`text-xs ${
                          threat.anomaly_score < -0.3 ? 'text-cyber-red' :
                          threat.anomaly_score < -0.2 ? 'text-cyber-orange' :
                          'text-cyber-yellow'
                        }`}
                      >
                        {threat.anomaly_score?.toFixed(3) || '0.000'}
                      </span>
                    </td>
                  </tr>
                ))}
                {filteredThreats.length === 0 && (
                  <tr>
                    <td colSpan="4" className="py-4 text-center text-gray-500">
                      No threats found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
