/* Interacción 3D de las tarjetas de servicios, sin dependencias externas.

   Dos comportamientos, apoyados en clases y custom properties que consume
   main.css:
     1. Escritorio: inclinación que sigue al puntero (--tilt-x / --tilt-y).
     2. Táctil: la tarjeta centrada en el viewport se activa (.is-active).

   La entrada escalonada al hacer scroll no vive aquí: la gestiona reveal.js
   junto con la del resto de la página. Con prefers-reduced-motion no se
   registra ningún listener. */
(function (window, document) {
  'use strict';

  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-card-3d]'));
  if (!cards.length) return;

  var MAX_TILT = 8;
  // Distancia máxima al centro del viewport, en fracción de su alto, para
  // que una tarjeta se considere activa en táctil.
  var ACTIVE_RANGE = 0.35;

  function matches(query) {
    return !!window.matchMedia && window.matchMedia(query).matches;
  }

  if (matches('(prefers-reduced-motion: reduce)')) return;

  var finePointer = matches('(hover: hover) and (pointer: fine)');

  function enableTilt(card) {
    var frame = null;
    var pointer = null;

    function apply() {
      frame = null;
      if (!pointer) return;

      var rect = card.getBoundingClientRect();
      if (!rect.width || !rect.height) return;

      // Posición del puntero dentro de la tarjeta, de -0.5 a 0.5.
      var offsetX = (pointer.x - rect.left) / rect.width - 0.5;
      var offsetY = (pointer.y - rect.top) / rect.height - 0.5;

      card.style.setProperty('--tilt-y', (offsetX * 2 * MAX_TILT).toFixed(2) + 'deg');
      card.style.setProperty('--tilt-x', (-offsetY * 2 * MAX_TILT).toFixed(2) + 'deg');
    }

    card.addEventListener('pointermove', function (event) {
      if (event.pointerType && event.pointerType !== 'mouse') return;
      pointer = { x: event.clientX, y: event.clientY };
      if (frame === null) frame = window.requestAnimationFrame(apply);
    });

    card.addEventListener('pointerleave', function () {
      pointer = null;
      if (frame !== null) {
        window.cancelAnimationFrame(frame);
        frame = null;
      }
      card.style.removeProperty('--tilt-x');
      card.style.removeProperty('--tilt-y');
    });
  }

  function enableActiveOnScroll() {
    var ticking = false;

    function update() {
      ticking = false;
      var viewportCenter = window.innerHeight / 2;
      var closest = null;
      var closestDistance = window.innerHeight * ACTIVE_RANGE;

      cards.forEach(function (card) {
        var rect = card.getBoundingClientRect();
        var distance = Math.abs(rect.top + rect.height / 2 - viewportCenter);
        if (distance < closestDistance) {
          closestDistance = distance;
          closest = card;
        }
      });

      cards.forEach(function (card) {
        card.classList.toggle('is-active', card === closest);
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
  }

  if (finePointer) {
    cards.forEach(enableTilt);
  } else {
    enableActiveOnScroll();
  }
})(window, document);
