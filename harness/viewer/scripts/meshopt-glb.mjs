// Comprime a geometria de um GLB com EXT_meshopt_compression (contrato do passo do Blender, item 7).
// Uso: node scripts/meshopt-glb.mjs entrada.glb saida.glb
//
// Sem perda: atributos no modo ATTRIBUTES sem filtro (os bytes voltam iguais) e índices no modo
// TRIANGLES (os mesmos triângulos; o codec pode girar a ordem dos três vértices, sem mudar a
// orientação). Nada é reordenado nem quantizado: posições, normais, UV e tangentes saem idênticas.
// Imagens e JSON (nós, extras, materiais) ficam como estão. O buffer 1 é o de reserva sem dados
// (fallback) que a extensão pede. Confere decodificando cada bufferView com o decodificador do
// próprio meshoptimizer antes de gravar. Determinístico.
import fs from 'node:fs';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';

const [entrada, saida] = process.argv.slice(2);
if (!entrada || !saida) { console.error('uso: node scripts/meshopt-glb.mjs entrada.glb saida.glb'); process.exit(2); }
await MeshoptEncoder.ready;
await MeshoptDecoder.ready;

const b = fs.readFileSync(entrada);
const L = b.readUInt32LE(12);
const j = JSON.parse(b.subarray(20, 20 + L).toString('utf8'));
const bin = b.subarray(28 + L, 28 + L + b.readUInt32LE(20 + L));
if ((j.extensionsUsed ?? []).includes('EXT_meshopt_compression')) { console.error('meshopt-glb: o GLB já está comprimido'); process.exit(1); }

const NC = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 };
const CS = { 5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4 };
// um accessor por bufferView de geometria (é o que integrate.py e blender_pass.py escrevem)
const porView = new Map();
for (const a of j.accessors) {
  if (porView.has(a.bufferView)) porView.set(a.bufferView, null);
  else porView.set(a.bufferView, a);
}

const partes = [];
let off = 0, reserva = 0, antes = 0, depois = 0;
const poe = (dados) => {
  const pad = (4 - (off % 4)) % 4;
  if (pad) { partes.push(Buffer.alloc(pad)); off += pad; }
  partes.push(Buffer.from(dados.buffer, dados.byteOffset, dados.byteLength));
  const o = off;
  off += dados.byteLength;
  return o;
};
const iguaisTriangulos = (x, y, n) => {
  for (let t = 0; t < n; t += 3) {
    const a = [x[t], x[t + 1], x[t + 2]], c = [y[t], y[t + 1], y[t + 2]];
    if (![0, 1, 2].some((r) => a[0] === c[r] && a[1] === c[(r + 1) % 3] && a[2] === c[(r + 2) % 3])) return false;
  }
  return true;
};
const views = j.bufferViews.map((v, i) => {
  const src = new Uint8Array(bin.buffer, bin.byteOffset + (v.byteOffset ?? 0), v.byteLength);
  const a = porView.get(i);
  const geo = a && (v.target === 34962 || v.target === 34963) && !v.byteStride;
  if (!geo) return { ...v, buffer: 0, byteOffset: poe(src) };
  const n = NC[a.type], cs = CS[a.componentType];
  const modo = v.target === 34963 ? 'TRIANGLES' : 'ATTRIBUTES';
  const tam = modo === 'TRIANGLES' ? cs : n * cs;
  if (modo === 'ATTRIBUTES' && tam % 4) return { ...v, buffer: 0, byteOffset: poe(src) };
  const cod = MeshoptEncoder.encodeGltfBuffer(src, a.count, tam, modo);
  const volta = new Uint8Array(a.count * tam);
  MeshoptDecoder.decodeGltfBuffer(volta, a.count, tam, cod, modo);
  const ok = modo === 'ATTRIBUTES'
    ? Buffer.compare(Buffer.from(volta), Buffer.from(src)) === 0
    : (() => { const T = cs === 4 ? Uint32Array : Uint16Array; return iguaisTriangulos(new T(src.buffer.slice(src.byteOffset, src.byteOffset + src.byteLength)), new T(volta.buffer), a.count); })();
  if (!ok) throw new Error(`meshopt-glb: bufferView ${i} não volta igual depois de decodificado`);
  antes += src.byteLength; depois += cod.byteLength;
  const o = poe(cod);
  const rv = reserva;
  reserva += Math.ceil(src.byteLength / 4) * 4;
  return {
    buffer: 1, byteOffset: rv, byteLength: src.byteLength, byteStride: modo === 'ATTRIBUTES' ? tam : undefined, target: v.target,
    extensions: { EXT_meshopt_compression: { buffer: 0, byteOffset: o, byteLength: cod.byteLength, byteStride: tam, count: a.count, mode: modo } },
  };
});
// índices de 16 ou 32 bits: o byteStride do bufferView de índices não pode existir
for (const v of views) if (v.byteStride === undefined) delete v.byteStride;

const corpo = Buffer.concat(partes);
const binOut = Buffer.concat([corpo, Buffer.alloc((4 - (corpo.length % 4)) % 4)]);
j.bufferViews = views;
j.buffers = [{ byteLength: binOut.length }, { byteLength: reserva, extensions: { EXT_meshopt_compression: { fallback: true } } }];
j.extensionsUsed = [...new Set([...(j.extensionsUsed ?? []), 'EXT_meshopt_compression'])];
j.extensionsRequired = [...new Set([...(j.extensionsRequired ?? []), 'EXT_meshopt_compression'])];
let js = Buffer.from(JSON.stringify(j), 'utf8');
js = Buffer.concat([js, Buffer.alloc((4 - (js.length % 4)) % 4, 0x20)]);
const cab = Buffer.alloc(12);
cab.write('glTF', 0); cab.writeUInt32LE(2, 4); cab.writeUInt32LE(12 + 8 + js.length + 8 + binOut.length, 8);
const pj = Buffer.alloc(8); pj.writeUInt32LE(js.length, 0); pj.write('JSON', 4);
const pb = Buffer.alloc(8); pb.writeUInt32LE(binOut.length, 0); pb.write('BIN\0', 4);
fs.writeFileSync(saida, Buffer.concat([cab, pj, js, pb, binOut]));
console.log(`meshopt-glb: geometria ${(antes / 2 ** 20).toFixed(2)} MB -> ${(depois / 2 ** 20).toFixed(2)} MB; arquivo ${(b.length / 2 ** 20).toFixed(2)} MB -> ${((12 + 16 + js.length + binOut.length) / 2 ** 20).toFixed(2)} MB`);
