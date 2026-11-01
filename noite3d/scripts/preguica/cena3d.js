// "Você é uma preguiça!" — cenas 3D (three.js). Cada cena = um nome de "scene" dos SEGS.
let O = {};

// ------------------------------------------------------------ preguiça-de-três-dedos (Bradypus)
// Corpo peludo (esfera deformada com ruído = pelagem desgrenhada, cores por vértice: dorso mais
// escuro, peito claro), cabeça pequena e redonda, máscara facial clara com faixas escuras que
// saem dos olhos para trás, focinho curto com nariz escuro e o "sorriso" natural, braços muito
// mais longos que as pernas e 3 garras longas e curvas em cada membro. Sem cauda visível.
function makeSloth(THREE, L, o = {}) {
  const g = new THREE.Group();
  const furA = new THREE.Color(o.fur ?? '#8c7b62'), furD = new THREE.Color('#5e503f'), furL = new THREE.Color('#b9a888');
  const algae = new THREE.Color('#6f9a45');
  const furMeshes = [];
  const noise = (x, y, z) => Math.sin(x * 23.1 + y * 7.3) * Math.sin(y * 19.7 - z * 11.3) * Math.sin(z * 17.9 + x * 5.1);
  function furify(geo, shag, colorFn) {
    const P = geo.attributes.position, n = new THREE.Vector3();
    geo.computeVertexNormals(); const N = geo.attributes.normal;
    for (let i = 0; i < P.count; i++) {
      const x = P.getX(i), y = P.getY(i), z = P.getZ(i); n.set(N.getX(i), N.getY(i), N.getZ(i));
      const d = shag * (0.55 + 0.45 * noise(x, y, z)) * (0.6 + 0.4 * Math.abs(Math.sin(x * 41 + z * 37 + y * 13)));
      P.setXYZ(i, x + n.x * d, y + n.y * d, z + n.z * d);
    }
    geo.computeVertexNormals();
    const c0 = new Float32Array(P.count * 3), c1 = new Float32Array(P.count * 3), col = new THREE.Color();
    for (let i = 0; i < P.count; i++) {
      const x = P.getX(i), y = P.getY(i), z = P.getZ(i);
      colorFn(x, y, z, col); col.offsetHSL(0, 0, noise(x * 2, y * 2, z * 2) * 0.05);
      c0.set([col.r, col.g, col.b], i * 3);
      const a = 0.45 + 0.4 * (0.5 + 0.5 * noise(x * 1.3, y * 1.7, z * 1.1));
      col.lerp(algae, a); c1.set([col.r, col.g, col.b], i * 3);
    }
    geo.setAttribute('color', new THREE.BufferAttribute(c0.slice(), 3));
    const m = new THREE.Mesh(geo, L.mat('#ffffff', { vertexColors: true })); m.castShadow = m.receiveShadow = true;
    m.userData.c0 = c0; m.userData.c1 = c1; furMeshes.push(m); return m;
  }
  // corpo
  const bg = new THREE.SphereGeometry(1, 64, 48); bg.scale(0.62, 0.86, 0.52);
  const body = furify(bg, 0.07, (x, y, z, c) => {
    c.copy(furA).lerp(furD, L.clamp((-z) / 0.5) * 0.7).lerp(furL, L.clamp((z - 0.15) / 0.35) * 0.55 * L.clamp((0.5 - y) / 0.8));
  });
  g.add(body);
  // cabeça
  const head = new THREE.Group(); head.position.set(0, 0.92, 0.16); g.add(head);
  const hg = new THREE.SphereGeometry(0.40, 48, 32); hg.scale(1, 0.92, 0.88);
  head.add(furify(hg, 0.045, (x, y, z, c) => c.copy(furA).lerp(furL, 0.25).lerp(furD, L.clamp(-z / 0.3) * 0.4)));
  // máscara facial clara
  const face = L.sphere(0.3, '#eadcbc'); face.scale.set(1.08, 0.92, 0.5); face.position.set(0, -0.03, 0.24); head.add(face);
  // faixas escuras dos olhos (saem dos olhos para trás e para baixo)
  const eyes = [], brows = [];
  for (const sx of [1, -1]) {
    const m = L.sphere(0.1, '#2c2219'); m.scale.set(2.1, 0.78, 0.55); m.position.set(sx * 0.17, 0.02, 0.33); m.rotation.z = sx * -0.28; m.rotation.y = sx * 0.45; head.add(m);
    const e = L.eye(0.085); e.position.set(sx * 0.12, 0.035, 0.39); e.rotation.y = sx * 0.25; head.add(e); eyes.push(e);
    const b = L.brow(0.13, '#2c2219'); b.position.set(sx * 0.13, 0.15, 0.37); b.rotation.y = sx * 0.25; head.add(b); brows.push(b);
  }
  const snout = L.sphere(0.12, '#e3d1ad'); snout.scale.set(1.2, 0.85, 0.75); snout.position.set(0, -0.11, 0.37); head.add(snout);
  const nose = L.sphere(0.06, '#1d1714'); nose.scale.set(1.35, 0.9, 0.8); nose.position.set(0, -0.07, 0.465); head.add(nose);
  const mouthG = new THREE.Group(); mouthG.position.set(0, -0.17, 0.445); head.add(mouthG);
  const smile = L.torus(0.065, 0.013, '#3a1a14', Math.PI); smile.rotation.z = Math.PI; mouthG.add(smile);
  const open = L.sphere(0.045, '#4a1418'); open.scale.set(1.2, 1, 0.5); open.position.set(0, -0.03, 0); open.visible = false; mouthG.add(open);

  // membros: grupo com pivô no ombro/quadril; o eixo +y local aponta para a mão/pé
  function limb(r, len, nClaw, clawR) {
    const p = new THREE.Group();
    const lg = new THREE.CapsuleGeometry(r, len, 8, 20); lg.translate(0, len / 2, 0);
    p.add(furify(lg, 0.06, (x, y, z, c) => c.copy(furA).lerp(furL, 0.12).lerp(furD, L.clamp(-z / r) * 0.3)));
    const hand = new THREE.Group(); hand.position.y = len + r * 0.6; p.add(hand);
    const palm = L.sphere(r * 0.75, '#6b5b46'); palm.scale.set(1, 0.7, 0.9); hand.add(palm);
    for (let i = 0; i < nClaw; i++) {
      const cl = L.torus(clawR, 0.022, '#d9cbb0', Math.PI * 0.95);
      cl.rotation.y = Math.PI / 2; cl.position.set((i - (nClaw - 1) / 2) * r * 0.55, clawR * 0.15, 0);
      hand.add(cl);   // garra em arco: sai de trás, passa por cima e desce na frente (gancho)
    }
    p.userData = { len, hand }; return p;
  }
  const up = new THREE.Vector3(0, 1, 0);
  function aim(p, dir) { p.quaternion.setFromUnitVectors(up, dir.clone().normalize()); }
  const arms = [], legs = [];
  for (const sx of [1, -1]) {
    const a = limb(0.15, 1.2, 3, 0.13); a.position.set(sx * 0.4, 0.5, 0.02); g.add(a); arms.push(a);
    const l = limb(0.15, 0.42, 3, 0.11); l.position.set(sx * 0.3, -0.6, 0.12); g.add(l); legs.push(l);
  }
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  g.userData = { body, head, eyes, brows, arms, legs, smile, open, mouthG };
  g.pose = (name, k = 0) => {
    if (name === 'hang') {          // pendurada no galho com os dois braços (galho em y≈1.95)
      arms.forEach((a, i) => { const sx = i ? -1 : 1; aim(a, V(sx * 0.17, 1.35, -0.02)); });
      legs.forEach((l, i) => { const sx = i ? -1 : 1; aim(l, V(sx * 0.35, -0.55, 0.75)); });
    } else if (name === 'onearm') { // pendurada num braço só, o outro acenando
      aim(arms[1], V(0.2, 1.35, -0.02));
      aim(arms[0], V(0.9 + 0.2 * Math.sin(k * 6), 0.7 + 0.25 * Math.sin(k * 6), 0.35));
      legs.forEach((l, i) => { const sx = i ? -1 : 1; aim(l, V(sx * 0.35, -0.55, 0.75)); });
    } else if (name === 'eat') {    // pendurada por um braço, o outro segura a folha na boca
      aim(arms[1], V(0.2, 1.35, -0.02));
      aim(arms[0], V(-0.1, 0.2, 0.95));
      legs.forEach((l, i) => { const sx = i ? -1 : 1; aim(l, V(sx * 0.35, -0.55, 0.75)); });
    } else if (name === 'swim') {   // corpo deitado (o grupo é girado fora), braços remando
      arms.forEach((a, i) => { const ph = k * 5 + (i ? Math.PI : 0); aim(a, V((i ? -0.5 : 0.5) + 0.3 * Math.cos(ph), 1.0, 0.6 * Math.sin(ph))); });
      legs.forEach((l, i) => { const sx = i ? -1 : 1; aim(l, V(sx * 0.3, -1, 0.15 * Math.sin(k * 5 + i * 3))); });
    }
  };
  g.mood = (m) => {
    const a = { bravo: -0.4, medo: 0.45, feliz: 0.12, surpresa: 0.25, tedio: 0.0 }[m] ?? 0;
    brows.forEach((b, i) => { b.rotation.z = Math.PI / 2 + (i ? a : -a); b.position.y = m === 'surpresa' ? 0.2 : (m === 'tedio' ? 0.125 : 0.15); });
    open.visible = (m === 'surpresa' || m === 'medo'); smile.visible = !open.visible;
    if (m === 'tedio') { smile.scale.set(1, 0.35, 1); } else smile.scale.set(1, 1, 1);
  };
  g.look = (x, y) => eyes.forEach(e => e.look(x, y));
  g.blink = (k) => eyes.forEach(e => e.blink(k));
  g.chew = (t) => { mouthG.scale.y = 1 + 0.5 * Math.max(0, Math.sin(t * 3)); head.rotation.x = 0.04 * Math.sin(t * 3); };
  g.setAlgae = (k) => furMeshes.forEach(m => {
    const a = m.geometry.attributes.color, c0 = m.userData.c0, c1 = m.userData.c1;
    for (let i = 0; i < a.array.length; i++) a.array[i] = c0[i] + (c1[i] - c0[i]) * k;
    a.needsUpdate = true;
  });
  g.pose('hang'); g.mood('feliz');
  return g;
}

function leaf(THREE, L, s = 1, color = '#3f9a45') {
  const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.quadraticCurveTo(0.35 * s, 0.35 * s, 0, 1.0 * s); sh.quadraticCurveTo(-0.35 * s, 0.35 * s, 0, 0);
  const m = new THREE.Mesh(new THREE.ShapeGeometry(sh, 10), L.mat(color, { side: THREE.DoubleSide })); m.castShadow = true; return m;
}

export async function setup({ THREE, L, scene, camera, renderer }) {
  O.st = L.stage(scene, camera, renderer, { top: '#ffd98a', bottom: '#2d6a3a', ground: 'grama', groundY: -3.4, fogColor: '#9cbf7a', fogNear: 9, fogFar: 34 });
  O.st.ground.material.color.set('#4f8f3a');
  // floresta ao fundo: troncos, copas e cipós
  O.forest = new THREE.Group();
  for (let i = 0; i < 9; i++) {
    const x = -9 + i * 2.3 + (i % 2) * 0.6, z = -7 - (i % 3) * 3;
    const tr = L.cyl(0.25, 0.4, 16, i % 2 ? '#6b4a2f' : '#5a3d27'); tr.position.set(x, 3, z); O.forest.add(tr);
    for (let j = 0; j < 3; j++) { const f = L.sphere(1.6 + (j % 2) * 0.6, j % 2 ? '#2f7a3a' : '#3f8f45', 16); f.position.set(x + (j - 1) * 1.3, 7 + (j % 2) * 1.2, z); O.forest.add(f); }
    const cipo = L.cyl(0.03, 0.03, 6, '#4b6b2a', 6); cipo.position.set(x + 0.9, 3.5, z + 1); O.forest.add(cipo);
  }
  scene.add(O.forest);
  // galho principal (horizontal) com folhas
  O.branch = new THREE.Group();
  const br = L.cyl(0.13, 0.17, 7, '#6e4b2e', 20); br.rotation.z = Math.PI / 2; O.branch.add(br);
  O.leaves = [];
  for (let i = 0; i < 16; i++) {
    const lf = leaf(THREE, L, 0.42 + (i % 3) * 0.08, i % 2 ? '#3f9a45' : '#58b34f');
    const x = -3.2 + i * 0.42 + (i % 2) * 0.1;
    lf.position.set(x, 0.05, (i % 2 ? 0.12 : -0.12)); lf.rotation.set(i % 2 ? 0.5 : -0.5, i * 0.7, Math.PI + (i % 2 ? 0.6 : -0.6));
    if (Math.abs(x) < 0.85) lf.visible = false;   // não cobrir o rosto
    O.branch.add(lf); O.leaves.push(lf);
  }
  scene.add(O.branch);
  // folhas extras que crescem ao redor (cena das algas)
  O.bush = new THREE.Group();
  for (let i = 0; i < 26; i++) {
    const a = i / 26 * Math.PI * 2, r = 1.15 + (i % 3) * 0.25;
    const lf = leaf(THREE, L, 0.5 + (i % 4) * 0.08, ['#3f9a45', '#58b34f', '#6aa843', '#2f8a3f'][i % 4]);
    lf.position.set(Math.cos(a) * r, 0.3 + Math.sin(a) * r * 1.35, -0.2 - (i % 2) * 0.4); lf.rotation.set(0.2, (i % 2) * 0.6, a - Math.PI / 2);
    O.bush.add(lf);
  }
  scene.add(O.bush);
  // tronco vertical (cena do banheiro)
  O.trunk = L.cyl(0.32, 0.4, 9, '#6e4b2e', 20); scene.add(O.trunk);
  O.pile = new THREE.Group();
  for (let i = 0; i < 9; i++) { const lf = leaf(THREE, L, 0.35, i % 2 ? '#a5823d' : '#7c9a3a'); lf.rotation.set(-Math.PI / 2 + 0.3, 0, i * 0.7); lf.position.set((i % 3 - 1) * 0.3, 0.02 + i * 0.01, (Math.floor(i / 3) - 1) * 0.25); O.pile.add(lf); }
  scene.add(O.pile);
  // folha que ela come
  O.food = leaf(THREE, L, 0.5, '#5cb84f'); scene.add(O.food);
  // rio
  O.water = new THREE.Mesh(new THREE.PlaneGeometry(40, 30), new THREE.MeshPhongMaterial({ color: '#3d8fae', transparent: true, opacity: 0.72, shininess: 80, specular: '#cfefff' }));
  O.water.rotation.x = -Math.PI / 2; scene.add(O.water);
  O.rings = [];
  for (let i = 0; i < 5; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(1, 0.02, 6, 48), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.6 })); r.rotation.x = Math.PI / 2; scene.add(r); O.rings.push(r); }
  O.bub = L.bubbles(scene, 30, 3);
  // protagonista dentro de um pivô (o pivô fica na altura do galho, para balançar)
  O.pivot = new THREE.Group(); scene.add(O.pivot);
  O.hero = makeSloth(THREE, L); O.hero.position.y = -1.95; O.pivot.add(O.hero);
}

function hideAll() { [O.trunk, O.pile, O.food, O.water, O.bush, O.bub, ...O.rings].forEach(o => o.visible = false); O.branch.visible = true; O.st.ground.visible = true; }

export function update({ THREE, L, scene, camera }, c) {
  const { t, d, gt } = c;
  hideAll();
  const H = O.hero, P = O.pivot;
  P.position.set(0, 1.0, 0); P.rotation.set(0, 0, 0); P.scale.setScalar(1);
  H.rotation.set(0, 0, 0); H.position.set(0, -1.95, 0); H.scale.setScalar(1);
  H.userData.head.rotation.set(0, 0, 0); H.userData.head.scale.setScalar(1); H.userData.mouthG.scale.set(1, 1, 1);
  O.branch.position.set(0, 1.0, 0); O.branch.rotation.set(0, 0, 0);
  H.setAlgae(0); H.pose('hang'); H.mood('feliz');
  H.blink((gt % 3.7) < 0.12 ? 1 : 0); H.look(0, 0);
  const sway = (amp, sp = 1) => { P.rotation.z = Math.sin(gt * 1.2 * sp) * amp; };

  if (c.name === 'abertura') {
    sway(0.08); H.userData.head.rotation.z = Math.sin(gt * 1.2) * -0.1;
    const m1 = c.mark(1);
    if (t > m1 + 2.4) { H.mood('surpresa'); H.look(0.4, 0.2); }
    camera.position.set(0, 0.05, L.lerp(10.5, 7.2, L.easeOut(t / 2.2))); camera.lookAt(0, 0.05, 0);
  }
  else if (c.name === 'sono') {
    sway(0.04, 0.6);
    const m1 = c.mark(1);
    if (t < m1 + 0.2) { H.blink(1); H.mood('feliz'); H.userData.head.rotation.z = 0.25; H.userData.head.rotation.x = 0.15; }
    else { H.blink(0.45); H.mood('tedio'); H.look(0.5, 0); }
    camera.position.set(0.3, 0.2, 6.6); camera.lookAt(0.05, 0.1, 0);
  }
  else if (c.name === 'digestao') {
    sway(0.03, 0.5); H.pose('eat'); H.mood('tedio'); H.blink(0.35); H.chew(gt * 0.8);
    H.updateMatrixWorld(true);
    const hp = H.userData.head.localToWorld(new THREE.Vector3(0.2, -0.3, 0.5));
    O.food.visible = true; O.food.position.copy(hp); O.food.rotation.set(0.3, 0.2, 1.9);
    O.food.scale.setScalar(L.lerp(1, 0.75, L.ease(t / d)));
    const m1 = c.mark(1);
    if (t > m1 + 3.6) { H.mood('surpresa'); H.blink(0); }
    camera.position.set(-0.2, 0.15, 6.8); camera.lookAt(-0.05, 0.05, 0);
  }
  else if (c.name === 'banheiro') {
    // tronco vertical; ela desce até o chão e depois sobe mais leve
    O.branch.visible = false; O.trunk.visible = true; O.trunk.position.set(0, 1.0, -0.55);
    O.pile.visible = true; O.pile.position.set(0.0, -3.38, 0.35);
    const m1 = c.mark(1);
    const down = L.ease((t - 0.6) / 3.0), upk = L.ease((t - m1 - 0.2) / 2.5);
    const y = L.lerp(1.6, -1.15, down) + L.lerp(0, 1.9, upk);
    P.position.set(0, y, 0); H.pose('hang');
    const climb = Math.sin(gt * 3) * 0.12 * (down < 1 || (upk > 0 && upk < 1) ? 1 : 0);
    H.userData.arms.forEach((a, i) => a.rotation.x += (i ? climb : -climb));
    if (t > m1) { H.mood('feliz'); P.scale.set(L.lerp(1, 0.86, upk), 1, L.lerp(1, 0.86, upk)); H.look(0.3, 0.3); }
    else if (down > 0.95) { H.mood('surpresa'); H.look(-0.5, -0.3); }
    else { H.mood('tedio'); H.look(0, -0.5); }
    camera.position.set(0, -0.6, 10.5); camera.lookAt(0, -0.6, 0);
  }
  else if (c.name === 'nado') {
    O.branch.visible = false; O.st.ground.visible = false; O.water.visible = true; O.water.position.y = 0;
    P.position.set(-0.75, 0, 0); P.scale.setScalar(0.72); H.position.set(0, 0.15, 0); H.rotation.z = -Math.PI / 2 + 0.12;
    H.pose('swim', gt); H.mood('feliz'); H.look(0.5, 0);
    H.userData.head.rotation.z = Math.PI / 2 - 0.3;  // cabeça de pé, fora d'água
    const m1 = c.mark(1);
    const dive = L.ease((t - m1 - 3.4) / 0.8) * (1 - L.ease((t - d + 0.9) / 0.6));
    H.position.y = L.lerp(0.15, -1.25, dive) + Math.sin(gt * 5) * 0.04;
    if (dive > 0.3) { H.mood('surpresa'); H.userData.head.scale.set(1.08, 1, 1.05); O.bub.visible = true; O.bub.position.set(0.1, -1.0, 0.6); O.bub.update(gt); }
    O.rings.forEach((r, i) => { const ph = ((gt * 0.6 + i / 5) % 1); r.visible = dive < 0.5; r.position.set(-1.1 - ph * 2.2, 0.01, 0); r.scale.setScalar(0.3 + ph * 1.2); r.material.opacity = 0.6 * (1 - ph); });
    camera.position.set(0, 1.6, 7.6); camera.lookAt(0, -0.2, 0);
  }
  else if (c.name === 'algas') {
    sway(0.03, 0.7); H.mood('feliz');
    const k = L.ease((t - 0.8) / 3.0); H.setAlgae(k);
    O.bush.visible = true; O.bush.position.set(0, 0, 0);
    const g2 = L.ease((t - 3.5) / 1.5);
    O.bush.children.forEach((lf, i) => lf.scale.setScalar(Math.max(0.001, L.easeBack(g2 * 1.2 - i * 0.008))));
    H.look(Math.sin(gt * 1.5) * 0.4, 0);
    camera.position.set(0, 0.1, L.lerp(6.6, 7.6, L.ease(t / d))); camera.lookAt(0, 0.05, 0);
  }
  else if (c.name === 'final') {
    sway(0.07, 0.8); H.setAlgae(0.35);
    const m1 = c.mark(1);
    if (t > m1) { H.pose('onearm', gt); }
    H.look(0.2, 0.1);
    camera.position.set(0, 0.05, L.lerp(7.2, 8.4, L.ease(t / d))); camera.lookAt(0, 0.05, 0);
  }
  else if (c.name === 'capa') {
    P.rotation.z = 0.08; H.pose('onearm', 0.3); H.mood('feliz'); H.look(0.25, 0.1); H.blink(0);
    H.userData.head.rotation.z = -0.12;
    camera.position.set(0, 0.9, 7.5); camera.lookAt(0, 0.9, 0);
  }
}
