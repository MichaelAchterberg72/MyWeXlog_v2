var maxBtns = document.getElementsByClassName('max-btn')

for (i = 0; i < maxBtns.length; i++) {

  maxBtns[i].addEventListener('click', function(){
    var vc = this.dataset.vac
    var tt = this.dataset.tlt
    updateVacancyViewed(vc, tt)
  })
}

function updateVacancyViewed(vc, tt){
  var url = '/marketplace/vacancy-viewed-updated/'

  fetch(url, {
    method:'POST',
    headers:{
        'Content-Type':'application/json',
        'X-CSRFToken':csrftoken,
    },
    body:JSON.stringify({'vac':vc, 'tlt':tt})
  })
  .then((response) => {
    return response.json();
  })
  .then((data) => {
    console.log('Data:', data)
  });
}

function getToken(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
/*const csrftoken = getToken('csrftoken');*/

/* js for mod_corporate */

var updateStatus = document.getElementsByClassName('update-status')

for (var i = 0; i < updateStatus.length; i++){
  updateStatus[i].addEventListener('click', function(){
    var staffSlug = this.dataset.slug
    var action = this.dataset.action

    var url = '/corporate/admin-permission/'
    var csrftoken = Cookies.get('csrftoken');

    fetch(url, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'X-CSRFToken':csrftoken,
      },
      body:JSON.stringify({'staffSlug': staffSlug, 'action': action})
    })

    .then((response) => {
      return response.json();
    })

    .then ((data) => {
      location.reload()
    });
  });
}

var currentStaff = document.getElementsByClassName('update-staff')

for (var i = 0; i < currentStaff.length; i++){
  currentStaff[i].addEventListener('click', function(){
    var staffSlug = this.dataset.slug
    var action = this.dataset.action
    console.log(staffSlug)
    var url = '/corporate/staff-actions/'
    var csrftoken = Cookies.get('csrftoken');

    fetch(url, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'X-CSRFToken':csrftoken,
      },
      body:JSON.stringify({'staffSlug': staffSlug, 'action': action})
    })

    .then((response) => {
      return response.json();
    })

    .then ((data) => {
      location.reload()
    });
  });
}

var hiddenBtn = document.getElementsByClassName('hide-talent')

for (var i = 0; i < hiddenBtn.length; i++){
  hiddenBtn[i].addEventListener('click', function(){
    var tltAlias = this.dataset.slug
    var action = this.dataset.action

    var url = '/corporate/hidden-actions/'
    var csrftoken = Cookies.get('csrftoken');

    fetch(url, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'X-CSRFToken':csrftoken,
      },
      body:JSON.stringify({'tltAlias': tltAlias, 'action': action})
    })

    .then((response) => {
      return response.json();
    })

    .then ((data) => {
      location.reload()
    });
  });
}

var setCorpCookie = document.getElementsByClassName('setCorp')

for (var i = 0; i < setCorpCookie.length; i++){
  setCorpCookie[i].addEventListener('click', function(){
    var corp = this.dataset.slug

    document.cookie = 'corp=' + JSON.stringify(corp) + ";max-age=83200; domain=; path=/"

  });
}
