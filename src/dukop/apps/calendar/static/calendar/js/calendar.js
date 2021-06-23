function closeAll() {
  document.getElementById('js-overlay').classList.remove('js-active');
  document.getElementById('js-lock-body').classList.remove('js-active');
  var allActive = document.getElementsByClassName('js-active');

  Array.prototype.forEach.call(allActive, function (el) {
    el.classList.remove('js-active');
  });
}

function ready(event) {
  function addEventListenerList(list, event, fn) {
    for (var i = 0, len = list.length; i < len; i++) {
      list[i].addEventListener(event, fn, false);
    }
  }

  function toggleActive() {
    var dataElement = this.dataset.element;
    var group = document.getElementsByClassName(this.dataset.group);
    var element = document.getElementById(dataElement);
    element.classList.toggle('js-active');
  }

  document.getElementById('paginator').addEventListener('change', (event) => {
    location.href = document.querySelector('.result');
  });

  window.onhashchange = function () {
    console.log("window hash changed to", window.location.hash);
  };

  function toggleCard(event) {
    event.preventDefault();
    this.parentNode.classList.toggle('js-active');
    document.getElementById('js-overlay').classList.toggle('js-active');
    document.getElementById('js-lock-body').classList.toggle('js-active');

    // Change active URL
    if (this.parentNode.classList.contains('js-active')) {
       // prevents browser from storing history with each change:
       window.location.hash = this.parentNode.dataset.hash;
       window.scrollTo(0,0);

    }
  }

  function toggleBurger() {
    var controls = document.getElementById('js-controls');
    controls.classList.toggle('js-active');
  }

  var listJsToggle = document.getElementsByClassName('js-toggle');
  addEventListenerList(listJsToggle, 'click', toggleActive);

  var listJsToggleCard = document.getElementsByClassName('js-toggle-card');
  addEventListenerList(listJsToggleCard, 'click', toggleCard);

  var now = new Date();
  var nowElement = document.getElementById('timeline__now');
  var timeAsNumber = now.getHours() + (now.getMinutes() / 60);
  nowElement.style.marginLeft = (timeAsNumber - 8) * 6.25 + '%';
  // clean up event binding
  window.removeEventListener('DOMContentLoaded', ready);
}
// bind to the load event
window.addEventListener('DOMContentLoaded', ready);

document.onkeydown = function (evt) {
  evt = evt || window.event;
  var isEscape = false;
  if ("key" in evt) {
    isEscape = (evt.key == "Escape" || evt.key == "Esc");
  } else {
    isEscape = (evt.keyCode == 27);
  }
  if (isEscape) {
    closeAll();
  }
};
