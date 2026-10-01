/* Chat flotante con el asistente de IA.

   Cada mensaje va por fetch() a /landing/chat/ (ChatView en apps/landing/views.py),
   que lo reenvía al agente de n8n y devuelve su respuesta. El widget llega
   con `hidden` y solo este script lo muestra: sin JS la landing queda como
   siempre, con el formulario de contacto. */
(function (window, document) {
  'use strict';

  var root = document.querySelector('[data-chat]');
  if (!root || !window.fetch || !window.FormData) return;

  var STORAGE_KEY = 'iabits-chat-conversation';
  // Alto máximo del campo de texto al crecer con el contenido (unas 4 líneas).
  var INPUT_MAX_HEIGHT = 120;

  var toggle = root.querySelector('[data-chat-toggle]');
  var closeButton = root.querySelector('[data-chat-close]');
  var panel = root.querySelector('[data-chat-panel]');
  var list = root.querySelector('[data-chat-messages]');
  var form = root.querySelector('[data-chat-form]');
  var input = root.querySelector('[data-chat-input]');
  var sendButton = form.querySelector('[type="submit"]');
  var sending = false;

  // La conversación sigue en el servidor mientras dure la pestaña. El acceso a
  // sessionStorage puede lanzar (modo privado, cookies bloqueadas): sin él,
  // cada recarga simplemente empieza una conversación nueva.
  function readConversationId() {
    try {
      return window.sessionStorage.getItem(STORAGE_KEY) || '';
    } catch (error) {
      return '';
    }
  }

  function saveConversationId(id) {
    try {
      window.sessionStorage.setItem(STORAGE_KEY, id);
    } catch (error) {
      /* Sin almacenamiento la conversación dura hasta recargar. */
    }
  }

  function isOpen() {
    return root.classList.contains('is-open');
  }

  function setOpen(open, returnFocus) {
    root.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', root.getAttribute(open ? 'data-close-label' : 'data-open-label'));

    if (open) {
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
    data.set('conversation_id', readConversationId());

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
      if (result.data.conversation_id) saveConversationId(result.data.conversation_id);
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
    if (event.key === 'Escape' && isOpen()) setOpen(false, true);
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

  root.hidden = false;
})(window, document);
