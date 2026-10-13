/* Chat flotante con el asistente de IA (landing y home).

   Cada mensaje va por fetch() a /chat/ (ChatView en apps/landing/views.py),
   que lo reenvía al agente de n8n y devuelve su respuesta. El widget llega
   con `hidden` y solo este script lo muestra: sin JS la página queda como
   siempre, con su formulario de contacto. */
(function (window, document) {
  'use strict';

  var root = document.querySelector('[data-chat]');
  if (!root || !window.fetch || !window.FormData) return;

  // Alto máximo del campo de texto al crecer con el contenido (unas 4 líneas).
  var INPUT_MAX_HEIGHT = 120;
  // Espera antes de asomar la burbuja de bienvenida: deja leer el principio
  // de la página antes de interrumpir.
  var TEASER_DELAY = 5000;

  var toggle = root.querySelector('[data-chat-toggle]');
  var closeButton = root.querySelector('[data-chat-close]');
  var panel = root.querySelector('[data-chat-panel]');
  var list = root.querySelector('[data-chat-messages]');
  var form = root.querySelector('[data-chat-form]');
  var input = root.querySelector('[data-chat-input]');
  var sendButton = form.querySelector('[type="submit"]');
  var teaser = root.querySelector('[data-chat-teaser]');
  var sending = false;
  var teaserTimer = null;

  // Claves por página (campo oculto `source`): la landing y la home llevan
  // cada una su conversación y sus avisos aunque se abran en la misma pestaña.
  var source = form.elements.source.value;
  var CONVERSATION_KEY = 'iabits-chat-conversation-' + source;
  // El visitante ya abrió el chat o descartó el aviso: el botón deja de latir.
  var SEEN_KEY = 'iabits-chat-seen-' + source;
  // La burbuja ya asomó en esta sesión: no vuelve a salir al recargar.
  var TEASER_KEY = 'iabits-chat-teaser-' + source;

  // La conversación sigue en el servidor mientras dure la pestaña. El acceso a
  // sessionStorage puede lanzar (modo privado, cookies bloqueadas): sin él,
  // cada recarga empieza una conversación nueva y los avisos vuelven a salir.
  function readStorage(key) {
    try {
      return window.sessionStorage.getItem(key) || '';
    } catch (error) {
      return '';
    }
  }

  function writeStorage(key, value) {
    try {
      window.sessionStorage.setItem(key, value);
    } catch (error) {
      /* Sin almacenamiento el dato dura hasta recargar. */
    }
  }

  function isOpen() {
    return root.classList.contains('is-open');
  }

  function showTeaser() {
    teaserTimer = null;
    if (isOpen() || root.classList.contains('is-seen')) return;
    teaser.hidden = false;
    writeStorage(TEASER_KEY, '1');
  }

  function hideTeaser() {
    window.clearTimeout(teaserTimer);
    teaserTimer = null;
    teaser.hidden = true;
  }

  // Abrir el chat o cerrar la burbuja cuenta como "visto": se retiran la
  // burbuja y el contador y el botón deja de latir, también al recargar.
  function markSeen() {
    hideTeaser();
    root.classList.add('is-seen');
    writeStorage(SEEN_KEY, '1');
  }

  function setOpen(open, returnFocus) {
    root.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', root.getAttribute(open ? 'data-close-label' : 'data-open-label'));

    if (open) {
      markSeen();
      // En táctil, enfocar el campo abriría el teclado y taparía medio chat:
      // allí el foco va al panel y el visitante toca el campo cuando quiera.
      if (window.matchMedia('(pointer: fine)').matches) {
        input.focus();
      } else {
        panel.focus();
      }
      scrollToEnd();
    } else if (returnFocus) {
      toggle.focus();
    }
  }

  function scrollToEnd() {
    list.scrollTop = list.scrollHeight;
  }

  function addBubble(text, role) {
    var bubble = document.createElement('p');
    bubble.className = 'chat-bubble chat-bubble-' + role;
    // textContent, nunca innerHTML: la respuesta del agente no debe poder
    // inyectar HTML en la página.
    bubble.textContent = text;
    list.appendChild(bubble);
    scrollToEnd();
    return bubble;
  }

  function showTyping() {
    var bubble = document.createElement('p');
    bubble.className = 'chat-bubble chat-bubble-bot chat-typing';
    for (var i = 0; i < 3; i++) {
      var dot = document.createElement('span');
      dot.className = 'chat-typing-dot';
      dot.setAttribute('aria-hidden', 'true');
      bubble.appendChild(dot);
    }
    var label = document.createElement('span');
    label.className = 'visually-hidden';
    label.textContent = root.getAttribute('data-typing-label');
    bubble.appendChild(label);

    list.appendChild(bubble);
    scrollToEnd();
    return bubble;
  }

  function showError(message) {
    var bubble = addBubble((message || root.getAttribute('data-error-message')) + ' ', 'bot');
    bubble.classList.add('chat-bubble-error');

    var link = document.createElement('a');
    link.href = root.getAttribute('data-form-anchor');
    link.textContent = root.getAttribute('data-form-link-text');
    bubble.appendChild(link);
    scrollToEnd();
  }

  function resizeInput() {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, INPUT_MAX_HEIGHT) + 'px';
  }

  function setSending(isSending) {
    sending = isSending;
    sendButton.disabled = isSending;
  }

  function send() {
    var text = input.value.trim();
    if (sending || !text) return;

    // FormData se toma antes de vaciar el campo: lleva el token CSRF del form.
    var data = new FormData(form);
    data.set('message', text);
    data.set('conversation_id', readStorage(CONVERSATION_KEY));

    addBubble(text, 'user');
    input.value = '';
    resizeInput();
    setSending(true);
    var typing = showTyping();

    window.fetch(form.action, {
      method: 'POST',
      body: data,
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    }).then(function (response) {
      return response.json().then(function (payload) {
        return { ok: response.ok, data: payload };
      });
    }).then(function (result) {
      typing.remove();
      if (result.data.conversation_id) writeStorage(CONVERSATION_KEY, result.data.conversation_id);
      if (result.ok && result.data.ok) {
        addBubble(result.data.reply, 'bot');
        return;
      }
      showError(result.data.error);
    }).catch(function () {
      typing.remove();
      showError();
    }).then(function () {
      setSending(false);
    });
  }

  toggle.addEventListener('click', function () {
    setOpen(!isOpen(), false);
  });

  closeButton.addEventListener('click', function () {
    setOpen(false, true);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    if (isOpen()) {
      setOpen(false, true);
    } else if (!teaser.hidden) {
      markSeen();
    }
  });

  teaser.querySelector('[data-chat-teaser-open]').addEventListener('click', function () {
    setOpen(true, false);
  });

  // Al cerrar la burbuja, el foco pasa al botón del chat en vez de perderse.
  teaser.querySelector('[data-chat-teaser-close]').addEventListener('click', function () {
    markSeen();
    toggle.focus();
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    send();
  });

  // Enter envía; Shift+Enter hace salto de línea. isComposing evita enviar a
  // medias al confirmar un carácter con teclados de acentos o IME.
  input.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      send();
    }
  });

  input.addEventListener('input', resizeInput);

  // El enlace al formulario cierra el chat: en móvil ocupa toda la pantalla y
  // taparía la sección de destino.
  list.addEventListener('click', function (event) {
    if (event.target.closest('a[href^="#"]')) setOpen(false, false);
  });

  if (readStorage(SEEN_KEY)) {
    root.classList.add('is-seen');
  } else if (!readStorage(TEASER_KEY)) {
    teaserTimer = window.setTimeout(showTeaser, TEASER_DELAY);
  }

  root.hidden = false;
})(window, document);
