/* Hilo conductor de la sección de servicios.

   Dos cosas, calculadas en el mismo frame:
     1. --timeline-progress: el porcentaje de recorrido trazado, que .timeline::after
        de main.css usa como altura del trazo azul.
     2. .is-lit en cada bloque cuando ese trazo alcanza la altura de su icono,
        lo que enciende el nodo y hace aparecer el icono.

   El avance se mide contra una línea de lectura situada al 60% del alto del
   viewport, para que el trazo acompañe a la tarjeta que se está leyendo y no al
   borde inferior de la pantalla. Los bloques ya encendidos salen de la lista de
   pendientes: no se vuelven a medir ni se apagan al subir.

   Con prefers-reduced-motion se pinta el hilo entero y se encienden todos. */
(function (window, document) {
  'use strict';

  var timeline = document.querySelector('[data-timeline]');
  if (!timeline) return;

  var READING_LINE = 0.6;

  var pending = Array.prototype.slice
    .call(timeline.querySelectorAll('[data-timeline-item]'))
    .map(function (item) {
      return { item: item, icon: item.querySelector('[data-timeline-icon]') };
    })
    .filter(function (entry) {
      return !!entry.icon;
    });

  function setProgress(value) {
    timeline.style.setProperty('--timeline-progress', value);
  }

  function light(entry) {
    entry.item.classList.add('is-lit');
  }

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    setProgress('100%');
    pending.forEach(light);
    return;
  }

  var ticking = false;

  function update() {
    ticking = false;
    var rect = timeline.getBoundingClientRect();
    if (!rect.height) return;

    var readingLine = window.innerHeight * READING_LINE;
    var advanced = readingLine - rect.top;
    setProgress((Math.min(1, Math.max(0, advanced / rect.height)) * 100).toFixed(2) + '%');

    // Extremo real del trazo azul, recortado a los límites de la sección.
    var traceEnd = Math.min(Math.max(readingLine, rect.top), rect.bottom);

    pending = pending.filter(function (entry) {
      var iconRect = entry.icon.getBoundingClientRect();
      if (iconRect.top + iconRect.height / 2 > traceEnd) return true;
      light(entry);
      return false;
    });
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
