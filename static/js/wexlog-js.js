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
const csrftoken = getToken('csrftoken');
