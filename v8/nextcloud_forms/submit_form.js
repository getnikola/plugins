(function () {
  function submit(ev) {
    const form = ev.target;

    ev.preventDefault();

    const answers = {};
    const [,formId] = form.id.split("-");

    for (let i = 0; i < form.length; i++) {
      var input = form[i];

      // extract question id (qid) and answer id (aid)
      var [,,qid,,aid] = input.id.split("-");

      if ( qid && !(qid in answers) )
        answers[qid] = [];

      switch (input.type) {
        case "checkbox":
        case "radio":
          if (input.checked)
            answers[qid].push(aid);
          console.log(input.type, input.id, qid, aid, input.checked);
          break;

        case "select-one":
        case "text":
        case "textarea":
        case "date":
        case "datetime-local":
          if (input.value)
            answers[qid].push(input.value);
          console.log(input.type, input.id, qid, input.value);
          break;

        default:
          console.log("unknown form element type:", input.type);
      }
    }

    const request = new XMLHttpRequest();
    request.open("POST", form.action, true);
    request.setRequestHeader("OCS-APIRequest", "true");
    request.setRequestHeader("Accept", "application/json");
    request.setRequestHeader("Content-Type", "application/json");
    request.onload = function () {
        const message = document.getElementById("form-" + formId + "-messages");
        const form = document.getElementById("form-" + formId);
        const success = document.getElementById("form-" + formId + "-success");
        const response = JSON.parse(this.response);

        if (this.status == 200) {
            // success
            form.style.display = "none";
            success.style.display = "block";
        } else {
            message.innerHTML = '<div class="alert alert-danger" role="alert">' +
                this.statusText + "(" + this.status + "): " +
                response['ocs']['meta']['message'] +
                '</div>';
        }
    };
    request.send(JSON.stringify({'formId': formId, 'answers': answers}));
  }

  for (let i = 0; i < document.forms.length; i++)
    document.forms[i].onsubmit = submit;
})();
