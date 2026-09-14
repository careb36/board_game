import { useEffect, useRef } from 'react'
import * as THREE from 'three'

const ROOM_LIGHT_TONES = {
  'Biblioteca': 0xc4a46f,
  'Salón Principal': 0xd6a35a,
  'Comedor': 0xb89452,
  'Cocina': 0x9bb89f,
  'Invernadero': 0x67b37c,
  'Galería de Arte': 0xa894c6,
  'Estudio': 0xc8b06e,
  'Dormitorio Principal': 0xb89a7f,
  'Sótano': 0x8fa0c8,
}

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

function ImmersiveRoomScene({ roomName }) {
  const mountRef = useRef(null)

  useEffect(() => {
    const mountNode = mountRef.current
    if (!mountNode) return undefined

    const scene = new THREE.Scene()
    scene.fog = new THREE.Fog(0x07090d, 2.4, 16)

    const camera = new THREE.PerspectiveCamera(
      62,
      mountNode.clientWidth / Math.max(mountNode.clientHeight, 1),
      0.1,
      50,
    )
    camera.position.set(0, 1.55, 5.4)

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(mountNode.clientWidth, mountNode.clientHeight)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    mountNode.appendChild(renderer.domElement)

    const tone = ROOM_LIGHT_TONES[roomName] ?? 0xd0a76a

    const ambient = new THREE.AmbientLight(0x8aa0b3, 0.22)
    scene.add(ambient)

    const fillLight = new THREE.PointLight(0x7ea0c2, 0.45, 18, 2)
    fillLight.position.set(-3, 2.2, -1)
    scene.add(fillLight)

    const lantern = new THREE.PointLight(tone, 2.4, 13, 2)
    lantern.position.set(0.4, 1.4, 0.8)
    scene.add(lantern)

    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x2b221b,
      roughness: 0.9,
      metalness: 0.08,
    })
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x3b3430,
      roughness: 0.86,
      metalness: 0.05,
    })

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(12, 18), floorMaterial)
    floor.rotation.x = -Math.PI * 0.5
    floor.position.y = 0
    scene.add(floor)

    const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(12, 18), wallMaterial)
    ceiling.rotation.x = Math.PI * 0.5
    ceiling.position.y = 3.2
    scene.add(ceiling)

    const backWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 3.2), wallMaterial)
    backWall.position.set(0, 1.6, -9)
    scene.add(backWall)

    const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(18, 3.2), wallMaterial)
    leftWall.rotation.y = Math.PI * 0.5
    leftWall.position.set(-6, 1.6, 0)
    scene.add(leftWall)

    const rightWall = new THREE.Mesh(new THREE.PlaneGeometry(18, 3.2), wallMaterial)
    rightWall.rotation.y = -Math.PI * 0.5
    rightWall.position.set(6, 1.6, 0)
    scene.add(rightWall)

    const corridorPieces = []
    for (let i = 0; i < 8; i += 1) {
      const width = 0.9 + (i % 2) * 0.4
      const mesh = new THREE.Mesh(
        new THREE.BoxGeometry(width, 1.8, 0.35),
        new THREE.MeshStandardMaterial({
          color: 0x5b5040,
          roughness: 0.78,
          metalness: 0.12,
        }),
      )
      mesh.position.set(i % 2 === 0 ? -4.8 : 4.8, 0.9, -7.2 + i * 1.75)
      mesh.rotation.y = i % 2 === 0 ? Math.PI / 10 : -Math.PI / 10
      scene.add(mesh)
      corridorPieces.push(mesh)
    }

    const pedestal = new THREE.Mesh(
      new THREE.CylinderGeometry(0.4, 0.6, 1.1, 16),
      new THREE.MeshStandardMaterial({ color: 0x4d4336, roughness: 0.75, metalness: 0.1 }),
    )
    pedestal.position.set(0, 0.55, -1.2)
    scene.add(pedestal)

    const artifact = new THREE.Mesh(
      new THREE.OctahedronGeometry(0.38, 0),
      new THREE.MeshStandardMaterial({ color: tone, emissive: tone, emissiveIntensity: 0.25 }),
    )
    artifact.position.set(0, 1.4, -1.2)
    scene.add(artifact)

    const dustCount = 180
    const dustGeometry = new THREE.BufferGeometry()
    const dustPositions = new Float32Array(dustCount * 3)
    for (let i = 0; i < dustCount; i += 1) {
      dustPositions[i * 3] = (Math.random() - 0.5) * 10
      dustPositions[i * 3 + 1] = 0.2 + Math.random() * 2.8
      dustPositions[i * 3 + 2] = -8 + Math.random() * 14
    }
    dustGeometry.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3))

    const dust = new THREE.Points(
      dustGeometry,
      new THREE.PointsMaterial({
        color: 0xf0d8a2,
        size: 0.025,
        transparent: true,
        opacity: 0.55,
      }),
    )
    scene.add(dust)

    const keyState = {}
    const onKeyDown = (event) => {
      keyState[event.code] = true
    }
    const onKeyUp = (event) => {
      keyState[event.code] = false
    }

    const onResize = () => {
      if (!mountNode.clientWidth || !mountNode.clientHeight) return
      camera.aspect = mountNode.clientWidth / mountNode.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(mountNode.clientWidth, mountNode.clientHeight)
    }

    window.addEventListener('resize', onResize)
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)

    let frameId = null
    let angle = 0
    let lastTime = performance.now()

    const animate = () => {
      const now = performance.now()
      const delta = Math.min((now - lastTime) / 1000, 0.05)
      lastTime = now
      angle += delta

      lantern.intensity = 2.1 + Math.sin(angle * 9) * 0.28 + Math.random() * 0.14
      artifact.rotation.y += delta * 0.65
      artifact.rotation.x = Math.sin(angle * 0.9) * 0.16
      artifact.position.y = 1.36 + Math.sin(angle * 1.7) * 0.08

      corridorPieces.forEach((piece, index) => {
        piece.position.y = 0.9 + Math.sin(angle * 0.7 + index * 0.8) * 0.025
      })

      const baseSpeed = (keyState.ShiftLeft || keyState.ShiftRight) ? 3.1 : 1.75
      const moveStep = baseSpeed * delta
      if (keyState.KeyW || keyState.ArrowUp) camera.position.z -= moveStep
      if (keyState.KeyS || keyState.ArrowDown) camera.position.z += moveStep
      if (keyState.KeyA || keyState.ArrowLeft) camera.position.x -= moveStep * 0.75
      if (keyState.KeyD || keyState.ArrowRight) camera.position.x += moveStep * 0.75

      camera.position.x = clamp(camera.position.x, -2.8, 2.8)
      camera.position.z = clamp(camera.position.z, -7.9, 5.4)

      camera.lookAt(0, 1.35, -7.5)
      renderer.render(scene, camera)
      frameId = requestAnimationFrame(animate)
    }

    onResize()
    animate()

    return () => {
      if (frameId) cancelAnimationFrame(frameId)
      window.removeEventListener('resize', onResize)
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)

      dustGeometry.dispose()
      dust.material.dispose()
      floor.geometry.dispose()
      floor.material.dispose()
      ceiling.geometry.dispose()
      ceiling.material.dispose()
      backWall.geometry.dispose()
      backWall.material.dispose()
      leftWall.geometry.dispose()
      leftWall.material.dispose()
      rightWall.geometry.dispose()
      rightWall.material.dispose()
      pedestal.geometry.dispose()
      pedestal.material.dispose()
      artifact.geometry.dispose()
      artifact.material.dispose()
      corridorPieces.forEach((piece) => {
        piece.geometry.dispose()
        piece.material.dispose()
      })

      renderer.dispose()
      if (renderer.domElement.parentNode === mountNode) {
        mountNode.removeChild(renderer.domElement)
      }
    }
  }, [roomName])

  return (
    <div className="immersive-canvas-shell">
      <div ref={mountRef} className="immersive-canvas" />
      <div className="immersive-help">
        <span>Vista inmersiva 3D</span>
        <small>Mueve con W A S D o flechas | Shift para avanzar más rápido</small>
      </div>
    </div>
  )
}

export default ImmersiveRoomScene