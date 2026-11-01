// "Você é uma piranha!" — cenas 3D (three.js). Cada cena = um nome de "scene" dos SEGS.
let O = {};

export async function setup({ THREE, L, scene, camera, renderer }) {
  const st = L.stage(scene, camera, renderer, { top: '#2b9be0', bottom: '#052139', ground: 'agua', groundY: -2.4, fogColor: '#0b4f7d', fogNear: 6, fogFar: 26 });
  O.bub = L.bubbles(scene, 60, 10);
  // raios de luz vindos da superfície
  O.rays = new THREE.Group();
  for (let i = 0; i < 6; i++) {
    const r = new THREE.Mesh(new THREE.ConeGeometry(0.6, 14, 16, 1, true),
      new THREE.MeshBasicMaterial({ color: 0xbfe8ff, transparent: true, opacity: 0.07, side: THREE.DoubleSide, depthWrite: false }));
    r.position.set(-5 + i * 2, 4, -4 - (i % 3)); r.rotation.z = 0.25; O.rays.add(r);
  }
  scene.add(O.rays);
  // plantas no fundo
  O.plants = new THREE.Group();
  for (let i = 0; i < 14; i++) {
    const p = L.capsule(0.08, 1 + (i % 4) * 0.5, i % 2 ? '#2f8f4e' : '#3fae5a');
    p.position.set(-7 + i, -2.0, -3 - (i % 5)); O.plants.add(p);
  }
  scene.add(O.plants);

  // protagonista
  O.hero = L.makeFish({ body: '#8f9db3', belly: '#ff4b2b', fin: '#6f7f99', teeth: true, size: 1 });
  scene.add(O.hero);
  // cardume (amigas)
  O.school = [];
  for (let i = 0; i < 14; i++) {
    const f = L.makeFish({ body: '#8796ad', belly: '#f0532f', fin: '#6a7a92', teeth: true, size: 0.55 });
    f.userData.home = new THREE.Vector3((i % 5 - 2) * 1.4 + (Math.random() - .5) * .5, Math.floor(i / 5) * 1.1 - 1.0, -2 - (i % 3) * 1.2);
    f.userData.ph = Math.random() * 10; scene.add(f); O.school.push(f);
  }
  // predadores
  O.boto = new THREE.Group();
  const bb = L.capsule(0.7, 2.6, '#f5a3c0'); bb.rotation.z = Math.PI / 2; O.boto.add(bb);
  const sn = L.cone(0.22, 1.2, '#f5a3c0'); sn.rotation.z = -Math.PI / 2; sn.position.x = 2.4; O.boto.add(sn);
  const df = L.cone(0.35, 0.8, '#e88aac', 4); df.position.set(-0.2, 0.8, 0); df.scale.z = .3; O.boto.add(df);
  const be = L.eye(0.16); be.position.set(1.5, 0.25, 0.6); O.boto.add(be);
  O.boto.scale.setScalar(1.2); scene.add(O.boto);
  O.jacare = new THREE.Group();
  const jb = L.capsule(0.55, 3.2, '#3f6b2e'); jb.rotation.z = Math.PI / 2; jb.scale.y = 0.7; O.jacare.add(jb);
  const jh = L.box(1.8, 0.35, 0.7, '#4c7d37'); jh.position.set(2.6, 0.05, 0); O.jacare.add(jh);
  for (const z of [0.25, -0.25]) { const e = L.eye(0.16); e.position.set(2.0, 0.42, z); O.jacare.add(e); }
  scene.add(O.jacare);

  // comida (cardápio)
  O.menu = new THREE.Group();
  const peixinho = L.makeFish({ body: '#ffd34d', belly: '#ffe9a0', size: 0.35 }); peixinho.position.set(-0.6, 1.0, 0); O.menu.add(peixinho);
  const inseto = L.makeBlob({ color: '#6b4f2a', size: 0.3, squash: 0.7 }); inseto.position.set(0.7, 1.6, 0); O.menu.add(inseto);
  const fruta = L.sphere(0.35, '#d9342b'); fruta.position.set(-0.4, 2.5, 0); O.menu.add(fruta);
  const folha = L.sphere(0.4, '#43b45a'); folha.scale.set(1.4, 0.15, 0.8); folha.position.set(0.6, 0.3, 0.5); O.menu.add(folha);
  scene.add(O.menu);

  // dentes grandes (close nos dentes): duas fileiras; a da esquerda cai e a nova sobe
  O.teeth = new THREE.Group();
  O.gum = L.box(5.2, 0.5, 1.0, '#c9505e'); O.gum.position.y = 0.6; O.teeth.add(O.gum);
  O.oldL = new THREE.Group(); O.oldR = new THREE.Group(); O.newL = new THREE.Group();
  for (let i = 0; i < 6; i++) {
    const x = -2.2 + i * 0.85;
    const t = L.cone(0.38, 1.1, '#fffaf0', 3); t.rotation.x = Math.PI; t.position.set(x < 0 ? x : x, 0, 0);
    (x < 0 ? O.oldL : O.oldR).add(t);
    if (x < 0) { const n = L.cone(0.38, 1.1, '#ffffff', 3); n.rotation.x = Math.PI; n.position.set(x, 0, 0); O.newL.add(n); }
  }
  O.teeth.add(O.oldL, O.oldR, O.newL); scene.add(O.teeth);
}

function hideAll() { [O.hero, O.boto, O.jacare, O.menu, O.teeth, ...O.school].forEach(o => o.visible = false); }

function schoolAt(L, gt, spread = 1, cx = 0) {
  O.school.forEach((f, i) => {
    const h = f.userData.home; f.visible = true;
    f.position.set(cx + h.x * spread + Math.sin(gt * 1.3 + f.userData.ph) * .25, h.y * spread + Math.sin(gt * 1.7 + i) * .15, h.z);
    f.swim(gt + f.userData.ph, 1.2);
  });
}

export function update({ THREE, L, scene, camera }, c) {
  const { t, d, gt } = c;
  hideAll(); O.bub.update(gt);
  O.rays.children.forEach((r, i) => r.material.opacity = 0.05 + 0.03 * Math.sin(gt * 0.8 + i));
  const H = O.hero; const e = H.userData.eyes[0];
  H.rotation.set(0, 0, 0); H.position.set(0, 0, 0); H.scale.setScalar(1);
  e.blink((gt % 3.3) < 0.1 ? 1 : 0); e.look(0.3, 0);

  if (c.name === 'abertura') {
    H.visible = true; H.swim(gt, 0.6);
    const scared = L.ease((t - c.mark(1) - 1.2) / 0.4);
    H.mood(scared > 0.5 ? 'medo' : 'bravo'); H.chomp(scared > 0.5 ? 0 : gt * 0.8);
    H.rotation.y = -0.95 + Math.sin(gt * .7) * .08; H.scale.setScalar(0.85);
    e.look(scared > .5 ? -0.6 + Math.sin(gt * 9) * .3 : 0.4, 0);
    H.position.x = scared > .5 ? Math.sin(gt * 30) * 0.03 : 0;
    camera.position.set(0.2, 0.3, L.lerp(10, 6.8, L.easeOut(t / 2))); camera.lookAt(0.2, -0.1, 0);
  }
  else if (c.name === 'cardume') {
    H.visible = true; H.swim(gt, 1.3); H.mood('medo'); H.scale.setScalar(0.75);
    const k = L.ease((t - c.mark(1)) / 1.0);
    H.position.set(0, -0.2, -1.4);
    schoolAt(L, gt, L.lerp(1.0, 0.7, k));
    O.boto.visible = true; O.boto.position.set(L.lerp(12, 5.5, L.ease((t - c.mark(1)) / 1.5)), 2.6, -5); O.boto.rotation.y = Math.PI;
    O.boto.rotation.z = Math.sin(gt * 1.5) * .05;
    O.jacare.visible = true; O.jacare.position.set(L.lerp(-13, -5.8, L.ease((t - c.mark(1) - 0.8) / 1.5)), -1.6, -4);
    camera.position.set(0, 0.8, 9.5); camera.lookAt(0, 0, -2);
  }
  else if (c.name === 'nervosa') {
    // só duas piranhas: respiração acelerada. Depois o grupo chega e ela acalma.
    const calm = L.ease((t - c.d * 0.62) / 1.2);
    H.visible = true; H.mood(calm > .5 ? 'feliz' : 'medo'); H.swim(gt, 0.8);
    H.chomp(gt * L.lerp(5, 0.8, calm)); H.rotation.y = -0.9; H.scale.setScalar(0.8); H.position.y = -0.7;
    const b = O.school[0]; b.visible = true; b.position.set(-0.3, 1.4, -0.8); b.rotation.y = -0.6; b.swim(gt, 1);
    if (calm > 0.01) O.school.slice(1).forEach((f, i) => { f.visible = true; const h = f.userData.home; f.position.set(L.lerp(h.x + 14, h.x, calm), h.y, h.z - 1); f.swim(gt + i, 1.2); });
    e.look(Math.sin(gt * 7) * 0.7, 0);
    camera.position.set(0.1, 0.3, 8.2); camera.lookAt(0, 0.1, -0.5);
  }
  else if (c.name === 'cardapio') {
    H.visible = true; H.mood('feliz'); H.swim(gt, 0.7); H.position.set(0, -1.5, 0); H.scale.setScalar(0.7);
    H.rotation.y = -0.9;
    O.menu.visible = true; O.menu.children.forEach((m, i) => {
      const a = L.easeBack((t - 0.4 - i * 0.6) / 0.5); m.scale.setScalar(Math.max(0.001, a));
      if (m.userData.y0 === undefined) m.userData.y0 = m.position.y; m.position.y = m.userData.y0 + Math.sin(gt * 2 + i) * 0.12; m.rotation.y = gt * (0.6 + i * .2);
    });
    H.chomp(t > c.d - 1.5 ? (t - c.d + 1.5) * 2 : 0);
    camera.position.set(0, 0.4, 9.5); camera.lookAt(0, 0.4, 0);
  }
  else if (c.name === 'dentes') {
    O.teeth.visible = true;
    const drop = L.ease((t - c.mark(1) - 0.8) / 1.0), rise = L.ease((t - c.mark(1) - 2.2) / 1.0);
    O.oldL.position.y = -6 * drop; O.oldL.rotation.z = 0.4 * drop;
    O.newL.position.y = L.lerp(1.3, 0, rise); O.newL.visible = drop > 0.05;
    O.newL.children.forEach(n => n.material.color.set(rise > 0.95 ? '#ffffff' : '#e8f4ff'));
    O.teeth.rotation.y = Math.sin(gt * .5) * .25; O.teeth.position.set(0, 0.4, 0); O.teeth.scale.setScalar(0.42);
    camera.position.set(0, 0.2, 7.5); camera.lookAt(0, 0.3, 0);
  }
  else if (c.name === 'late') {
    H.visible = true; H.mood('bravo'); H.swim(gt, 1);
    const bark = Math.max(0, Math.sin(gt * 9)) * (t > 0.3 && t < c.d - 0.5 ? 1 : 0);
    H.chomp(bark > 0.3 ? 0.5 : 0); H.scale.setScalar(1 + bark * 0.06);
    H.rotation.y = -0.95; H.position.y = bark * 0.08 - 0.2; H.scale.multiplyScalar(0.85);
    camera.position.set(0.2, 0.3, 7.0); camera.lookAt(0.2, -0.1, 0);
  }
  else if (c.name === 'final') {
    H.visible = true; H.mood('feliz'); H.swim(gt, 1); H.rotation.y = -0.9 + Math.sin(gt) * .1; H.position.set(0, -0.3, 0); H.scale.setScalar(0.8);
    e.look(0.2, 0.1); schoolAt(L, gt, 1.0);
    camera.position.set(0, 0.4, L.lerp(8, 10, L.ease(t / c.d))); camera.lookAt(0, 0, -1);
  }
  else if (c.name === 'capa') {
    H.visible = true; H.mood('bravo'); H.chomp(0.5); H.rotation.y = -1.0; H.position.set(0, -1.0, 0); H.scale.setScalar(0.95);
    H.userData.tail.rotation.y = 0.3; e.look(0.5, 0); e.blink(0);
    schoolAt(L, 2.0, 1.1);
    O.school.forEach(f => f.position.z -= 2);
    camera.position.set(0.2, -0.2, 7.0); camera.lookAt(0.1, -0.5, 0);
  }
}
