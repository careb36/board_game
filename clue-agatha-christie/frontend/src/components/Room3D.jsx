import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html, Float, Sparkles, Stars } from '@react-three/drei';
import * as THREE from 'three';

// Datos detallados de cada habitación
const ROOM_DETAILS = {
  salon: {
    name: 'Salón Principal',
    description: 'Elegante salón victoriano con chimenea de mármol, candelabros de cristal y retratos familiares. Aquí se servía el té de la tarde.',
    color: '#8B4513',
    details: [
      { position: [0, 1.5, -2], text: 'Chimenea de Mármol', icon: '🔥' },
      { position: [-2, 1, 0], text: 'Retrato Familiar', icon: '🖼️' },
      { position: [2, 1, 0], text: 'Candelabro', icon: '🕯️' },
      { position: [0, 0.5, 2], text: 'Mesa de Té', icon: '☕' },
    ],
    clues: ['Huella de ceniza', 'Carta arrugada', 'Medallón roto']
  },
  biblioteca: {
    name: 'Biblioteca',
    description: 'Imponente biblioteca con estantes de roble hasta el techo, escalera móvil y un escritorio antiguo cubierto de polvo.',
    color: '#2F4F4F',
    details: [
      { position: [-2.5, 1, 0], text: 'Estanterías de Roble', icon: '📚' },
      { position: [2, 0.5, -2], text: 'Escritorio Antiguo', icon: '🖋️' },
      { position: [0, 2, 0], text: 'Escalera Móvil', icon: '🪜' },
      { position: [2.5, 1, 2], text: 'Globo Terráqueo', icon: '🌍' },
    ],
    clues: ['Libro abierto', 'Tinta derramada', 'Llave antigua']
  },
  comedor: {
    name: 'Comedor Formal',
    description: 'Suntuoso comedor con mesa para 12 personas, vajilla de porcelana fina y una lámpara de araña impresionante.',
    color: '#800020',
    details: [
      { position: [0, 0.8, 0], text: 'Mesa para 12', icon: '🍽️' },
      { position: [0, 2.5, 0], text: 'Lámpara de Araña', icon: '💡' },
      { position: [-2.5, 1, 0], text: 'Aparador de Porcelana', icon: '🏺' },
      { position: [2.5, 1, -2], text: 'Ventanal Gótico', icon: '🪟' },
    ],
    clues: ['Copa rota', 'Servilleta manchada', 'Anillo perdido']
  },
  cocina: {
    name: 'Cocina',
    description: 'Amplia cocina victoriana con estufa de hierro, utensilios colgados y despensa llena de provisiones.',
    color: '#CD853F',
    details: [
      { position: [-2, 1, -2], text: 'Estufa de Hierro', icon: '🔥' },
      { position: [2, 1.5, 0], text: 'Utensilios Colgados', icon: '🍴' },
      { position: [0, 0.5, 2], text: 'Mesa de Preparación', icon: '🔪' },
      { position: [2.5, 0.5, 2.5], text: 'Despensa', icon: '🥫' },
    ],
    clues: ['Cuchillo faltante', 'Receta rasgada', 'Frasco de veneno']
  },
  invernadero: {
    name: 'Invernadero',
    description: 'Exótico invernadero con plantas tropicales, fuente central y bancos de hierro forjado para descansar.',
    color: '#228B22',
    details: [
      { position: [0, 1, 0], text: 'Fuente Central', icon: '⛲' },
      { position: [-2.5, 0.5, -2], text: 'Helechos Gigantes', icon: '🌿' },
      { position: [2.5, 0.5, 2], text: 'Orquídeas Raras', icon: '🌸' },
      { position: [-2, 0.3, 2], text: 'Banco de Hierro', icon: '🪑' },
    ],
    clues: ['Tierra removida', 'Tijeras de podar', 'Flor marchita']
  },
  estudio: {
    name: 'Estudio del Lord',
    description: 'Privado estudio con mapa del mundo, telescopio, y documentos confidenciales sobre la mesa.',
    color: '#483D8B',
    details: [
      { position: [2, 0.8, -2], text: 'Escritorio de Caoba', icon: '🗂️' },
      { position: [-2, 1.5, 0], text: 'Telescopio', icon: '🔭' },
      { position: [0, 1, 2], text: 'Mapa del Mundo', icon: '🗺️' },
      { position: [2.5, 0.5, 2], text: 'Caja Fuerte', icon: '🔒' },
    ],
    clues: ['Documento cifrado', 'Sobre lacrado', 'Pluma dorada']
  },
  capilla: {
    name: 'Capilla Privada',
    description: 'Pequeña capilla con vitrales coloridos, altar de madera tallada y bancos para la familia.',
    color: '#4B0082',
    details: [
      { position: [0, 1.5, -2.5], text: 'Altar Tallado', icon: '⛪' },
      { position: [-2, 2, 0], text: 'Vitrales Coloridos', icon: '🎨' },
      { position: [2, 0.5, 0], text: 'Bancos de Madera', icon: '🪑' },
      { position: [0, 2.5, 0], text: 'Crucifijo', icon: '✝️' },
    ],
    clues: ['Velador caído', 'Libro de oraciones', 'Rosario roto']
  },
  dormitorio: {
    name: 'Dormitorio Principal',
    description: 'Lujoso dormitorio con cama con dosel, tocador de plata y balcón con vista a los jardines.',
    color: '#DC143C',
    details: [
      { position: [0, 0.6, 0], text: 'Cama con Dosel', icon: '🛏️' },
      { position: [2.5, 1, -2], text: 'Tocador de Plata', icon: '💄' },
      { position: [-2.5, 1, 2], text: 'Balcón', icon: '🌙' },
      { position: [2.5, 0.5, 2], text: 'Armario Empotrado', icon: '🚪' },
    ],
    clues: ['Diario íntimo', 'Frasco de perfume', 'Pañuelo bordado']
  },
  sotano: {
    name: 'Sótano',
    description: 'Oscuro sótano con barricas de vino, herramientas antiguas y pasadizos secretos.',
    color: '#2F2F2F',
    details: [
      { position: [-2, 0.5, -2], text: 'Barricas de Vino', icon: '🍷' },
      { position: [2, 1, 0], text: 'Herramientas Antiguas', icon: '🔧' },
      { position: [0, 0.3, 2.5], text: 'Pasadizo Secreto', icon: '🚪' },
      { position: [2.5, 0.5, 2.5], text: 'Caldera', icon: '🔥' },
    ],
    clues: ['Botella vacía', 'Llave oxidada', 'Mapa del sótano']
  }
};

// Componente para un objeto interactuable en 3D
function InteractiveObject({ position, text, icon, onClick, isSelected }) {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current && hovered) {
      meshRef.current.rotation.y += 0.02;
      meshRef.current.scale.setScalar(1.1);
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1);
    }
  });

  return (
    <group position={position}>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.3}>
        <mesh
          ref={meshRef}
          onClick={(e) => {
            e.stopPropagation();
            onClick({ text, icon });
          }}
          onPointerOver={() => {
            document.body.style.cursor = 'pointer';
            setHovered(true);
          }}
          onPointerOut={() => {
            document.body.style.cursor = 'default';
            setHovered(false);
          }}
        >
          <boxGeometry args={[0.4, 0.4, 0.4]} />
          <meshStandardMaterial
            color={hovered ? '#FFD700' : isSelected ? '#FF6B6B' : '#C0C0C0'}
            emissive={hovered ? '#FFD700' : isSelected ? '#FF6B6B' : '#000000'}
            emissiveIntensity={hovered ? 0.5 : 0}
            transparent
            opacity={0.9}
          />
        </mesh>
      </Float>
      <Text
        position={[0, 0.6, 0]}
        fontSize={0.15}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="black"
      >
        {icon}
      </Text>
      {hovered && (
        <Html distanceFactor={10}>
          <div style={{
            background: 'rgba(0,0,0,0.8)',
            padding: '8px 12px',
            borderRadius: '8px',
            color: 'white',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            pointerEvents: 'none',
            border: '2px solid #FFD700'
          }}>
            {text}
          </div>
        </Html>
      )}
    </group>
  );
}

// Paredes de la habitación
function RoomWalls({ color, roomKey }) {
  const wallMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: color,
    side: THREE.DoubleSide,
    roughness: 0.8,
    metalness: 0.2,
  }), [color]);

  const floorMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: new THREE.Color(color).multiplyScalar(0.7),
    roughness: 0.9,
    metalness: 0.1,
  }), [color]);

  return (
    <group>
      {/* Suelo */}
      <mesh position={[0, -0.1, 0]} material={floorMaterial} receiveShadow>
        <boxGeometry args={[6, 0.2, 6]} />
      </mesh>
      
      {/* Paredes */}
      <mesh position={[0, 1.5, -3]} material={wallMaterial} receiveShadow castShadow>
        <boxGeometry args={[6, 3, 0.2]} />
      </mesh>
      <mesh position={[0, 1.5, 3]} material={wallMaterial} receiveShadow castShadow>
        <boxGeometry args={[6, 3, 0.2]} />
      </mesh>
      <mesh position={[-3, 1.5, 0]} material={wallMaterial} receiveShadow castShadow>
        <boxGeometry args={[0.2, 3, 6]} />
      </mesh>
      <mesh position={[3, 1.5, 0]} material={wallMaterial} receiveShadow castShadow>
        <boxGeometry args={[0.2, 3, 6]} />
      </mesh>
      
      {/* Techo parcialmente abierto para ver mejor */}
      <mesh position={[0, 3.5, 0]} rotation={[Math.PI / 2, 0, 0]} material={new THREE.MeshBasicMaterial({ 
        color: 0x1a1a2e, 
        transparent: true, 
        opacity: 0.3,
        side: THREE.DoubleSide
      })}>
        <planeGeometry args={[6, 6]} />
      </mesh>
    </group>
  );
}

// Componente principal de la habitación 3D
export function Room3D({ roomKey, onSelectDetail, selectedDetail }) {
  const room = ROOM_DETAILS[roomKey];
  
  if (!room) {
    return <div style={{ color: 'white', padding: '20px' }}>Habitación no encontrada</div>;
  }

  return (
    <div style={{ 
      width: '100%', 
      height: '500px', 
      position: 'relative',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      borderRadius: '16px',
      overflow: 'hidden',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
    }}>
      <Canvas shadows camera={{ position: [8, 6, 8], fov: 50 }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={1} castShadow />
        <spotLight
          position={[0, 10, 0]}
          angle={0.5}
          penumbra={1}
          intensity={0.8}
          castShadow
        />
        
        {/* Efectos atmosféricos */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <Sparkles count={50} scale={8} size={2} speed={0.4} opacity={0.5} color="#FFD700" />
        
        {/* Habitación */}
        <RoomWalls color={room.color} roomKey={roomKey} />
        
        {/* Objetos interactivos */}
        {room.details.map((detail, index) => (
          <InteractiveObject
            key={index}
            position={detail.position}
            text={detail.text}
            icon={detail.icon}
            onClick={onSelectDetail}
            isSelected={selectedDetail?.text === detail.text}
          />
        ))}
        
        {/* Controles de cámara */}
        <OrbitControls
          enablePan={false}
          enableZoom={true}
          minDistance={5}
          maxDistance={15}
          minPolarAngle={Math.PI / 6}
          maxPolarAngle={Math.PI / 2.5}
        />
      </Canvas>
      
      {/* Overlay de información */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        right: '20px',
        pointerEvents: 'none'
      }}>
        <h2 style={{
          margin: 0,
          color: '#FFD700',
          fontSize: '24px',
          textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
          fontFamily: 'Georgia, serif'
        }}>
          {room.name}
        </h2>
        <p style={{
          margin: '8px 0 0 0',
          color: 'white',
          fontSize: '14px',
          textShadow: '1px 1px 2px rgba(0,0,0,0.8)',
          maxWidth: '400px',
          lineHeight: '1.4'
        }}>
          {room.description}
        </p>
      </div>
      
      {/* Panel de pistas */}
      {selectedDetail && (
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '20px',
          right: '20px',
          background: 'rgba(0,0,0,0.85)',
          padding: '16px',
          borderRadius: '12px',
          border: '2px solid #FFD700',
          pointerEvents: 'auto',
          backdropFilter: 'blur(10px)'
        }}>
          <h3 style={{
            margin: '0 0 8px 0',
            color: '#FFD700',
            fontSize: '16px'
          }}>
            {selectedDetail.icon} {selectedDetail.text}
          </h3>
          <div style={{ color: 'white', fontSize: '13px', marginBottom: '12px' }}>
            <strong>Pistas posibles en este objeto:</strong>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {room.clues.map((clue, idx) => (
              <span key={idx} style={{
                background: 'linear-gradient(135deg, #8B4513, #A0522D)',
                padding: '6px 12px',
                borderRadius: '20px',
                fontSize: '12px',
                color: 'white',
                border: '1px solid #FFD700'
              }}>
                🔍 {clue}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Instrucciones */}
      {!selectedDetail && (
        <div style={{
          position: 'absolute',
          bottom: '20px',
          right: '20px',
          background: 'rgba(0,0,0,0.7)',
          padding: '12px',
          borderRadius: '8px',
          color: 'white',
          fontSize: '12px',
          pointerEvents: 'none'
        }}>
          🖱️ Click en objetos para investigar<br/>
          🔄 Arrastra para rotar la cámara<br/>
          🔍 Zoom con la rueda del ratón
        </div>
      )}
    </div>
  );
}

export default Room3D;
