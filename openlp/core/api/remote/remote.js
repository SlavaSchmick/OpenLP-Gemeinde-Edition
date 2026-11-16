/*
 * The web remote of the OpenLP Gemeinde-Edition.
 *
 * One screen: search on top, the service on the left, the slides of the live item on the right and "Show" / "Black"
 * at the bottom. Everything works with one tap. The live state comes from the web socket of OpenLP.
 */
(function () {
  'use strict';

  var API = '/api/v2';
  // Plugins whose items are listed without typing (there are only a few of them)
  var LIST_WITHOUT_TEXT = ['livevideo', 'presentations', 'images', 'media'];
  // Items which play something, they can be stopped
  var STOPPABLE = ['livevideo', 'media'];
  var SEARCH_DELAY = 250;

  var TEXTS = {
    de: {
      search: 'Lied, Nummer, Bibelstelle …', service: 'Ablauf', serviceEmpty: 'Der Ablauf ist leer.',
      nothingLive: 'Nichts live', slidesEmpty: 'Wählen Sie ein Lied im Ablauf oder suchen Sie oben.',
      live: 'Live', add: '+ Ablauf', added: '„{0}“ zum Ablauf hinzugefügt', noResults: 'Nichts gefunden.',
      show: 'Bild zeigen', blank: 'Schwarz', stop: 'Beenden', upload: 'Präsentation hochladen',
      uploading: 'Lade „{0}“ hoch …', uploaded: '„{0}“ hochgeladen', uploadFailed: 'Hochladen fehlgeschlagen',
      unsupported: 'Dieses Dateiformat wird nicht unterstützt', offline: 'Keine Verbindung zu OpenLP – verbinde neu …',
      failed: 'OpenLP hat nicht geantwortet', clear: 'Suche leeren'
    },
    ru: {
      search: 'Песня, номер, место Писания …', service: 'Порядок', serviceEmpty: 'Порядок служения пуст.',
      nothingLive: 'Ничего не показывается', slidesEmpty: 'Выберите песню в порядке или найдите её вверху.',
      live: 'Показать', add: '+ В порядок', added: '«{0}» добавлено в порядок', noResults: 'Ничего не найдено.',
      show: 'Показать', blank: 'Чёрный', stop: 'Остановить', upload: 'Загрузить презентацию',
      uploading: 'Загрузка «{0}» …', uploaded: '«{0}» загружено', uploadFailed: 'Не удалось загрузить',
      unsupported: 'Этот формат файла не поддерживается', offline: 'Нет связи с OpenLP – подключаюсь …',
      failed: 'OpenLP не ответил', clear: 'Очистить поиск'
    },
    uk: {
      search: 'Пісня, номер, місце Писання …', service: 'Порядок', serviceEmpty: 'Порядок служіння порожній.',
      nothingLive: 'Нічого не показується', slidesEmpty: 'Виберіть пісню в порядку або знайдіть її вгорі.',
      live: 'Показати', add: '+ До порядку', added: '«{0}» додано до порядку', noResults: 'Нічого не знайдено.',
      show: 'Показати', blank: 'Чорний', stop: 'Зупинити', upload: 'Завантажити презентацію',
      uploading: 'Завантаження «{0}» …', uploaded: '«{0}» завантажено', uploadFailed: 'Не вдалося завантажити',
      unsupported: 'Цей формат файлу не підтримується', offline: 'Немає зв’язку з OpenLP – підключаюся …',
      failed: 'OpenLP не відповів', clear: 'Очистити пошук'
    },
    en: {
      search: 'Song, number, Bible reference …', service: 'Service', serviceEmpty: 'The service is empty.',
      nothingLive: 'Nothing live', slidesEmpty: 'Choose a song in the service or search above.',
      live: 'Live', add: '+ Service', added: '"{0}" added to the service', noResults: 'Nothing found.',
      show: 'Show', blank: 'Black', stop: 'Stop', upload: 'Upload presentation',
      uploading: 'Uploading "{0}" …', uploaded: '"{0}" uploaded', uploadFailed: 'Upload failed',
      unsupported: 'This file format is not supported', offline: 'No connection to OpenLP – reconnecting …',
      failed: 'OpenLP did not answer', clear: 'Clear search'
    }
  };
  // The names of the verse types in the order of OpenLP (VerseType). OpenLP sends the first letter of the name in its
  // language as tag, e.g. "S1" for "Strophe 1" in German or "К1" for "Куплет 1" in Russian.
  var VERSE_NAMES = {
    de: ['Strophe', 'Refrain', 'Bridge', 'Vorrefrain', 'Intro', 'Ende', 'Anderes'],
    ru: ['Куплет', 'Припев', 'Бридж', 'Предприпев', 'Вступление', 'Окончание', 'Другое'],
    uk: ['Куплет', 'Приспів', 'Брідж', 'Передприспів', 'Вступ', 'Закінчення', 'Інше'],
    en: ['Verse', 'Chorus', 'Bridge', 'Pre-Chorus', 'Intro', 'Ending', 'Other']
  };
  var ICONS = {
    songs: 'M9 3v10.6A4 4 0 1 0 11 17V7h6V3H9z',
    bibles: 'M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm5 4v3H8v2h3v6h2v-6h3V9h-3V6h-2z',
    custom: 'M4 4h16v12H5.2L4 17.2V4zm3 3v2h10V7H7zm0 4v2h7v-2H7z',
    presentations: 'M3 3h18v2h-1v10H4V5H3V3zm3 2v8h12V5H6zm5 11h2v2.4l3.3 2-1 1.7L12 20l-3.3 2.1-1-1.7 3.3-2V16z',
    images: 'M3 4h18v16H3V4zm2 2v10l4-4 3 3 4-5 3 4V6H5zm3 1.5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z',
    media: 'M4 4h16v16H4V4zm6 4v8l6-4-6-4z',
    livevideo: 'M3 6h12v12H3V6zm13 4 5-3v10l-5-3v-4z',
    other: 'M5 4h14v16H5V4zm3 4v2h8V8H8zm0 4v2h8v-2H8z'
  };

  var texts = TEXTS.de;
  var verseNames = VERSE_NAMES.de;
  var state = {
    plugins: [],
    category: 'songs',
    service: null,
    item: null,
    slide: -1,
    searchToken: 0
  };
  var el = function (id) { return document.getElementById(id); };

  // ---- Helpers ----------------------------------------------------------------------------------------------------

  function format(text, value) {
    return text.replace('{0}', value);
  }

  function request(method, path, body) {
    var options = { method: method, headers: {} };
    if (body !== undefined) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
    return fetch(API + path, options).then(function (response) {
      if (!response.ok) {
        var error = new Error('HTTP ' + response.status);
        error.status = response.status;
        throw error;
      }
      if (response.status === 204) {
        return null;
      }
      return response.json();
    });
  }

  function post(path, body) {
    return request('POST', path, body || {}).catch(function (error) {
      toast(texts.failed, true);
      throw error;
    });
  }

  var toastTimer = null;
  function toast(message, isError) {
    var box = el('toast');
    box.textContent = message;
    box.classList.toggle('error', !!isError);
    box.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { box.hidden = true; }, isError ? 4000 : 2500);
  }

  function icon(name, cssClass) {
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('class', 'icon ' + (cssClass || ''));
    svg.setAttribute('aria-hidden', 'true');
    var path = document.createElementNS(ns, 'path');
    path.setAttribute('d', ICONS[name] || ICONS.other);
    svg.appendChild(path);
    return svg;
  }

  function make(tag, cssClass, text) {
    var node = document.createElement(tag);
    if (cssClass) {
      node.className = cssClass;
    }
    if (text !== undefined && text !== null) {
      node.textContent = text;
    }
    return node;
  }

  // File names of presentations, images and media come as full paths
  function baseName(path) {
    return String(path).split(/[\\/]/).pop();
  }

  // Formatting tags of OpenLP like {r}…{/r} or {br} aren't shown on the tablet
  function plainText(text) {
    return String(text || '').replace(/\{br\}/g, '\n').replace(/\{\/?[a-z0-9_-]+\}/gi, '').trim();
  }

  function verseLabel(tag) {
    var match = /^(\D)(\d*)(.*)$/.exec(String(tag || ''));
    if (!match) {
      return String(tag || '');
    }
    var letter = match[1].toLowerCase();
    var name = verseNames.filter(function (verseName) { return verseName.charAt(0).toLowerCase() === letter; })[0];
    if (!name) {
      return String(tag);
    }
    return (name + ' ' + match[2] + match[3]).trim();
  }

  // ---- Search -----------------------------------------------------------------------------------------------------

  function renderCategories() {
    var nav = el('categories');
    nav.textContent = '';
    state.plugins.forEach(function (plugin) {
      var button = make('button', plugin.key === state.category ? 'active' : '', plugin.name);
      button.type = 'button';
      button.addEventListener('click', function () {
        state.category = plugin.key;
        renderCategories();
        el('upload').hidden = state.category !== 'presentations';
        search();
        if (LIST_WITHOUT_TEXT.indexOf(plugin.key) === -1) {
          el('search').focus();
        }
      });
      nav.appendChild(button);
    });
    el('upload').hidden = state.category !== 'presentations';
  }

  var searchTimer = null;
  function searchSoon() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(search, SEARCH_DELAY);
  }

  function search() {
    clearTimeout(searchTimer);
    var text = el('search').value.trim();
    el('clear-search').hidden = !el('search').value;
    if (!text && LIST_WITHOUT_TEXT.indexOf(state.category) === -1) {
      closeResults();
      return;
    }
    var token = ++state.searchToken;
    var category = state.category;
    request('GET', '/plugins/' + category + '/search?text=' + encodeURIComponent(text)).then(function (results) {
      if (token === state.searchToken) {
        renderResults(category, results || []);
      }
    }).catch(function () {
      if (token === state.searchToken) {
        renderResults(category, []);
      }
    });
  }

  function resultEntry(category, result) {
    if (category === 'songs') {
      return { id: result[0], title: result[1], number: result[2] || '' };
    }
    if (category === 'bibles') {
      return { id: result[0], title: result[0], sub: plainText(result[1]) };
    }
    if (category === 'presentations' || category === 'images' || category === 'media') {
      return { id: result[0], title: baseName(result[1] || result[0]) };
    }
    return { id: result[0], title: result[1] };
  }

  function renderResults(category, results) {
    var list = el('result-list');
    list.textContent = '';
    if (!results.length) {
      list.appendChild(make('li', 'empty', texts.noResults));
    }
    results.slice(0, 100).forEach(function (result) {
      var entry = resultEntry(category, result);
      var row = make('li', 'result');
      var name = make('div', 'name');
      var title = make('div', 'title');
      if (entry.number) {
        title.appendChild(make('span', 'number', entry.number));
      }
      title.appendChild(document.createTextNode(entry.title));
      name.appendChild(title);
      if (entry.sub) {
        name.appendChild(make('div', 'sub', entry.sub));
      }
      row.appendChild(name);
      var add = make('button', 'add', texts.add);
      add.type = 'button';
      add.addEventListener('click', function () {
        post('/plugins/' + category + '/add', { id: entry.id }).then(function () {
          toast(format(texts.added, entry.title));
        });
      });
      var live = make('button', 'go-live', texts.live);
      live.type = 'button';
      live.addEventListener('click', function () {
        post('/plugins/' + category + '/live', { id: entry.id }).then(function () {
          clearSearch();
        });
      });
      row.appendChild(add);
      row.appendChild(live);
      list.appendChild(row);
    });
    openResults();
  }

  function openResults() {
    var results = el('results');
    var top = document.querySelector('.top');
    results.style.top = (top.offsetTop + top.offsetHeight) + 'px';
    results.style.maxHeight = 'calc(100% - ' + (top.offsetTop + top.offsetHeight + el('show').offsetHeight + 20) +
      'px)';
    results.hidden = false;
    results.scrollTop = 0;
  }

  function closeResults() {
    el('results').hidden = true;
    state.searchToken++;
  }

  function clearSearch() {
    el('search').value = '';
    el('clear-search').hidden = true;
    el('search').blur();
    closeResults();
  }

  // ---- Upload of presentations -------------------------------------------------------------------------------------

  function upload(file) {
    var data = new FormData();
    data.append('file', file);
    toast(format(texts.uploading, file.name));
    fetch(API + '/plugins/presentations/upload', { method: 'POST', body: data }).then(function (response) {
      if (response.status === 415) {
        toast(texts.unsupported, true);
        return;
      }
      if (!response.ok) {
        throw new Error('HTTP ' + response.status);
      }
      return response.json().then(function (presentation) {
        toast(format(texts.uploaded, presentation.title));
        state.category = 'presentations';
        renderCategories();
        el('search').value = '';
        search();
      });
    }).catch(function () {
      toast(texts.uploadFailed, true);
    });
  }

  // ---- Service ----------------------------------------------------------------------------------------------------

  function loadService() {
    return request('GET', '/service/items').then(renderService).catch(function () {});
  }

  function renderService(items) {
    var list = el('service-list');
    list.textContent = '';
    if (!items.length) {
      list.appendChild(make('li', 'empty', texts.serviceEmpty));
      return;
    }
    items.forEach(function (item) {
      var row = make('li', (item.selected ? 'live ' : '') + (item.is_valid === false ? 'invalid' : ''));
      row.appendChild(icon(item.plugin, 'kind'));
      row.appendChild(make('span', 'name', item.title));
      row.addEventListener('click', function () {
        list.querySelectorAll('li.live').forEach(function (node) { node.classList.remove('live'); });
        row.classList.add('live');
        post('/service/show', { id: item.id });
      });
      list.appendChild(row);
      if (item.selected) {
        row.scrollIntoView({ block: 'nearest' });
      }
    });
  }

  // ---- Slides -----------------------------------------------------------------------------------------------------

  function loadSlides() {
    return request('GET', '/controller/live-items').then(renderSlides).catch(function () {});
  }

  function renderSlides(item) {
    var list = el('slide-list');
    list.textContent = '';
    var slides = (item && item.slides) || [];
    el('item-title').textContent = slides.length ? item.title : texts.nothingLive;
    el('stop').hidden = !slides.length || STOPPABLE.indexOf(item.name) === -1;
    if (!slides.length) {
      list.appendChild(make('div', 'empty', texts.slidesEmpty));
      return;
    }
    var isText = item.type === 1 || item.type === 'text' ||
      slides.some(function (slide) { return !slide.img && slide.html !== slide.text; });
    slides.forEach(function (slide, index) {
      // Not a <button>: browsers size buttons in a grid wrongly, long verses would stick out
      var card = make('div', 'slide' + (slide.selected ? ' selected' : ''));
      card.setAttribute('role', 'button');
      card.tabIndex = 0;
      card.dataset.index = index;
      if (slide.img) {
        var image = make('img');
        image.src = slide.img;
        image.alt = '';
        card.appendChild(image);
        if (slide.title || slide.text) {
          card.appendChild(make('div', 'text', plainText(slide.title || slide.text)));
        }
      } else if (isText) {
        card.appendChild(make('span', 'tag', verseLabel(slide.tag)));
        card.appendChild(make('div', 'text', plainText(slide.text)));
      } else {
        if (slides.length > 1) {
          card.appendChild(make('span', 'tag', String(slide.tag)));
        }
        card.appendChild(make('div', 'text', plainText(slide.title || slide.text)));
      }
      card.addEventListener('click', function () {
        markSlide(index);
        post('/controller/show', { id: index });
      });
      list.appendChild(card);
    });
    var selected = slides.findIndex(function (slide) { return slide.selected; });
    markSlide(selected, true);
  }

  function markSlide(index, scroll) {
    state.slide = index;
    var cards = el('slide-list').querySelectorAll('.slide');
    cards.forEach(function (card) {
      card.classList.toggle('selected', Number(card.dataset.index) === index);
    });
    if (scroll && cards[index]) {
      cards[index].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  // ---- Show / black -----------------------------------------------------------------------------------------------

  function renderDisplay(results) {
    var hidden = results.blank || results.theme || results.display;
    el('blank').classList.toggle('active', !!hidden);
    el('show').classList.toggle('active', !hidden);
  }

  // ---- Live state -------------------------------------------------------------------------------------------------

  function onState(results) {
    var serviceChanged = results.service !== state.service;
    var itemChanged = results.item !== state.item;
    if (serviceChanged || itemChanged) {
      loadService();
    }
    if (itemChanged) {
      loadSlides();
    } else if (results.slide !== state.slide) {
      markSlide(results.slide, true);
    }
    state.service = results.service;
    state.item = results.item;
    state.slide = results.slide;
    renderDisplay(results);
  }

  function connect(port) {
    var protocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
    var socket;
    try {
      socket = new WebSocket(protocol + location.hostname + ':' + port);
    } catch (error) {
      setTimeout(function () { connect(port); }, 3000);
      return;
    }
    // OpenLP sends the state as binary frames (UTF-8 encoded JSON)
    socket.binaryType = 'arraybuffer';
    var offlineTimer = setTimeout(function () { el('offline').hidden = false; }, 4000);
    socket.onopen = function () {
      clearTimeout(offlineTimer);
      el('offline').hidden = true;
      // After a reconnect everything is loaded again
      state.service = null;
      state.item = null;
    };
    socket.onmessage = function (event) {
      try {
        var data = typeof event.data === 'string' ? event.data : new TextDecoder('utf-8').decode(event.data);
        var message = JSON.parse(data);
        if (message && message.results) {
          onState(message.results);
        }
      } catch (error) {
        // Not a state message
      }
    };
    socket.onclose = function () {
      clearTimeout(offlineTimer);
      el('offline').hidden = false;
      setTimeout(function () { connect(port); }, 2000);
    };
  }

  // ---- Start ------------------------------------------------------------------------------------------------------

  function applyTexts() {
    el('search').placeholder = texts.search;
    el('clear-search').setAttribute('aria-label', texts.clear);
    el('service-title').textContent = texts.service;
    el('upload').querySelector('.label').textContent = texts.upload;
    el('upload').title = texts.upload;
    el('show').querySelector('.label').textContent = texts.show;
    el('blank').querySelector('.label').textContent = texts.blank;
    el('stop').querySelector('.label').textContent = texts.stop;
    el('offline').querySelector('span').textContent = texts.offline;
  }

  function bindControls() {
    var input = el('search');
    input.addEventListener('input', searchSoon);
    input.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        search();
      } else if (event.key === 'Escape') {
        clearSearch();
      }
    });
    input.addEventListener('focus', function () {
      if (input.value.trim()) {
        search();
      }
    });
    el('clear-search').addEventListener('click', function (event) {
      event.preventDefault();
      clearSearch();
    });
    // A tap beside the results closes them
    document.querySelector('.main').addEventListener('click', function () {
      if (!el('results').hidden) {
        closeResults();
        input.blur();
      }
    }, true);
    el('show').addEventListener('click', function () {
      el('show').classList.add('active');
      el('blank').classList.remove('active');
      post('/core/display', { display: 'show' });
    });
    el('blank').addEventListener('click', function () {
      el('blank').classList.add('active');
      el('show').classList.remove('active');
      post('/core/display', { display: 'blank' });
    });
    el('stop').addEventListener('click', function () {
      post('/controller/clear/live');
    });
    el('upload').addEventListener('click', function () {
      el('upload-file').value = '';
      el('upload-file').click();
    });
    el('upload-file').addEventListener('change', function () {
      if (this.files && this.files[0]) {
        upload(this.files[0]);
      }
    });
  }

  function start() {
    applyTexts();
    bindControls();
    request('GET', '/core/language').then(function (data) {
      var language = String((data && data.language) || 'de').toLowerCase().split(/[_-]/)[0];
      texts = TEXTS[language] || TEXTS.en;
      verseNames = VERSE_NAMES[language] || VERSE_NAMES.en;
      document.documentElement.lang = language;
      applyTexts();
      loadSlides();
    }).catch(function () {});
    request('GET', '/core/plugins').then(function (plugins) {
      state.plugins = plugins || [];
      if (state.plugins.length && !state.plugins.some(function (plugin) { return plugin.key === state.category; })) {
        state.category = state.plugins[0].key;
      }
      renderCategories();
    }).catch(function () {});
    request('GET', '/core/system').then(function (system) {
      connect(system.websocket_port || 4317);
    }).catch(function () {
      connect(4317);
    });
    loadService();
    loadSlides();
  }

  start();
}());
