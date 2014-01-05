function logout() {
    /**** OLD CODE
    try {
        document.execCommand("ClearAuthenticationCache");
    } catch (exception) {
        //not an IE browser
        $.ajax({
            url: '/logout',
            username: 'reset',
            password: 'reset',
            statusCode: { 401: function() { alert('Logged Out') } }
        });
    } **** END OLD CODE */

    /**** NEW CODE */
    try {
          $.ajax({
               url: '/logout',
               username: 'reset',
               password: 'reset',
               statusCode: { 401: function() { alert('Logged Out') } }
         });
    } catch (exception) {
         document.execCommand("ClearAuthenticationCache");
         } /**** END NEW CODE */
    return false;
}

function send(command) {
            $.ajax({
                type: "POST",
                url: "/invoke/" + command,
                success: function (html) {
                    $("#result").empty();
                    $("#result").append("Последняя комманда: <b>" + html + "</b>");
                }
            });
}

function keyEvent() {
  status='Unicode= '+event.keyCode+' Символ='+String.fromCharCode(event.keyCode);
  switch (event.keyCode) //Анализ Unicode клавиш
  {
        case 37: {send("move_left"); break} // "Стрелка влево"
        case 40: {send("move_backward"); break}  // "Стрелка вниз"
        case 39: {send("move_right"); break} // "Стрелка вправо"
        case 38: {send("move_forward"); break}  // "Стрелка вверх"
        default: switch (String.fromCharCode(event.keyCode)) //Анализ клавиши
                 {
                      case 'W': {send("cam_up"); break}   //Камера вверх
                      case 'Z': {send("cam_down"); break} //Камера вниз
                      case 'A': {send("cam_left"); break} //Камера влево
                      case 'S': {send("cam_right"); break} //Камера вправо
                      default: <!-- {send(String.fromCharCode(event.keyCode)); -->  break}
                 }
  }
  $("#key").empty();
  $("#key").append(status);
}

function SetResolution2(r) {
       
       $.ajax({
                type: "POST",
                url: "/set_resolution/" + r,                
                success: function(html) {
                    $("#result").empty();
                    $("#result").append("Установлен режим: <b>" + html + "</b>");
                }
        });
}


function ShowTemperature() {
        $.ajax({
                type: "GET",
                url: "/get_temperature",
                cache: false,
                success: function(html){
                        $("#temperature").empty();
                        $("#temperature").append("<b>"+html+"&deg;C</b>"); 
                }
        });
}

function ShowPressure() {
        $.ajax({
                type: "GET",
                url: "/get_pressure",
                cache: false,
                success: function(html){
                        $("#pressure").empty();
                        $("#pressure").append("<b>"+html+" мм. рт. ст.</b>");
                }
        });
}

function Show() {
        ShowTemperature();
        ShowPressure();
}

$(document).ready(function(){
        Show();
        setInterval('Show()',60000);
});


