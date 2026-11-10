// Cena 3D: cenário escuro, três luzes, tone mapping ACES.
// Carrega card.glb se existir; senão desenha um marcador em blockout a partir de measurements.json.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import CameraControls from 'camera-controls';
import { STAGE_W, STAGE_H } from './layout.js';

// O storyboard usa mm, Z para cima. O GLB vem em metros, Y para cima.
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
CameraControls.install({ THREE });

export async function criaCena(container, { medidas, temGlb, pixelRatio }) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(pixelRatio);
  renderer.setSize(STAGE_W, STAGE_H);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x07090c);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.25;

  // Três luzes (principal, preenchimento, contraluz) mais ambiente. A mesma luz do início ao fim.
  scene.add(new THREE.AmbientLight(0xffffff, 0.25));
  const key = new THREE.DirectionalLight(0xfff3e6, 2.6);
  key.position.set(300, -400, 500);
  key.target.position.set(152, 68, 0);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -300, right: 300, top: 300, bottom: -300, near: 10, far: 1500 });
  key.shadow.bias = -0.0004;
  scene.add(key, key.target);
  const fill = new THREE.DirectionalLight(0xbcd2ff, 0.8);
  fill.position.set(-400, -200, 250);
  scene.add(fill);
  const rim = new THREE.DirectionalLight(0xffffff, 1.4);
  rim.position.set(-100, 500, 200);
  scene.add(rim);

  // Chão que só recebe sombra
  const chao = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: 0.45 }));
  chao.position.set(152, 68, -2);
  chao.receiveShadow = true;
  scene.add(chao);

  const camera = new THREE.PerspectiveCamera(30, STAGE_W / STAGE_H, 1, 6000);
  camera.up.set(0, 0, 1);
  const controls = new CameraControls(camera, renderer.domElement);
  controls.dollySpeed = 0.6;

  const placa = new THREE.Group();    // tudo em mm, Z para cima
  scene.add(placa);
  let blockout = null;
  let estado = null;      // explosão e destaque (só com GLB)
  const avisos = [];

  if (temGlb) {
    try {
      const loader = new GLTFLoader();
      const draco = new DRACOLoader();
      draco.setDecoderPath('draco/');
      loader.setDRACOLoader(draco);
      loader.setMeshoptDecoder(MeshoptDecoder);
      // No arquivo único o GLB vem embutido em base64; servido, vem por fetch.
      const embutido = window.__TOUR_GLB__;
      const gltf = embutido
        ? await loader.parseAsync(Uint8Array.from(atob(embutido), (c) => c.charCodeAt(0)).buffer, '')
        : await loader.loadAsync('data/card.glb');
      // O GLTFLoader tira os pontos dos nomes ("gpu.die" vira "gpudie"); o nome original fica em userData.
      gltf.scene.traverse((o) => { if (o.userData?.name) o.name = o.userData.name; });
      // metros, Y para cima -> milímetros, Z para cima
      const raiz = new THREE.Group();
      raiz.add(gltf.scene);
      raiz.scale.setScalar(1000);
      raiz.rotation.x = Math.PI / 2;
      gltf.scene.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      placa.add(raiz);
      estado = criaEstado3d(gltf.scene);
    } catch (e) {
      avisos.push(`falha ao carregar card.glb: ${e.message}; usando blockout`);
    }
  }
  if (!placa.children.length) blockout = desenhaBlockout(placa, medidas);

  // ---- câmera ----
  function ajustaCamera(c) {
    if (camera.fov !== c.fov) { camera.fov = c.fov; camera.updateProjectionMatrix(); }
    controls.setLookAt(c.px, c.py, c.pz, c.tx, c.ty, c.tz, false);
    controls.update(0);
  }

  // ---- âncoras ----
  const v = new THREE.Vector3();
  const acha = (nome) => placa.getObjectByName(nome) ?? null;
  function ancoraTela(nome) {
    const o = acha(nome);
    if (!o) return null;
    placa.updateMatrixWorld(true);
    camera.updateMatrixWorld(true);
    o.getWorldPosition(v);
    v.project(camera);
    return [(v.x * 0.5 + 0.5) * STAGE_W, (-v.y * 0.5 + 0.5) * STAGE_H];
  }

  return {
    renderer, camera, controls, scene, blockout, avisos,
    temAncora: (n) => !!acha(n),
    temPeca: (n) => !!estado && estado.temPeca(n),
    /** Aplica explosão (nível 0 a 8, contínuo) e destaque (fatores prévio e atual, mistura hl). */
    aplicaEstado(nivel, fPrev, fCur, hl) {
      if (!estado) return;
      estado.explode(nivel);
      estado.destaque(fPrev, fCur, hl);
      placa.updateMatrixWorld(true);
    },
    fatoresDe: (partes, tags) => (estado ? estado.fatoresDe(partes, tags) : null),
    ancoraTela,
    ajustaCamera,
    desenha() { renderer.render(scene, camera); },
  };
}

/** Marcador em blockout: envelope, dois ventiladores e o retângulo do chip. Não é modelo. */
function desenhaBlockout(pai, medidas) {
  const m = (k) => medidas?.[k]?.value_mm;
  const L = m('card_envelope_length') ?? 304.8;
  const H = m('card_envelope_height') ?? 137.16;
  const T = m('two_slot_pitch') ?? 40.64;           // espessura sem fonte: provisória
  const dFan = m('fan_ring_outer_diameter') ?? 115;
  const fx = [m('fan1_center_from_bracket_end') ?? 61, m('fan2_center_from_bracket_end') ?? 244];
  const g = new THREE.Group();
  g.name = 'blockout';
  const corpo = new THREE.Mesh(new THREE.BoxGeometry(L, H, T), new THREE.MeshStandardMaterial({ color: 0x2b3038, metalness: 0.5, roughness: 0.55 }));
  corpo.position.set(L / 2, H / 2, T / 2);
  corpo.castShadow = corpo.receiveShadow = true;
  g.add(corpo);
  const arestas = new THREE.LineSegments(new THREE.EdgesGeometry(corpo.geometry), new THREE.LineBasicMaterial({ color: 0x59626f }));
  arestas.position.copy(corpo.position);
  g.add(arestas);
  const matFan = new THREE.MeshStandardMaterial({ color: 0x14171c, metalness: 0.2, roughness: 0.8 });
  for (const x of fx) {
    const d = new THREE.Mesh(new THREE.CylinderGeometry(dFan / 2, dFan / 2, 1.5, 64), matFan);
    d.rotation.x = Math.PI / 2;                       // eixo do cilindro em Z
    d.position.set(x, H / 2, T + 0.75);
    d.castShadow = true;
    g.add(d);
    const anel = new THREE.Mesh(new THREE.TorusGeometry(dFan / 2, 0.6, 8, 64), new THREE.MeshBasicMaterial({ color: 0x59626f }));
    anel.position.set(x, H / 2, T + 1.6);
    g.add(anel);
  }
  // Chip: tamanho provisório (não há medida); só marca a região entre os ventiladores.
  const chip = new THREE.Mesh(new THREE.BoxGeometry(30, 30, 0.8), new THREE.MeshStandardMaterial({ color: 0x6b7686, metalness: 0.3, roughness: 0.5 }));
  chip.position.set((fx[0] + fx[1]) / 2, H / 2, T + 0.4);
  g.add(chip);
  pai.add(g);
  return g;
}

const DIM = 0.15;          // opacidade das peças esmaecidas
const suave = (x) => x * x * (3 - 2 * x);

/**
 * Estado de explosão e de destaque sobre o GLB (nós em metros, Y para cima, dentro de gltf.scene).
 * Explosão: nível n (0 = montada, 1 a 8 = E1 a E8, contínuo). A peça de estágio k desloca
 * explode_cad.dir * distance (referencial CAD, relativo à peça-mãe) com progresso
 * suave(clamp(n - (k - 1), 0, 1)). Mover o nó leva os filhos junto.
 * Destaque: cada malha ganha uma cópia própria do material (os originais não mudam); a opacidade
 * é recalculada a cada quadro a partir do estado, sem acumular nada.
 */
function criaEstado3d(raiz) {
  const nos = [];
  const pecas = new Map();       // nome -> true
  const malhas = [];
  raiz.traverse((o) => {
    const u = o.userData ?? {};
    if (o.name) pecas.set(o.name, o);
    const est = /^E([1-8])$/.exec(u.stage ?? '');
    const ex = u.explode_cad;
    if (est && ex && ex.distance > 0) {
      const [dx, dy, dz] = ex.dir;            // CAD (Z para cima) -> glTF (Y para cima): (x, z, -y)
      const d = ex.distance / 1000;
      nos.push({ o, base: o.position.clone(), estagio: Number(est[1]), off: new THREE.Vector3(dx * d, dz * d, -dy * d), p: -1 });
    }
    if (o.isMesh) {
      const nomes = new Set();
      for (let a = o; a; a = a.parent) {
        if (a.name) nomes.add(a.name);
        if (a.userData?.instance_of) nomes.add(a.userData.instance_of);
        if (a.userData?.group) nomes.add(`tag:${a.userData.group}`);
      }
      const mats = (Array.isArray(o.material) ? o.material : [o.material]).map((m) => m.clone());
      o.material = Array.isArray(o.material) ? mats : mats[0];
      malhas.push({ o, nomes, mats, base: mats.map((m) => ({ op: m.opacity, tr: m.transparent, dw: m.depthWrite })), f: 1 });
    }
  });

  return {
    temPeca: (n) => pecas.has(n),
    explode(nivel) {
      for (const n of nos) {
        const p = suave(Math.min(1, Math.max(0, nivel - (n.estagio - 1))));
        if (p === n.p) continue;
        n.p = p;
        n.o.position.copy(n.base).addScaledVector(n.off, p);
      }
    },
    /** Fatores de opacidade por malha para um conjunto de peças (ids) e de tags; null = nada esmaece. */
    fatoresDe(partes, tags) {
      const sel = [...(partes ?? []), ...(tags ?? []).map((t) => `tag:${t}`)];
      const ok = sel.filter((n) => pecas.has(n) || n.startsWith('tag:'));
      if (!ok.length) return null;
      return malhas.map((m) => (ok.some((n) => m.nomes.has(n)) ? 1 : DIM));
    },
    destaque(fPrev, fCur, hl) {
      malhas.forEach((m, i) => {
        const a = fPrev ? fPrev[i] : 1, b = fCur ? fCur[i] : 1;
        const f = a + (b - a) * hl;
        if (f === m.f) return;
        m.f = f;
        m.mats.forEach((mt, k) => {
          const bs = m.base[k];
          mt.opacity = bs.op * f;
          mt.transparent = bs.tr || f < 0.999;
          mt.depthWrite = f < 0.999 ? false : bs.dw;
        });
      });
    },
  };
}
