/* Confeti sobre canvas, sin dependencias externas.
   Expone window.launchConfetti(options) para lanzar una ráfaga de partículas.

   options:
     origin        {x, y} en píxeles de viewport (por defecto, centro).
     particleCount número de partículas de la ráfaga.
     angle         dirección en grados (90 = hacia arriba).
     spread        apertura del cono en grados.
     startVelocity velocidad inicial en px/frame.
     colors        array de colores CSS.

   Con prefers-reduced-motion activo la función no hace nada. */
(function (window, document) {
  'use strict';

  var DEFAULTS = {
    particleCount: 90,
    angle: 90,
    spread: 65,
    startVelocity: 38,
    gravity: 0.85,
    decay: 0.91,
    ticks: 130,
    scalar: 1,
    colors: ['#1a56db', '#3b82f6', '#22c55e', '#facc15', '#f97316', '#ec4899'],
  };

  var canvas = null;
  var ctx = null;
  var particles = [];
  var frameId = null;

  function prefersReducedMotion() {
    return window.matchMedia
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function resizeCanvas() {
    if (!canvas) return;
    var ratio = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * ratio;
    canvas.height = window.innerHeight * ratio;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  function ensureCanvas() {
    if (canvas) return;
    canvas = document.createElement('canvas');
    canvas.className = 'confetti-canvas';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
    ctx = canvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
  }

  function destroyCanvas() {
    window.removeEventListener('resize', resizeCanvas);
    if (canvas && canvas.parentNode) canvas.parentNode.removeChild(canvas);
    canvas = null;
    ctx = null;
  }

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function createParticle(opts) {
    var radians = (opts.angle + randomBetween(-opts.spread / 2, opts.spread / 2))
      * Math.PI / 180;
    return {
      // El eje Y del canvas crece hacia abajo: se invierte para que 90° suba.
      vectorX: Math.cos(radians),
      vectorY: -Math.sin(radians),
      x: opts.origin.x,
      y: opts.origin.y,
      velocity: opts.startVelocity * randomBetween(0.5, 1),
      gravity: opts.gravity,
      decay: opts.decay,
      color: opts.colors[Math.floor(Math.random() * opts.colors.length)],
      width: randomBetween(6, 11) * opts.scalar,
      height: randomBetween(5, 9) * opts.scalar,
      tilt: randomBetween(0, Math.PI * 2),
      tiltSpeed: randomBetween(-0.14, 0.14),
      wobble: randomBetween(0, Math.PI * 2),
      wobbleSpeed: randomBetween(0.06, 0.13),
      tick: 0,
      totalTicks: opts.ticks * randomBetween(0.75, 1.25),
    };
  }

  function updateParticle(p) {
    p.x += p.vectorX * p.velocity;
    p.y += p.vectorY * p.velocity + p.gravity;
    p.velocity *= p.decay;
    p.gravity += 0.06;
    p.tilt += p.tiltSpeed;
    p.wobble += p.wobbleSpeed;
    p.tick += 1;
    return p.tick < p.totalTicks && p.y < window.innerHeight + 40;
  }

  function drawParticle(p) {
    ctx.save();
    ctx.globalAlpha = Math.max(0, 1 - p.tick / p.totalTicks);
    ctx.fillStyle = p.color;
    ctx.translate(p.x + Math.cos(p.wobble) * 8, p.y);
    ctx.rotate(p.tilt);
    // El escalado vertical simula el papel girando sobre su propio eje.
    ctx.scale(1, Math.cos(p.wobble));
    ctx.fillRect(-p.width / 2, -p.height / 2, p.width, p.height);
    ctx.restore();
  }

  function animate() {
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    particles = particles.filter(updateParticle);
    particles.forEach(drawParticle);

    if (particles.length) {
      frameId = window.requestAnimationFrame(animate);
      return;
    }
    frameId = null;
    destroyCanvas();
  }

  function launchConfetti(options) {
    if (prefersReducedMotion()) return;

    var opts = {};
    Object.keys(DEFAULTS).forEach(function (key) {
      opts[key] = (options && options[key] !== undefined) ? options[key] : DEFAULTS[key];
    });
    opts.origin = (options && options.origin)
      || { x: window.innerWidth / 2, y: window.innerHeight / 2 };

    ensureCanvas();
    for (var i = 0; i < opts.particleCount; i += 1) {
      particles.push(createParticle(opts));
    }
    if (frameId === null) {
      frameId = window.requestAnimationFrame(animate);
    }
  }

  window.launchConfetti = launchConfetti;
})(window, document);
