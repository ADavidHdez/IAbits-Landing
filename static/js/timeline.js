/* Trazado progresivo del hilo conductor de la sección de servicios.

   Escribe en --timeline-progress el porcentaje del recorrido ya alcanzado; el
   pseudo-elemento .timeline::after de main.css lo usa como altura. El avance se
   mide contra una línea de lectura situada al 60% del alto del viewport, para
   que el trazo azul acompañe a la tarjeta que se está leyendo y no al borde
   inferior de la pantalla.

   Con prefers-reduced-motion el hilo se pinta entero y no se escucha el scroll. */
(function (window, document) {
  'use strict';

  var timeline = document.querySelector('[data-timeline]');
  if (!timeline) return;

  var READING_LINE = 0.6;

  function setProgress(value) {
    timeline.style.setProperty('--timeline-progress', value);
  }

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    setProgress('100%');
    return;
  }

  var ticking = false;

  function update() {
    ticking = false;
    var rect = timeline.getBoundingClientRect();
    if (!rect.height) return;

    var advanced = window.innerHeight * READING_LINE - rect.top;
    var progress = Math.min(1, Math.max(0, advanced / rect.height));
    setProgress((progress * 100).toFixed(2) + '%');
  }

  function schedule() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(update);
  }

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  update();
})(window, document);
