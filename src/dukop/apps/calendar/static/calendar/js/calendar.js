/*
Zero-framework JS stuff
*/

function closeAll() {
  document.getElementById('js-overlay').classList.remove('js-active');
  document.getElementById('js-lock-body').classList.remove('js-active');
  var allActive = document.getElementsByClassName('js-active');

  Array.prototype.forEach.call(allActive, function (el) {
    el.classList.remove('js-active');
  });
}

function ready(event) {

  paginator_select = document.getElementById('paginator');
  if (paginator_select) {
    paginator_select.addEventListener('change', (event) => {
      location.href = document.querySelector('.result');
    });
  }

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

  var listJsToggle = document.getElementsByClassName('js-toggle');
  addEventListenerList(listJsToggle, 'click', toggleActive);


  var now = new Date();
  var nowElement = document.getElementById('timeline__now');
  var timeAsNumber = now.getHours() + (now.getMinutes() / 60);
  nowElement.style.marginLeft = (timeAsNumber - 8) * 6.25 + '%';

  // clean up event binding
  window.removeEventListener('DOMContentLoaded', ready);
}

// bind to the load event
window.addEventListener('DOMContentLoaded', ready);

/*
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
*/
