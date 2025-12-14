import React, { useRef, useMemo, useEffect, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Environment } from '@react-three/drei'
import * as THREE from 'three'

// Custom shader for glow effect
const glowShader = {
  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vPosition;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 glowColor;
    uniform float glowIntensity;
    uniform float time;
    varying vec3 vNormal;
    varying vec3 vPosition;
    
    void main() {
      float intensity = pow(0.7 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
      float pulse = sin(time * 2.0) * 0.5 + 0.5;
      vec3 glow = glowColor * intensity * glowIntensity * (1.0 + pulse * 0.5);
      gl_FragColor = vec4(glow, 1.0);
    }
  `
}

// Network Node Component
function NetworkNode({ node, position, onClick, isSelected, time }) {
  const meshRef = useRef()
  const glowRef = useRef()
  
  // Determine color based on attack type
  const getAttackColor = (attackType) => {
    switch (attackType) {
      case 'Normal': return '#00aaff'
      case 'Exploits': return '#9966ff'
      case 'Reconnaissance': return '#00ff88'
      case 'Worms': return '#ff3366'
      case 'DoS': return '#ff8844'
      case 'Fuzzers': return '#ffcc00'
      default: return '#00aaff'
    }
  }

  // Calculate glow intensity based on anomaly score
  const getGlowIntensity = () => {
    if (!node.is_anomaly) return 0.3
    const score = Math.abs(node.anomaly_score)
    return Math.min(score * 2, 2.0)
  }

  const color = getAttackColor(node.attack_type)
  const glowIntensity = getGlowIntensity()
  const shouldPulse = node.is_anomaly || node.attack_type !== 'Normal'

  // Pulsing animation
  useFrame(({ clock }) => {
    if (meshRef.current) {
      const scale = shouldPulse 
        ? 1 + Math.sin(clock.elapsedTime * 3) * 0.1 
        : 1
      meshRef.current.scale.setScalar(scale)
    }
    
    if (glowRef.current) {
      glowRef.current.material.uniforms.time.value = clock.elapsedTime
      glowRef.current.material.uniforms.glowColor.value = new THREE.Color(color)
      glowRef.current.material.uniforms.glowIntensity.value = glowIntensity
    }
  })

  return (
    <group position={position}>
      {/* Main node sphere */}
      <mesh 
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation()
          onClick(node)
        }}
        onPointerOver={(e) => {
          e.stopPropagation()
          document.body.style.cursor = 'pointer'
        }}
        onPointerOut={() => {
          document.body.style.cursor = 'default'
        }}
      >
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshStandardMaterial 
          color={color} 
          emissive={color}
          emissiveIntensity={0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      
      {/* Glow effect */}
      {shouldPulse && (
        <mesh ref={glowRef} scale={[1.5, 1.5, 1.5]}>
          <sphereGeometry args={[0.3, 32, 32]} />
          <shaderMaterial
            {...glowShader}
            uniforms={{
              glowColor: { value: new THREE.Color(color) },
              glowIntensity: { value: glowIntensity },
              time: { value: 0 }
            }}
            transparent
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </mesh>
      )}
      
      {/* Selection highlight */}
      {isSelected && (
        <mesh scale={[1.8, 1.8, 1.8]}>
          <ringGeometry args={[0.35, 0.45, 32]} />
          <meshBasicMaterial 
            color={color} 
            transparent 
            opacity={0.5}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}
    </group>
  )
}

// Network Edge Component (animated attack flow)
function NetworkEdge({ edge, sourcePos, targetPos, isActive }) {
  const curve = useMemo(() => {
    const midPoint = new THREE.Vector3()
      .addVectors(sourcePos, targetPos)
      .multiplyScalar(0.5)
      .add(new THREE.Vector3(0, 0.5, 0))
    
    return new THREE.QuadraticBezierCurve3(sourcePos, midPoint, targetPos)
  }, [sourcePos, targetPos])

  const getEdgeColor = () => {
    switch (edge.attack_type) {
      case 'Normal': return '#00aaff'
      case 'Exploits': return '#9966ff'
      case 'Reconnaissance': return '#00ff88'
      case 'Worms': return '#ff3366'
      case 'DoS': return '#ff8844'
      default: return '#00aaff'
    }
  }

  const color = getEdgeColor()

  return (
    <mesh>
      <tubeGeometry 
        args={[
          curve,
          50,
          0.02,
          8,
          false
        ]}
      />
      <meshStandardMaterial 
        color={color}
        emissive={color}
        emissiveIntensity={isActive ? 1 : 0.3}
        transparent
        opacity={isActive ? 1 : 0.5}
      />
    </mesh>
  )
}

// Main Network Scene
function NetworkScene({ nodes, edges, onNodeClick, selectedNode }) {
  const groupRef = useRef()
  const nodePositions = useRef(new Map())
  const [activeEdges, setActiveEdges] = useState(new Set())

  // Generate positions for nodes in 3D space
  const nodePositionsMap = useMemo(() => {
    const map = new Map()
    if (nodes.length === 0) return map
    
    const radius = 5
    nodes.forEach((node, index) => {
      const angle = (index / nodes.length) * Math.PI * 2
      const height = (index % 3 - 1) * 2
      const x = Math.cos(angle) * radius
      const z = Math.sin(angle) * radius
      map.set(node.id || node.ip, [x, height, z])
    })
    return map
  }, [nodes])

  // Animate edges
  useEffect(() => {
    if (edges.length === 0) return
    
    const interval = setInterval(() => {
      // Find edges with attacks
      const threatEdges = edges
        .filter(e => e.attack_type !== 'Normal')
        .slice(-10) // Animate last 10 threat edges
      
      setActiveEdges(new Set(threatEdges.map(e => `${e.source}-${e.target}`)))
      
      setTimeout(() => {
        setActiveEdges(new Set())
      }, 2000)
    }, 3000)

    return () => clearInterval(interval)
  }, [edges])

  // Slow rotation
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001
    }
  })

  // Auto-focus on threats
  useEffect(() => {
    const threatNodes = nodes.filter(n => n.is_anomaly || n.attack_type !== 'Normal')
    if (threatNodes.length > 0 && !selectedNode) {
      // Could implement camera focus here
    }
  }, [nodes, selectedNode])

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00ffff" />
      
      <group ref={groupRef}>
        {/* Render nodes */}
        {nodes.map((node) => {
          const pos = nodePositionsMap.get(node.id || node.ip)
          if (!pos) return null
          return (
            <NetworkNode
              key={node.id || node.ip}
              node={node}
              position={pos}
              onClick={onNodeClick}
              isSelected={selectedNode?.id === node.id || selectedNode?.ip === node.ip}
            />
          )
        })}

        {/* Render edges */}
        {edges.slice(-100).map((edge, index) => {
          if (!edge.source || !edge.target) return null
          
          const sourcePos = nodePositionsMap.get(edge.source)
          const targetPos = nodePositionsMap.get(edge.target)
          if (!sourcePos || !targetPos) return null
          
          const sourceVec = new THREE.Vector3(...sourcePos)
          const targetVec = new THREE.Vector3(...targetPos)
          const edgeKey = `${edge.source}-${edge.target}`
          
          return (
            <NetworkEdge
              key={`${edgeKey}-${index}`}
              edge={edge}
              sourcePos={sourceVec}
              targetPos={targetVec}
              isActive={activeEdges.has(edgeKey)}
            />
          )
        })}
      </group>
    </>
  )
}

export default function Network3D({ nodes, edges, onNodeClick, selectedNode }) {
  return (
    <div className="absolute inset-0">
      <Canvas
        gl={{ antialias: true, alpha: true }}
        camera={{ position: [0, 5, 15], fov: 50 }}
      >
        <PerspectiveCamera makeDefault position={[0, 5, 15]} />
        <NetworkScene 
          nodes={nodes} 
          edges={edges}
          onNodeClick={onNodeClick}
          selectedNode={selectedNode}
        />
        <OrbitControls 
          enableDamping
          dampingFactor={0.05}
          minDistance={5}
          maxDistance={30}
          autoRotate={false}
        />
        <Environment preset="night" />
      </Canvas>
      
      {/* UI Overlay */}
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-cyber-dark/80 backdrop-blur-sm rounded-lg p-4 border border-cyber-neon/30">
          <h2 className="text-cyber-neon text-xl font-bold mb-2">Network Status</h2>
          <p className="text-sm text-gray-300">Nodes: {nodes.length}</p>
          <p className="text-sm text-gray-300">Connections: {edges.length}</p>
          <p className="text-sm text-cyber-red">
            Threats: {nodes.filter(n => n.is_anomaly || n.attack_type !== 'Normal').length}
          </p>
        </div>
      </div>
    </div>
  )
}
