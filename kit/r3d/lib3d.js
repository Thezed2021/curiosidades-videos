// Biblioteca 3D (three.js) para os vídeos "Você é um..." do canal Curiosidades do Mundo.
// Estilo: cartoon 3D (MeshToonMaterial), olhos grandes e expressivos, cores vivas.
// Tudo é feito de primitivas (esfera, cone, cilindro, cápsula, torus) — nada de modelos externos.
import * as THREE from './three.module.min.js';
export { THREE };

// ---------------------------------------------------------------- utilidades
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const ease = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
export const easeOut = (x) => { x = clamp(x); return 1 - Math.pow(1 - x, 3); };
export const easeBack = (x) => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
export const lerp = (a, b, k) => a + (b - a) * k;
export const fade = (t, start, dur = 0.4) => ease((t - start) / dur);

let _grad = null;
function toonGrad() {
  if (_grad) return _grad;
  const data = new Uint8Array([70, 140, 210, 255]);
  _grad = new THREE.DataTexture(data, 4, 1, THREE.RedFormat);
  _grad.minFilter = _grad.magFilter = THREE.NearestFilter; _grad.needsUpdate = true;
  return _grad;
}
export function mat(color, opts = {}) {
  return new THREE.MeshToonMaterial({ color, gradientMap: toonGrad(), ...opts });
}
export function mesh(geo, color, opts) { const m = new THREE.Mesh(geo, mat(color, opts)); m.castShadow = true; m.receiveShadow = true; return m; }
export const sphere = (r, color, seg = 32) => mesh(new THREE.SphereGeometry(r, seg, seg / 2), color);
export const cone = (r, h, color, seg = 24) => mesh(new THREE.ConeGeometry(r, h, seg), color);
export const cyl = (rt, rb, h, color, seg = 24) => mesh(new THREE.CylinderGeometry(rt, rb, h, seg), color);
export const capsule = (r, len, color) => mesh(new THREE.CapsuleGeometry(r, len, 8, 20), color);
export const box = (w, h, d, color) => mesh(new THREE.BoxGeometry(w, h, d), color);
export const torus = (r, tube, color, arc = Math.PI * 2) => mesh(new THREE.TorusGeometry(r, tube, 12, 40, arc), color);

// ---------------------------------------------------------------- palco
// stage({ top, bottom, ground: 'agua'|'grama'|'areia'|'neve'|'espaco'|'lab'|null, fogColor })
export function stage(scene, camera, renderer, o = {}) {
  const top = new THREE.Color(o.top ?? '#4fb3ff'), bottom = new THREE.Color(o.bottom ?? '#0a3d6b');
  const c = document.createElement('canvas'); c.width = 2; c.height = 512;
  const g = c.getContext('2d'); const gr = g.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, '#' + top.getHexString()); gr.addColorStop(1, '#' + bottom.getHexString());
  g.fillStyle = gr; g.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; scene.background = tex;
  if (o.fogColor) scene.fog = new THREE.Fog(o.fogColor, o.fogNear ?? 8, o.fogFar ?? 30);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 2.2); sun.position.set(4, 8, 6); sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 });
  scene.add(sun);
  const groups = { sun };
  const gcol = { agua: '#d9c38c', grama: '#5cbf4a', areia: '#e8cf8a', neve: '#f2f6ff', lab: '#cfd6e0', espaco: null }[o.ground ?? 'grama'];
  if (gcol) {
    const ground = mesh(new THREE.CircleGeometry(30, 64), gcol); ground.rotation.x = -Math.PI / 2; ground.position.y = o.groundY ?? -1.6;
    scene.add(ground); groups.ground = ground;
  }
  if (o.ground === 'espaco') {
    const pts = new THREE.BufferGeometry(); const arr = [];
    for (let i = 0; i < 600; i++) arr.push((Math.random() - .5) * 60, (Math.random() - .5) * 60, -10 - Math.random() * 30);
    pts.setAttribute('position', new THREE.Float32BufferAttribute(arr, 3));
    scene.add(new THREE.Points(pts, new THREE.PointsMaterial({ color: 0xffffff, size: 0.08 })));
  }
  camera.position.set(0, 0.6, 7); camera.lookAt(0, 0, 0);
  return groups;
}

// bolhas subindo (debaixo d'água) — chame bubbles.update(gt)
export function bubbles(scene, n = 40, area = 8) {
  const g = new THREE.Group(); const list = [];
  for (let i = 0; i < n; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.04 + Math.random() * 0.08, 12, 8),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 }));
    b.userData = { x: (Math.random() - .5) * area, z: -Math.random() * 6, s: 0.5 + Math.random(), o: Math.random() * 10 };
    g.add(b); list.push(b);
  }
  scene.add(g);
  g.update = (gt) => list.forEach(b => { const u = b.userData; b.position.set(u.x + Math.sin(gt * 2 + u.o) * .1, ((gt * u.s + u.o) % 8) - 3, u.z); });
  return g;
}

// ---------------------------------------------------------------- olhos e boca (expressões)
export function eye(r = 0.22) {
  const g = new THREE.Group();
  const white = sphere(r, '#ffffff'); g.add(white);
  const iris = sphere(r * 0.55, '#1b1b22'); iris.position.z = r * 0.62; g.add(iris);
  const shine = new THREE.Mesh(new THREE.SphereGeometry(r * 0.16, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  shine.position.set(r * 0.2, r * 0.2, r * 0.98); g.add(shine);
  const lid = mesh(new THREE.SphereGeometry(r * 1.04, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), '#000'); lid.visible = false; g.add(lid);
  g.userData = { iris, shine, lid, r };
  // look(x,y) -1..1 ; blink(k) 0..1 ; mood: 'neutro'|'bravo'|'medo'|'feliz'
  g.look = (x = 0, y = 0) => { iris.position.set(x * r * .35, y * r * .35, r * 0.62); shine.position.set(r * .2 + x * r * .3, r * .2 + y * r * .3, r * .98); };
  g.blink = (k) => { g.scale.y = 1 - 0.9 * clamp(k); };
  return g;
}
export function brow(len = 0.3, color = '#222') { const b = capsule(0.035, len, color); b.rotation.z = Math.PI / 2; return b; }
export function mouth(w = 0.4, color = '#5a1020') {
  // boca: meia-torus (sorriso) que vira para baixo com mood
  const m = torus(w / 2, 0.035, color, Math.PI); m.rotation.z = Math.PI; return m;
}

// ---------------------------------------------------------------- criaturas genéricas
// peixe cartoon: makeFish({ body:'#8a9bb0', belly:'#ff5533', teeth:true, size:1 })
export function makeFish(o = {}) {
  const s = o.size ?? 1, g = new THREE.Group();
  const body = sphere(1, o.body ?? '#8a9bb0'); body.scale.set(1.25 * s, 0.95 * s, 0.7 * s); g.add(body);
  const belly = sphere(1, o.belly ?? '#ff5a36'); belly.scale.set(1.05 * s, 0.55 * s, 0.6 * s); belly.position.set(0.1 * s, -0.42 * s, 0.05 * s); g.add(belly);
  const tail = new THREE.Group(); tail.position.x = -1.2 * s;
  const tf = cone(0.55 * s, 0.9 * s, o.fin ?? o.body ?? '#7a8aa0', 4); tf.rotation.z = Math.PI / 2; tf.scale.z = 0.25; tf.position.x = -0.35 * s; tail.add(tf); g.add(tail);
  const dorsal = cone(0.35 * s, 0.7 * s, o.fin ?? '#6c7a90', 4); dorsal.position.set(-0.1 * s, 0.95 * s, 0); dorsal.scale.z = 0.2; dorsal.rotation.z = -0.4; g.add(dorsal);
  const eyeL = eye(0.26 * s); eyeL.position.set(0.75 * s, 0.25 * s, 0.45 * s); g.add(eyeL);
  const browL = brow(0.32 * s); browL.position.set(0.75 * s, 0.55 * s, 0.55 * s); g.add(browL);
  const jaw = new THREE.Group(); jaw.position.set(1.05 * s, -0.2 * s, 0); g.add(jaw);
  // boca: faixa escura na frente + dentes triangulares em cima (fixos) e embaixo (na mandíbula)
  const mouthLine = capsule(0.07 * s, 0.75 * s, '#3a0d14'); mouthLine.rotation.x = Math.PI / 2; mouthLine.position.set(1.12 * s, -0.22 * s, 0); g.add(mouthLine);
  if (o.teeth) {
    for (let i = 0; i < 7; i++) {
      const z = (-0.39 + i * 0.13) * s, x = 1.17 * s - 0.55 * z * z / s;
      const up = cone(0.075 * s, 0.24 * s, '#ffffff', 4); up.rotation.x = Math.PI; up.position.set(x, -0.15 * s, z); g.add(up);
      const lo = cone(0.07 * s, 0.22 * s, '#fffaf0', 4); lo.position.set(x - 1.05 * s, -0.1 * s, z); jaw.add(lo);
    }
  }
  g.userData = { body, tail, eyes: [eyeL], brows: [browL], jaw, s };
  g.swim = (t, speed = 1) => { tail.rotation.y = Math.sin(t * 9 * speed) * 0.5; g.rotation.z = Math.sin(t * 2) * 0.04; };
  g.chomp = (k) => { jaw.rotation.z = -0.5 * Math.abs(Math.sin(k * Math.PI)); };
  g.mood = (m) => { browL.rotation.z = Math.PI / 2 + ({ bravo: -0.5, medo: 0.5, feliz: 0.15 }[m] ?? 0); browL.position.y = (m === 'medo' ? 0.62 : 0.55) * s; };
  return g;
}

// bicho de 4 patas genérico: makeQuadruped({ color:'#c98b4a', ears:'pontuda'|'redonda'|'caida', tail:true, size:1 })
export function makeQuadruped(o = {}) {
  const s = o.size ?? 1, col = o.color ?? '#c98b4a', g = new THREE.Group();
  const body = capsule(0.55 * s, 1.1 * s, col); body.rotation.z = Math.PI / 2; g.add(body);
  const legs = [];
  for (const [x, z] of [[0.6, .3], [0.6, -.3], [-0.6, .3], [-0.6, -.3]]) {
    const leg = new THREE.Group(); leg.position.set(x * s, -0.3 * s, z * s);
    const l = capsule(0.13 * s, 0.5 * s, o.legs ?? col); l.position.y = -0.4 * s; leg.add(l); g.add(leg); legs.push(leg);
  }
  const head = new THREE.Group(); head.position.set(1.15 * s, 0.45 * s, 0); g.add(head);
  head.add(sphere(0.48 * s, col));
  const snout = sphere(0.25 * s, o.snout ?? '#f1d9b5'); snout.position.set(0.38 * s, -0.12 * s, 0); snout.scale.set(1.2, .8, 1); head.add(snout);
  const nose = sphere(0.08 * s, '#222'); nose.position.set(0.66 * s, -0.05 * s, 0); head.add(nose);
  const eyes = [];
  for (const z of [0.2, -0.2]) { const e = eye(0.13 * s); e.position.set(0.32 * s, 0.12 * s, z * s); e.rotation.y = Math.PI / 2 * 0.7 * Math.sign(z); head.add(e); eyes.push(e); }
  for (const z of [0.25, -0.25]) {
    const ear = o.ears === 'redonda' ? sphere(0.15 * s, col) : cone(0.14 * s, 0.35 * s, col);
    ear.position.set(-0.05 * s, 0.45 * s, z * s); if (o.ears === 'caida') { ear.rotation.x = Math.sign(z) * 2.4; ear.position.y = 0.25 * s; } head.add(ear);
  }
  let tail = null;
  if (o.tail !== false) { tail = new THREE.Group(); tail.position.set(-1.05 * s, 0.2 * s, 0); const tt = capsule(0.07 * s, 0.6 * s, col); tt.position.y = 0.3 * s; tail.add(tt); tail.rotation.z = 0.6; g.add(tail); }
  g.userData = { body, legs, head, eyes, tail, s };
  g.walk = (t, speed = 1) => { legs.forEach((l, i) => l.rotation.z = Math.sin(t * 8 * speed + (i % 2 ? Math.PI : 0) + (i > 1 ? Math.PI / 2 : 0)) * 0.5); g.position.y = Math.abs(Math.sin(t * 8 * speed)) * 0.06 * s; if (tail) tail.rotation.x = Math.sin(t * 6) * 0.4; };
  g.idle = (t) => { head.rotation.z = Math.sin(t * 1.5) * 0.08; if (tail) tail.rotation.x = Math.sin(t * 3) * 0.3; };
  return g;
}

// ave genérica: makeBird({ color:'#ff8fb8', beak:'#222', legs:'#e07aa0', size:1 })
export function makeBird(o = {}) {
  const s = o.size ?? 1, col = o.color ?? '#ffcc33', g = new THREE.Group();
  const body = sphere(0.7 * s, col); body.scale.set(1.2, 0.9, 0.85); g.add(body);
  const head = new THREE.Group(); head.position.set(0.6 * s, 0.75 * s, 0); g.add(head);
  head.add(sphere(0.38 * s, col));
  const beak = cone(0.12 * s, 0.4 * s, o.beak ?? '#ff9922'); beak.rotation.z = -Math.PI / 2; beak.position.x = 0.48 * s; head.add(beak);
  const eyes = [];
  for (const z of [0.18, -0.18]) { const e = eye(0.11 * s); e.position.set(0.2 * s, 0.1 * s, z * s); e.rotation.y = 0.7 * Math.sign(z); head.add(e); eyes.push(e); }
  const wings = [];
  for (const z of [0.6, -0.6]) { const w = new THREE.Group(); w.position.set(0, 0.2 * s, z * s); const ws = sphere(0.45 * s, o.wing ?? col); ws.scale.set(1.2, .25, .7); ws.position.x = -0.2 * s; w.add(ws); g.add(w); wings.push(w); }
  for (const z of [0.2, -0.2]) { const l = cyl(0.04 * s, 0.04 * s, 0.9 * s, o.legs ?? '#ff9922'); l.position.set(0, -0.95 * s, z * s); g.add(l); }
  g.userData = { body, head, eyes, wings, s };
  g.flap = (t, speed = 1) => wings.forEach((w, i) => w.rotation.x = (i ? -1 : 1) * Math.sin(t * 12 * speed) * 0.8);
  return g;
}

// "bolinha" com cara: serve para célula, gota, planeta, vírus, grão de areia, neurônio...
export function makeBlob(o = {}) {
  const s = o.size ?? 1, g = new THREE.Group();
  const body = sphere(1 * s, o.color ?? '#7dd3fc'); if (o.squash) body.scale.set(1, o.squash, 1); g.add(body);
  const eyes = [];
  for (const x of [-0.32, 0.32]) { const e = eye(0.24 * s); e.position.set(x * s, 0.2 * s, 0.82 * s); g.add(e); eyes.push(e); }
  const m = mouth(0.45 * s); m.position.set(0, -0.25 * s, 0.92 * s); g.add(m);
  if (o.spikes) for (let i = 0; i < o.spikes; i++) {
    const a = i / o.spikes * Math.PI * 2, b = (i % 3 - 1) * 0.6; const sp = cone(0.12 * s, 0.45 * s, o.spikeColor ?? o.color ?? '#f87171');
    const v = new THREE.Vector3(Math.cos(a) * Math.cos(b), Math.sin(b), Math.sin(a) * Math.cos(b)); sp.position.copy(v.clone().multiplyScalar(1.05 * s));
    sp.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), v); g.add(sp);
  }
  g.userData = { body, eyes, mouth: m, s };
  g.bounce = (t, amp = 0.08) => { const k = Math.abs(Math.sin(t * 4)); g.position.y = k * amp * 3 * s; body.scale.y = (o.squash ?? 1) * (1 - 0.06 * (1 - k)); };
  g.smile = (k) => { m.rotation.z = k >= 0 ? Math.PI : 0; m.scale.y = Math.abs(k) || 0.2; };
  return g;
}

// texto 3D simples não é usado: textos ficam na camada 2D do engine (legendas, chips).
