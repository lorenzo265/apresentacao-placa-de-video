#!/usr/bin/env python3
"""Gera src/ambiente-hdr.js (ambiente de estúdio escuro, embutido em base64) a partir de um HDR da Poly Haven.

Fonte usada: "Studio Small 08", de Sergej Majboroda, Poly Haven, licença CC0
(https://polyhaven.com/a/studio_small_08; arquivo 1k: studio_small_08_1k.hdr).

Uso (uma vez; o resultado é versionado e o viewer não baixa nada em tempo de execução):
    curl -o /caminho/studio_small_08_1k.hdr https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_08_1k.hdr
    python3 -I harness/viewer/scripts/ambiente-hdr.py /caminho/studio_small_08_1k.hdr harness/viewer/src/ambiente-hdr.js

Processamento: reduz de 1024 x 512 para 256 x 128 (média por área, em luz linear) e transforma o
estúdio claro num estúdio escuro: o que tem luminância acima do limiar (softboxes, octaboxes) fica
inteiro, com rampa suave; o resto (ciclorama branco, paredes) cai para 6 %. No fundo quase preto do
tema Keynote, um ciclorama claro acenderia todo metal da placa e tiraria o contraste da foto de produto.
"""
import base64
import re
import sys

import numpy as np

LUM = np.array([0.2126, 0.7152, 0.0722])


def le_hdr(caminho):
    b = open(caminho, 'rb').read()
    i = 0
    while True:
        j = b.index(b'\n', i)
        linha = b[i:j].decode('latin1')
        i = j + 1
        m = re.match(r'-Y (\d+) \+X (\d+)', linha)
        if m:
            H, W = int(m.group(1)), int(m.group(2))
            break
    dados = np.zeros((H, W, 4), np.uint8)
    p = i
    for y in range(H):
        if b[p] == 2 and b[p + 1] == 2:          # RLE novo
            p += 4
            for c in range(4):
                x = 0
                while x < W:
                    n = b[p]; p += 1
                    if n > 128:
                        n -= 128
                        dados[y, x:x + n, c] = b[p]; p += 1
                    else:
                        dados[y, x:x + n, c] = np.frombuffer(b[p:p + n], np.uint8); p += n
                    x += n
        else:
            dados[y] = np.frombuffer(b[p:p + 4 * W], np.uint8).reshape(W, 4); p += 4 * W
    e = dados[..., 3].astype(np.int32)
    f = np.where(e > 0, np.ldexp(1.0, e - 136), 0.0)
    return dados[..., :3].astype(np.float64) * f[..., None]


def hdr_bytes(img):
    H, W, _ = img.shape
    m = img.max(axis=2)
    man, ex = np.frexp(m)
    ok = m > 1e-32
    esc = np.where(ok, man * 256.0 / np.where(ok, m, 1), 0)
    rgb = np.clip(np.floor(img * esc[..., None]), 0, 255).astype(np.uint8)
    e = np.where(ok, ex + 128, 0).astype(np.uint8)
    cab = b'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y %d +X %d\n' % (H, W)
    return cab + np.concatenate([rgb, e[..., None]], axis=2).tobytes()


def reduz(img, W):
    H0, W0, _ = img.shape
    k = W0 // W
    return img[:H0 // k * k, :W0 // k * k].reshape(H0 // k, k, W0 // k, k, 3).mean(axis=(1, 3))


def main(src, dst, W=256, limiar=2.0, resto=0.06):
    img = reduz(le_hdr(src), W)
    lum = img @ LUM
    t = np.clip((lum - limiar * 0.5) / (limiar * 0.5), 0, 1)
    k = resto + (1 - resto) * t * t * (3 - 2 * t)
    out = img * k[..., None]
    b64 = base64.b64encode(hdr_bytes(out)).decode('ascii')
    with open(dst, 'w') as f:
        f.write('// Gerado por scripts/ambiente-hdr.py (não editar). Ambiente: "Studio Small 08", Sergej Majboroda,\n')
        f.write('// Poly Haven, CC0 (https://polyhaven.com/a/studio_small_08), reduzido a %d x %d e escurecido fora das luzes.\n' % (out.shape[1], out.shape[0]))
        f.write('export default "%s";\n' % b64)
    print(f'{dst}: {out.shape[1]} x {out.shape[0]}, {len(b64) / 1024:.0f} kB em base64, lum média {(out @ LUM).mean():.3f}, máx {(out @ LUM).max():.1f}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
