// Cena 3D: cenário escuro, três luzes, tone mapping ACES.
// Carrega card.glb se existir; senão desenha um marcador em blockout a partir de measurements.json.
// Com tema realista (Keynote), materiais, luz, chão, destaque e pós-processamento vêm de lookdev.js.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import CameraControls from 'camera-controls';
import { LineSegments2 } from 'three/examples/jsm/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/examples/jsm/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { STAGE_W, STAGE_H } from './layout.js';
import { QUALIDADES, aplicaMateriais, amostraAcumulacao, criaEstudio, criaPos, preparaMaterial } from './lookdev.js';

// O storyboard usa mm, Z para cima. O GLB vem em metros, Y para cima.
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
CameraControls.install({ THREE });

export async function criaCena(container, { medidas, temGlb, pixelRatio, tema = null, qualidade = null, luz = null, capture = false, acumula = null }) {
  const tc = tema?.cena ?? null;     // parâmetros de cena do tema; null = cena padrão
  const R = tc?.realista ?? null;    // modo realista (lookdev.js)
  // Qualidade: a pedida na URL; sem pedido, a média, com troca automática para a baixa se o
  // notebook não aguentar (medida nos primeiros quadros ao vivo; nunca no modo de captura).
  let nivelQ = R ? (qualidade ?? 'media') : null;
  const autoQ = !!R && !qualidade && !capture;
  const q0 = R ? QUALIDADES[nivelQ] : null;
  const pr = R ? Math.min(pixelRatio, q0.prMax) : pixelRatio;
  // Com tema, o canvas é transparente: o fundo do tema (canvas 2D sob o palco) aparece atrás da placa
  // e dos diagramas, e a passagem 3D para diagrama não troca de fundo.
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, alpha: !!tc });
  renderer.setPixelRatio(pr);
  renderer.setSize(STAGE_W, STAGE_H);
  renderer.toneMapping = R ? THREE.AgXToneMapping : THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = R ? R.exposicao : tc?.exposicao ?? 1.0;
  renderer.shadowMap.enabled = R ? q0.sombra > 0 : true;
  renderer.shadowMap.type = R ? THREE.PCFSoftShadowMap : tc?.sombraSuave ? THREE.PCFShadowMap : THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  if (tc) renderer.setClearColor(0x000000, 0);
  else scene.background = new THREE.Color(0x07090c);
  let estudio = null;
  if (R) {
    estudio = criaEstudio({ renderer, scene, cfg: R, q: q0, medidas, luz });
  } else {
    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = tc?.ambiente ?? 0.25;
  }

  if (R) {
    // luzes e chão do estúdio já estão na cena (lookdev.js)
  } else if (!tc) {
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
  } else {
    // Luzes do tema: a primeira é a principal (com sombra, se o tema pedir); as outras, preenchimento e recorte.
    scene.add(new THREE.AmbientLight(0xffffff, tc.ambienteLuz ?? 0.2));
    for (const l of tc.luzes) {
      const luz = new THREE.DirectionalLight(l.cor, l.i);
      luz.position.set(...l.pos);
      luz.target.position.set(152, 68, 0);
      if (l.sombra && tc.sombra > 0) {
        luz.castShadow = true;
        luz.shadow.mapSize.set(2048, 2048);
        Object.assign(luz.shadow.camera, { left: -300, right: 300, top: 300, bottom: -300, near: 10, far: 1500 });
        luz.shadow.bias = -0.0004;
        if (tc.sombraSuave) luz.shadow.radius = 5;
      }
      scene.add(luz, luz.target);
    }
  }

  // Chão que só recebe sombra
  if (!R) {
    const chao = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: tc ? tc.sombra : 0.45 }));
    chao.position.set(152, 68, -2);
    chao.receiveShadow = true;
    if (!tc || tc.sombra > 0) scene.add(chao);
    if (tc?.contato) scene.add(sombraContato(medidas, tc.contato));
  }

  const camera = new THREE.PerspectiveCamera(30, STAGE_W / STAGE_H, 1, 6000);
  camera.up.set(0, 0, 1);
  const controls = new CameraControls(camera, renderer.domElement);
  controls.dollySpeed = 0.6;

  const placa = new THREE.Group();    // tudo em mm, Z para cima
  scene.add(placa);
  let blockout = null;
  let estado = null;      // explosão e destaque (só com GLB)
  const avisos = [];
  let materiais = null;   // relatório do lookdev: malha, material, por quê
  let caixas = null;      // id da peça -> caixa das malhas próprias em repouso (mm), para caminhos e mergulho
  const corRealce = R ? new THREE.Color(R.realce.cor).multiplyScalar(R.realce.forca) : null;

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
      if (R) materiais = aplicaMateriais(gltf.scene, { medidas, q: q0, corRealce });
      else if (tc) aplicaTema(gltf.scene, tc);
      placa.add(raiz);
      estado = criaEstado3d(gltf.scene, R ? { corRealce, apaga: R.apaga } : null);
      placa.updateMatrixWorld(true);
      caixas = montaCaixas(gltf.scene);
    } catch (e) {
      avisos.push(`falha ao carregar card.glb: ${e.message}; usando blockout`);
    }
  }
  if (!placa.children.length) blockout = desenhaBlockout(placa, medidas);

  // ---- câmera ----
  function ajustaCamera(c) {
    // Planos de recorte acompanham a distância ao alvo: com near fixo em 1 mm, superfícies
    // paralelas a poucos mm de uma pele fina vazavam através dela (falta de precisão de profundidade).
    const dist = Math.hypot(c.px - c.tx, c.py - c.ty, c.pz - c.tz);
    const near = Math.min(Math.max(1, dist * 0.08), 60);
    const far = Math.max(2000, dist * 12);
    if (camera.fov !== c.fov || camera.near !== near || camera.far !== far) {
      camera.fov = c.fov; camera.near = near; camera.far = far; camera.updateProjectionMatrix();
    }
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

  // ---- caixas das peças ----
  const vTmp = new THREE.Vector3();
  /** Caixa das malhas próprias da peça (sem as peças filhas) no estado atual da explosão, em mm. */
  function caixaPeca(id) {
    const c = caixas?.get(id);
    if (!c) return null;
    c.no.getWorldPosition(vTmp).sub(c.p0);          // a explosão só translada os nós
    return { min: c.caixa.min.clone().add(vTmp), max: c.caixa.max.clone().add(vTmp) };
  }
  /** Caixa de um nó qualquer (instância, peça com filhos) no estado atual, em mm; nó sem malha vira ponto. */
  const bTmp = new THREE.Box3();
  function caixaNo(nome) {
    const o = acha(nome);
    if (!o) return null;
    bTmp.makeEmpty().expandByObject(o);
    if (bTmp.isEmpty()) { o.getWorldPosition(vTmp); return { min: vTmp.clone(), max: vTmp.clone() }; }
    return { min: bTmp.min.clone(), max: bTmp.max.clone() };
  }
  /** Posição de um nó (âncora ou peça) em mm, no estado atual. */
  function pontoNo(nome) {
    const o = acha(nome);
    if (!o) return null;
    return o.getWorldPosition(new THREE.Vector3());
  }

  // ---- quadro ----
  let pos = null;
  const montaPos = () => {
    pos?.dispose();
    const q = QUALIDADES[nivelQ];
    pos = q.pos ? criaPos({ renderer, scene, camera, q, W: Math.round(STAGE_W * renderer.getPixelRatio()), H: Math.round(STAGE_H * renderer.getPixelRatio()), cfg: R }) : null;
  };
  if (R) montaPos();
  let nivelAtual = 0;
  const alvo = new THREE.Vector3();
  const medida = { n: 0, soma: 0, ult: 0, pulou: true };
  /** Troca de qualidade em execução (só para baixo, pela medição automática). */
  function defineQualidade(nq) {
    if (!R || nq === nivelQ) return;
    nivelQ = nq;
    const q = QUALIDADES[nq];
    renderer.setPixelRatio(Math.min(pixelRatio, q.prMax));
    if (renderer.shadowMap.enabled !== q.sombra > 0) {
      renderer.shadowMap.enabled = q.sombra > 0;
      scene.traverse((o) => { if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => { m.needsUpdate = true; }); });
    }
    montaPos();
    console.info(`[lookdev] qualidade ${nq}`);
  }

  // ---- acumulação de quadros (modo realista, média e alta) ----
  // Com a cena parada, cada quadro novo é uma amostra com deslocamento de subpixel, luz principal num
  // disco e espiral da profundidade de campo girada; a tela mostra a média. A assinatura do estado
  // (câmera, explosão, destaque, qualidade) diz se algo se mexeu: mexeu, recomeça da amostra 0, que é o
  // quadro normal. Ao vivo, uma amostra por quadro até o alvo; depois disso nada é desenhado (a imagem
  // fica no canvas, preserveDrawingBuffer). Na captura, o seek desenha de uma vez todas as amostras que
  // faltam: a imagem é função só do estado, e a sequência de amostras é fixa.
  const ac = { sig: null, n: 0 };
  const idsFat = new WeakMap();
  let proxIdFat = 1;
  const idFat = (f) => { if (!f) return 0; if (!idsFat.has(f)) idsFat.set(f, proxIdFat++); return idsFat.get(f); };
  let destaqueAtual = '';
  const nAcumDe = () => (acumula != null ? acumula : QUALIDADES[nivelQ]?.acum ?? 0);
  const r5 = (x) => Math.round(x * 1e5);
  function assinatura() {
    const p = camera.position, o = camera.quaternion;
    return `${[p.x, p.y, p.z, o.x, o.y, o.z, o.w, camera.fov, nivelAtual].map(r5).join(',')}|${destaqueAtual}|${nivelQ}|${renderer.getPixelRatio()}`;
  }
  function amostra(k) {
    const am = amostraAcumulacao(k, R.acumula);
    estudio.atualiza(camera, nivelAtual, am?.luz ?? null);
    if (pos) pos.render(camera.position.distanceTo(controls.getTarget(alvo)), k, am);
    else renderer.render(scene, camera);
  }
  /**
   * Desenha o quadro. parado: a cena não se mexe neste instante (a captura sabe pela timeline; ao vivo
   * vale a assinatura). Devolve true se desenhou algo.
   */
  function desenha({ parado = true } = {}) {
    if (!R) { renderer.render(scene, camera); return true; }
    camera.updateMatrixWorld(true);
    const sig = assinatura();
    const alvoN = pos && parado ? Math.max(1, nAcumDe()) : 1;
    if (sig !== ac.sig || ac.n > alvoN) { ac.sig = sig; ac.n = 0; }
    if (ac.n >= alvoN) { medida.pulou = true; return false; }
    const ate = capture ? alvoN : ac.n + 1;
    for (; ac.n < ate; ac.n++) amostra(ac.n);
    pos?.exibe();
    if (autoQ && nivelQ === 'media') {
      // primeira medição: 20 quadros de aquecimento, depois 60 quadros; abaixo de 28 qps, baixa.
      // Máquina claramente lenta (abaixo de 10 qps nos 10 primeiros quadros medidos) decide logo.
      // Só conta o intervalo entre dois quadros desenhados seguidos (parada da acumulação não conta).
      const t = performance.now();
      if (!medida.pulou) {
        medida.n++;
        if (medida.n > 20) medida.soma += t - medida.ult;
        if (medida.n === 30 && 10000 / medida.soma < 10) defineQualidade('baixa');
        else if (medida.n === 80) {
          const qps = 60000 / medida.soma;
          if (qps < 28) defineQualidade('baixa');
          else console.info(`[lookdev] qualidade media mantida (${qps.toFixed(0)} qps)`);
        }
      }
      medida.ult = t; medida.pulou = false;
    }
    return true;
  }

  // ---- mergulho: pose da câmera que põe uma peça num retângulo da tela ----
  const camTmp = new THREE.PerspectiveCamera(30, STAGE_W / STAGE_H, 1, 6000);
  camTmp.up.set(0, 0, 1);
  /** Cantos da face da peça voltada para fora da placa (normal: do centro do PCB para a peça, em z). */
  function faceDe(id, ref = 'pcb.main') {
    const c = caixaPeca(id);
    if (!c) return null;
    const r = caixaPeca(ref);
    const zc = (c.min.z + c.max.z) / 2;
    const sz = r ? Math.sign(zc - (r.min.z + r.max.z) / 2) || 1 : 1;
    const z = sz > 0 ? c.max.z : c.min.z;
    const cantos = [[c.min.x, c.min.y], [c.max.x, c.min.y], [c.max.x, c.max.y], [c.min.x, c.max.y]].map(([x, y]) => new THREE.Vector3(x, y, z));
    return { cantos, centro: new THREE.Vector3((c.min.x + c.max.x) / 2, (c.min.y + c.max.y) / 2, z), normal: new THREE.Vector3(0, 0, sz) };
  }
  /** Retângulo envolvente (px do palco) de pontos em mm vistos por uma câmera; null se algum ficar atrás. */
  function retTela(cam, pts) {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const p of pts) {
      v.copy(p).project(cam);
      if (v.z > 1) return null;
      const sx = (v.x * 0.5 + 0.5) * STAGE_W, sy = (-v.y * 0.5 + 0.5) * STAGE_H;
      x0 = Math.min(x0, sx); y0 = Math.min(y0, sy); x1 = Math.max(x1, sx); y1 = Math.max(y1, sy);
    }
    return [x0, y0, x1 - x0, y1 - y0];
  }
  /**
   * Pose de câmera (formato do storyboard: px..tz, fov) que olha a face externa da peça quase de frente
   * (inclinação em graus a partir da normal, no azimute de `de`) e põe a largura da face, projetada, em
   * rect = [x, y, w, h] (px do palco), centrada nele. Só vale no estado de explosão atual.
   */
  function poseMergulho({ peca, rect, fov = 30, inclinacao = 8, de = null }) {
    const f = faceDe(peca);
    if (!f) return null;
    const az = new THREE.Vector3(1, -1, 0);
    if (de) az.set(de.px - de.tx, de.py - de.ty, 0);
    if (az.lengthSq() < 1e-6) az.set(0, -1, 0);
    az.normalize();
    const inc = (inclinacao * Math.PI) / 180;
    const dir = f.normal.clone().multiplyScalar(Math.cos(inc)).addScaledVector(az, Math.sin(inc)).normalize();
    camTmp.fov = fov; camTmp.updateProjectionMatrix();
    const larg = Math.hypot(f.cantos[1].x - f.cantos[0].x, f.cantos[1].y - f.cantos[0].y);
    let d = (larg / 2) / (Math.tan((fov * Math.PI) / 360) * (STAGE_W / STAGE_H) * (rect[2] / STAGE_W));
    const T = f.centro.clone();
    const dx = new THREE.Vector3(), dy = new THREE.Vector3();
    for (let i = 0; i < 8; i++) {
      camTmp.position.copy(T).addScaledVector(dir, d);
      camTmp.lookAt(T);
      camTmp.updateMatrixWorld(true);
      const r = retTela(camTmp, f.cantos);
      if (!r) return null;
      d *= r[2] / rect[2];
      // desloca o alvo no plano da tela para o centro da face cair no centro do retângulo
      const mmPorPx = (2 * d * Math.tan((fov * Math.PI) / 360)) / STAGE_H;
      dx.setFromMatrixColumn(camTmp.matrixWorld, 0);
      dy.setFromMatrixColumn(camTmp.matrixWorld, 1);
      const ex = (rect[0] + rect[2] / 2) - (r[0] + r[2] / 2), ey = (rect[1] + rect[3] / 2) - (r[1] + r[3] / 2);
      T.addScaledVector(dx, -ex * mmPorPx).addScaledVector(dy, ey * mmPorPx);
    }
    const P = T.clone().addScaledVector(dir, d);
    return { px: P.x, py: P.y, pz: P.z, tx: T.x, ty: T.y, tz: T.z, fov };
  }
  /**
   * Mergulho: registra o afastamento das peças que ficam do lado de fora da face da peça (acima dela,
   * na direção da normal), que esconderiam a peça da câmera que desce sobre ela. Elas saem para trás
   * (contra o azimute da câmera anterior) e para cima, como mais um passo da explosão. Devolve o
   * índice do grupo para aplicaEstado(..., {g, f}), ou null.
   */
  function preparaAfastamento({ peca, de = null, recuo = 300, sobe = 150, folga = 2 }) {
    const f = faceDe(peca);
    const no = acha(peca);
    if (!f || !no || !estado) return null;
    const anc = new Set();
    for (let a = no; a; a = a.parent) anc.add(a);
    const sz = f.normal.z;
    const lista = [];
    for (const [id, c] of caixas) {
      if (anc.has(c.no)) continue;
      let dentro = false;
      for (let a = c.no.parent; a; a = a.parent) if (a === no) dentro = true;
      if (dentro) continue;
      const b = caixaPeca(id);
      const baixo = sz > 0 ? b.min.z - f.centro.z : f.centro.z - b.max.z;
      if (baixo >= folga) lista.push(c.no);
    }
    const set = new Set(lista);
    const topo = lista.filter((o) => { for (let a = o.parent; a; a = a.parent) if (set.has(a)) return false; return true; });
    if (!topo.length) return null;
    const az = new THREE.Vector3(1, -1, 0);
    if (de) az.set(de.px - de.tx, de.py - de.ty, 0);
    if (az.lengthSq() < 1e-6) az.set(0, -1, 0);
    az.normalize();
    const D = az.multiplyScalar(-recuo).addScaledVector(f.normal, sobe);
    // D em mm no mundo; o nó vive no GLB (metros, Y para cima, sob a raiz escalada): converte no registro
    return { g: estado.registraAfastamento(topo, D), pecas: topo.map((o) => o.name) };
  }
  /** Caixa da peça num nível de explosão (aplica o nível; o próximo quadro reaplica o estado do tour). */
  function caixaEm(id, nivel) {
    if (estado) { estado.explode(nivel); estado.afasta(null); placa.updateMatrixWorld(true); }
    return caixaPeca(id);
  }

  return {
    renderer, camera, controls, scene, blockout, avisos,
    qualidade: () => nivelQ, materiais: () => materiais, defineQualidade,
    temAncora: (n) => !!acha(n),
    caixaPeca, caixaNo, pontoNo, caixaEm, faceDe, poseMergulho, preparaAfastamento,
    /** Estado da acumulação (para os testes): amostras na média e o alvo. */
    acumulacao: () => ({ n: ac.n, alvo: pos ? Math.max(1, nAcumDe()) : 1 }),
    temPeca: (n) => !!estado && estado.temPeca(n),
    /** Aplica explosão (nível 0 a 8, contínuo) e destaque (fatores prévio e atual, mistura hl). */
    aplicaEstado(nivel, fPrev, fCur, hl, af = null, vit = null) {
      nivelAtual = nivel;
      destaqueAtual = `${idFat(fPrev)},${idFat(fCur)},${r5(hl)},${af ? `${af.g}:${r5(af.f)}` : ''},${(vit ?? []).map((v) => `${v.peca}:${r5(v.k)}`).join(';')}`;
      if (!estado) return;
      estado.explode(nivel);
      estado.afasta(af);
      estado.vitrine(vit);
      estado.destaque(fPrev, fCur, hl);
      placa.updateMatrixWorld(true);
    },
    fatoresDe: (partes, tags) => (estado ? estado.fatoresDe(partes, tags) : null),
    ancoraTela,
    /** Ponto em mm (referencial do storyboard) projetado para px do palco; null se atrás da câmera. */
    projeta([x, y, z]) {
      camera.updateMatrixWorld(true);
      v.set(x, y, z).project(camera);
      if (v.z > 1) return null;
      return [(v.x * 0.5 + 0.5) * STAGE_W, (-v.y * 0.5 + 0.5) * STAGE_H];
    },
    ajustaCamera,
    desenha,
  };
}

/**
 * Caixa de cada peça do assembly (nó com explode_cad) em repouso, no referencial do storyboard (mm,
 * Z para cima), só com as malhas próprias: instâncias sem explode_cad (indutores, chips de memória)
 * contam para a peça-mãe; peças filhas (o package dentro do PCB) têm caixa própria.
 */
function montaCaixas(raiz) {
  const m = new Map();
  const b = new THREE.Box3();
  raiz.traverse((o) => {
    if (!o.isMesh) return;
    let p = o;
    while (p && !p.userData?.explode_cad) p = p.parent;
    if (!p?.name) return;
    if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
    b.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld);
    let c = m.get(p.name);
    if (!c) { c = { no: p, caixa: new THREE.Box3(), p0: p.getWorldPosition(new THREE.Vector3()) }; m.set(p.name, c); }
    c.caixa.union(b);
  });
  return m;
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

/**
 * Tema na placa: troca os materiais do GLB pelos do tema (por nome de material; '*' vale para os
 * que não estão na lista) e, se o tema pedir, acrescenta arestas como filhas de cada malha. As
 * arestas são malhas também, então a explosão as leva e o destaque as esmaece junto com a peça.
 */
function aplicaTema(raiz, tc) {
  const cache = new Map();
  const matDe = (orig) => {
    const nome = orig.name ?? '';
    const m = tc.materiais?.[nome] ?? tc.materiais?.['*'];
    if (!m) return orig;
    if (!cache.has(nome)) {
      const novo = new THREE.MeshStandardMaterial({ name: nome, color: m.cor, metalness: m.metal, roughness: m.rug });
      cache.set(nome, novo);
    }
    return cache.get(nome);
  };
  const malhas = [];
  raiz.traverse((o) => { if (o.isMesh) malhas.push(o); });
  for (const o of malhas) {
    o.material = Array.isArray(o.material) ? o.material.map(matDe) : matDe(o.material);
    if (!(tc.sombra > 0)) o.castShadow = o.receiveShadow = false;
  }
  const a = tc.arestas;
  if (!a) return;
  const camadas = [];
  if (a.halo > 0) camadas.push({ w: a.halo, op: a.opHalo, aditivo: true });
  camadas.push({ w: a.nucleo, op: a.opNucleo, aditivo: false });
  const mats = camadas.map((c) => {
    const m = new LineMaterial({ color: a.cor, linewidth: c.w, transparent: true, opacity: c.op, depthWrite: false });
    if (c.aditivo) m.blending = THREE.AdditiveBlending;
    m.resolution.set(STAGE_W, STAGE_H);
    return m;
  });
  for (const o of malhas) {
    const eg = new THREE.EdgesGeometry(o.geometry, a.angulo ?? 30);
    if (!eg.attributes.position.count) continue;
    const g = new LineSegmentsGeometry().fromEdgesGeometry(eg);
    for (const m of mats) {
      const l = new LineSegments2(g, m);
      l.castShadow = l.receiveShadow = false;
      l.userData.aresta = true;
      o.add(l);
    }
  }
}

/** Sombra de contato: mancha suave sob o envelope da placa, desenhada uma vez num canvas. */
function sombraContato(medidas, c) {
  const m = (k) => medidas?.[k]?.value_mm;
  const L = m('card_envelope_length') ?? 304.8, H = m('card_envelope_height') ?? 137.16;
  const f = c.folga, px = 2;                         // 2 px por mm na textura
  const W = Math.round((L + 2 * (f + c.desfoque)) * px), Hh = Math.round((H + 2 * (f + c.desfoque)) * px);
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = Hh;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, Hh);
  ctx.filter = `blur(${c.desfoque * px * 0.5}px)`;
  ctx.fillStyle = '#fff';                            // alphaMap: branco = sombra cheia
  const x0 = c.desfoque * px, y0 = c.desfoque * px;
  ctx.fillRect(x0, y0, W - 2 * x0, Hh - 2 * y0);
  ctx.filter = 'none';
  const tex = new THREE.CanvasTexture(cv);
  const mat = new THREE.MeshBasicMaterial({ color: 0x000000, alphaMap: tex, transparent: true, opacity: c.opacidade, depthWrite: false });
  const plano = new THREE.Mesh(new THREE.PlaneGeometry(W / px, Hh / px), mat);
  plano.position.set(L / 2, H / 2, -1.9);
  plano.renderOrder = -1;
  return plano;
}

import COREO from './desmontagem.json';

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
const F = COREO.fases;
const expoOut = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x));
const janela = (k, [a, b]) => Math.min(1, Math.max(0, (k - a) / (b - a)));
/** Progresso local de uma peça no seu estágio (0 a 1), com o atraso do escalonamento. */
function local(nivel, n) {
  const t = Math.min(1, Math.max(0, nivel - (n.estagio - 1)));
  if (!n.atraso) return t;
  return Math.min(1, Math.max(0, (t - n.atraso) / (1 - n.atraso)));
}
/** Fração do deslocamento da peça: descola alguns mm, depois viaja com expo.out. */
function curvaPeca(k, dist) {
  const d = Math.min(0.5, (COREO.descola_mm ?? 0) / dist);
  return d * suave(janela(k, F.descola)) + (1 - d) * expoOut(janela(k, F.viagem));
}
const _q = new THREE.Quaternion();
const _v = new THREE.Vector3();
/** Parafuso: gira e recua no próprio eixo; na viagem da peça, segue à frente dela. */
function poeParafuso(f, k) {
  const a = suave(janela(k, F.fixadores));
  const ang = a * (COREO.fixadores.voltas ?? 0) * 2 * Math.PI;
  const mm = a * COREO.fixadores.recuo_mm + expoOut(janela(k, F.viagem)) * COREO.fixadores.alem_mm;
  _q.setFromAxisAngle(f.eixo, ang);
  f.o.quaternion.copy(_q).multiply(f.q0);
  // gira em torno do centro do parafuso: p = q (base - centro) + centro
  _v.copy(f.base).sub(f.centro).applyQuaternion(_q).add(f.centro);
  f.o.position.copy(_v).addScaledVector(f.eixo, mm / 1000);
}

function criaEstado3d(raiz, realista = null) {
  const nos = [];
  const pecas = new Map();       // nome -> true
  const malhas = [];
  const parafusos = [];          // fixadores de cada estágio (coreografia: giram e recuam)
  const gl = ([dx, dy, dz], mm) => new THREE.Vector3(dx * mm / 1000, dz * mm / 1000, -dy * mm / 1000);  // CAD -> glTF
  const atrasoDe = new Map();
  for (const [k, lista] of Object.entries(COREO.escalona ?? {})) {
    if (!Array.isArray(lista)) continue;
    lista.forEach((id, i) => atrasoDe.set(id, i * (COREO.escalona.passo ?? 0.1)));
  }
  raiz.traverse((o) => {
    const u = o.userData ?? {};
    if (o.name) pecas.set(o.name, o);
    const est = /^E([1-8])$/.exec(u.stage ?? '');
    const ex = u.explode_cad;
    if (est && ex && ex.distance > 0) {
      nos.push({ o, base: o.position.clone(), estagio: Number(est[1]), off: gl(ex.dir, ex.distance), dist: ex.distance, atraso: atrasoDe.get(o.name) ?? 0, p: -1 });
    }
    // fixadores: nó fasteners.eN_* (sem deslocamento próprio) com uma malha por parafuso
    if (est && ex && /^fasteners\.e\d/.test(o.name ?? '')) {
      const eixo = gl(ex.dir, 1000).normalize();
      for (const m of o.children) {
        if (!m.isMesh && !m.children.some((c) => c.isMesh)) continue;
        const bb = new THREE.Box3().setFromObject(m);   // nós com transformação identidade no GLB
        const centro = bb.getCenter(new THREE.Vector3());
        parafusos.push({ o: m, base: m.position.clone(), q0: m.quaternion.clone(), centro, eixo, estagio: Number(est[1]), atraso: atrasoDe.get(o.name) ?? 0, k: -1 });
      }
    }
    if (o.isMesh) {
      const nomes = new Set();
      for (let a = o; a; a = a.parent) {
        if (a.name) nomes.add(a.name);
        if (a.userData?.instance_of) nomes.add(a.userData.instance_of);
        if (a.userData?.group) nomes.add(`tag:${a.userData.group}`);
      }
      // clone() não leva o onBeforeCompile: no modo realista o trecho do destaque é reinstalado
      const mats = (Array.isArray(o.material) ? o.material : [o.material]).map((m) => (realista ? preparaMaterial(m.clone(), realista.corRealce) : m.clone()));
      o.material = Array.isArray(o.material) ? mats : mats[0];
      malhas.push({ o, nomes, mats, base: mats.map((m) => ({ op: m.opacity, tr: m.transparent, dw: m.depthWrite })), f: 1 });
    }
  });

  // Afastamento extra (mergulho): nós que saem do caminho da câmera, além da explosão.
  // extra: nó -> { base (posição sem explosão), local (deslocamento total no referencial do pai), f }
  const porNo = new Map(nos.map((n) => [n.o, n]));
  const extra = new Map();
  const comp = new Map();        // deslocamento extra da coreografia (abertura da carcaça), no referencial do pai
  const base0 = new Map();
  const poe = (o) => {
    const n = porNo.get(o), x = extra.get(o);
    if (!n && !x && !base0.has(o)) base0.set(o, o.position.clone());
    if (n) o.position.copy(n.base).addScaledVector(n.off, n.p);
    else if (x) o.position.copy(x.base);
    else o.position.copy(base0.get(o));
    if (x && x.f) o.position.addScaledVector(x.local, x.f);
    const c = comp.get(o);
    if (c) o.position.add(c);
  };
  // E8: a carcaça sai sem levar o cooler (os filhos que ficam recebem o deslocamento oposto)
  const ac = COREO.abre_carcaca;
  const noCarcaca = ac && pecas.get(ac.no);
  const carcaca = noCarcaca ? {
    o: noCarcaca, estagio: ac.estagio, janela: ac.janela, k: -1,
    D: gl(ac.dir, ac.distancia),
    ficam: noCarcaca.children.filter((c) => c.name && !c.name.startsWith('anchor.') && !(ac.leva ?? []).includes(c.name)),
  } : null;
  if (carcaca) for (const c of [carcaca.o, ...carcaca.ficam]) if (!porNo.has(c) && !base0.has(c)) base0.set(c, c.position.clone());
  const grupos = [];
  const vitrines = new Map();    // nome -> { o, q0 }
  return {
    temPeca: (n) => pecas.has(n),
    explode(nivel) {
      for (const n of nos) {
        const p = curvaPeca(local(nivel, n), n.dist);
        if (p === n.p) continue;
        n.p = p;
        poe(n.o);
      }
      for (const f of parafusos) {
        const k = local(nivel, f);
        if (k === f.k) continue;
        f.k = k;
        poeParafuso(f, k);
      }
      if (carcaca) {
        const [a, b] = carcaca.janela;
        const k = suave(Math.min(1, Math.max(0, (nivel - (carcaca.estagio - 1) - a) / (b - a))));
        if (k !== carcaca.k) {
          carcaca.k = k;
          comp.set(carcaca.o, carcaca.D.clone().multiplyScalar(k));
          for (const c of carcaca.ficam) comp.set(c, carcaca.D.clone().multiplyScalar(-k));
          poe(carcaca.o);
          for (const c of carcaca.ficam) poe(c);
        }
      }
    },
    /** Registra um grupo de nós a afastar por D (mm, mundo); devolve o índice do grupo. */
    registraAfastamento(lista, D) {
      const m3 = new THREE.Matrix3();
      const g = [];
      for (const o of lista) {
        if (extra.has(o)) continue;
        m3.setFromMatrix4(new THREE.Matrix4().copy(o.parent.matrixWorld).invert());
        extra.set(o, { base: porNo.get(o)?.base ?? o.position.clone(), local: D.clone().applyMatrix3(m3), f: 0 });
        g.push(o);
      }
      grupos.push(g);
      return grupos.length - 1;
    },
    /**
     * Vitrine (illustrative): peças tiradas da posição da placa e apresentadas ao público.
     * lista = [{ peca, k (0 a 1), pos ([x, y, z] mm, referencial do storyboard), giro ([x, y, z] graus, eixos do mundo) }].
     * Com k = 0 a peça volta ao lugar da explosão. O centro da caixa da peça vai até pos, girando em torno dele.
     */
    vitrine(lista) {
      const pedidas = new Map((lista ?? []).filter((v) => v.k > 0 && pecas.has(v.peca)).map((v) => [v.peca, v]));
      for (const [nome, st] of vitrines) {
        if (pedidas.has(nome)) continue;
        st.o.quaternion.copy(st.q0); poe(st.o); vitrines.delete(nome);
      }
      for (const [nome, v] of pedidas) {
        const o = pecas.get(nome);
        let st = vitrines.get(nome);
        if (!st) { st = { o, q0: o.quaternion.clone() }; vitrines.set(nome, st); }
        o.quaternion.copy(st.q0); poe(o);
        o.parent.updateMatrixWorld(true); o.updateMatrixWorld(true);
        const Cp = o.parent.worldToLocal(new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3()));
        const Tp = o.parent.worldToLocal(new THREE.Vector3(...v.pos));
        const g = (v.giro ?? [0, 0, 0]).map((x) => THREE.MathUtils.degToRad(x));
        const qw = new THREE.Quaternion().setFromEuler(new THREE.Euler(g[0], g[1], g[2], 'XYZ'));
        const qpw = o.parent.getWorldQuaternion(new THREE.Quaternion());
        const qp = qpw.clone().invert().multiply(qw).multiply(qpw);
        const s = suave(Math.min(1, Math.max(0, v.k)));
        const qs = new THREE.Quaternion().slerp(qp, s);
        const novoC = Cp.clone().lerp(Tp, s);
        o.position.sub(Cp).applyQuaternion(qs).add(novoC);
        o.quaternion.copy(qs).multiply(st.q0);
      }
    },
    /** Fração do afastamento de cada grupo (af = {g, f}; null = nenhum afastado). */
    afasta(af) {
      grupos.forEach((g, i) => {
        const f = af && af.g === i ? af.f : 0;
        for (const o of g) { const x = extra.get(o); if (x.f !== f) { x.f = f; poe(o); } }
      });
    },
    /** Fatores de opacidade por malha para um conjunto de peças (ids) e de tags; null = nada esmaece. */
    fatoresDe(partes, tags) {
      const sel = [...(partes ?? []), ...(tags ?? []).map((t) => `tag:${t}`)];
      const ok = sel.filter((n) => pecas.has(n) || n.startsWith('tag:'));
      if (!ok.length) return null;
      const f = malhas.map((m) => (ok.some((n) => m.nomes.has(n)) ? 1 : DIM));
      f.sel = f.some((x) => x !== 1);     // recorte de luz só quando algo de fato escurece
      return f;
    },
    destaque(fPrev, fCur, hl) {
      malhas.forEach((m, i) => {
        const a = fPrev ? fPrev[i] : 1, b = fCur ? fCur[i] : 1;
        const f = a + (b - a) * hl;
        if (realista) {
          // realista: nada fica translúcido; o resto escurece e perde a cor, a peça destacada ganha
          // um recorte de luz (só quando há seleção: fatores marcados com sel)
          const ra = fPrev?.sel && fPrev[i] === 1 ? 1 : 0, rb = fCur?.sel && fCur[i] === 1 ? 1 : 0;
          const realce = ra + (rb - ra) * hl;
          const apaga = (1 - f) / (1 - DIM) * realista.apaga;
          if (f === m.f && realce === m.r) return;
          m.f = f; m.r = realce;
          for (const mt of m.mats) { mt.userData.ld.apaga.value = apaga; mt.userData.ld.realce.value = realce; }
          return;
        }
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
