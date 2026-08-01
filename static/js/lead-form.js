/* Envío del formulario de leads sin recargar la página.

   La vista (apps/landing/views.py) responde JSON cuando detecta la cabecera
   X-Requested-With. Si este script no se ejecuta, el navegador hace el POST
   normal y la vista mantiene el flujo Post/Redirect/Get. */
(function (window, document) {
  'use strict';

  var form = document.querySelector('[data-lead-form]');
  if (!form || !window.fetch || !window.FormData) return;

  var feedback = document.querySelector('[data-form-feedback]');
  var nonFieldErrors = form.querySelector('[data-form-errors]');
  var submitButton = form.querySelector('[type="submit"]');
  var submitText = submitButton.textContent;
  var sendingText = submitButton.getAttribute('data-sending-text') || submitText;
  var errorMessage = form.getAttribute('data-error-message');
  var sending = false;

  function clearErrors() {
    form.querySelectorAll('.errorlist').forEach(function (list) {
      list.remove();
    });
  }

  function buildErrorList(fieldErrors) {
    var list = document.createElement('ul');
    list.className = 'errorlist';
    fieldErrors.forEach(function (error) {
      var item = document.createElement('li');
      item.textContent = error.message;
      list.appendChild(item);
    });
    return list;
  }

  function renderErrors(errors) {
    clearErrors();
    var firstInvalidField = null;

    Object.keys(errors).forEach(function (name) {
      var container = form.querySelector('[data-field="' + name + '"]');
      if (container) {
        container.appendChild(buildErrorList(errors[name]));
        if (!firstInvalidField) firstInvalidField = container.querySelector('input, select, textarea');
      } else {
        // Errores no ligados a un campo visible (non-field, honeypot).
        nonFieldErrors.appendChild(buildErrorList(errors[name]));
      }
    });

    if (firstInvalidField) firstInvalidField.focus();
  }

  function showFeedback(message, tag) {
    var list = document.createElement('ul');
    list.className = 'messages';
    var item = document.createElement('li');
    item.className = tag;
    item.textContent = message;
    list.appendChild(item);

    feedback.innerHTML = '';
    feedback.appendChild(list);
    feedback.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  function celebrate() {
    if (!window.launchConfetti) return;

    var rect = submitButton.getBoundingClientRect();
    var origin = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };

    window.launchConfetti({ origin: origin });
    window.setTimeout(function () {
      window.launchConfetti({
        origin: { x: 0, y: window.innerHeight * 0.85 },
        angle: 55,
        particleCount: 55,
      });
      window.launchConfetti({
        origin: { x: window.innerWidth, y: window.innerHeight * 0.85 },
        angle: 125,
        particleCount: 55,
      });
    }, 180);
  }

  function setSending(isSending) {
    sending = isSending;
    submitButton.disabled = isSending;
    submitButton.textContent = isSending ? sendingText : submitText;
  }

  form.addEventListener('submit', function (event) {
    if (sending) {
      event.preventDefault();
      return;
    }
    event.preventDefault();
    setSending(true);

    window.fetch(form.action || window.location.pathname, {
      method: 'POST',
      body: new FormData(form),
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    }).then(function (response) {
      return response.json().then(function (data) {
        return { ok: response.ok, data: data };
      });
    }).then(function (result) {
      if (result.ok && result.data.ok) {
        clearErrors();
        form.reset();
        showFeedback(result.data.message, 'success');
        celebrate();
        return;
      }
      feedback.innerHTML = '';
      renderErrors(result.data.errors || {});
    }).catch(function () {
      showFeedback(errorMessage, 'error');
    }).then(function () {
      setSending(false);
    });
  });
})(window, document);
