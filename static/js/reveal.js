/* Aparición progresiva de los bloques al hacer scroll, sin dependencias.

   Marca con .is-revealed cualquier elemento con data-reveal en cuanto entra en
   pantalla, y solo la primera vez. Cuando la animación acaba retira el atributo
   data-reveal: el elemento queda sin reglas de aparición encima, de modo que las
   animaciones de interacción (por ejemplo .prop:hover) no se ven afectadas ni la
   entrada se repite al quitar el ratón.

   Con prefers-reduced-motion se muestra todo de inmediato. */
(function (window, document) {
  'use strict';

  var targets = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
  if (!targets.length) return;

  function reveal(element) {
    function onAnimationEnd(event) {
      if (event.target !== element) return;
      element.removeEventListener('animationend', onAnimationEnd);
      element.removeAttribute('data-reveal');
    }

    element.addEventListener('animationend', onAnimationEnd);
    element.classList.add('is-revealed');
  }

  var reducedMotion = window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reducedMotion || !('IntersectionObserver' in window)) {
    targets.forEach(reveal);
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      reveal(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

  targets.forEach(function (element) {
    observer.observe(element);
  });
})(window, document);
