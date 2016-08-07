// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers

var attempts = 1;
function generateInterval (k) {
    return Math.min(5, (Math.pow(2, k) - 1)) * 1000;
}

function generateId(){
    // http://stackoverflow.com/a/2117523
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

function getId(){
    var guid = localStorage.getItem('djaodjin-chat:guid');
    if ( !guid ){
        guid = generateId();
        localStorage.setItem('djaodjin-chat:guid', guid);
    }
    return guid
}

var socket;
function createWebSocket () {
    socket = new WebSocket("ws://" + window.location.host + "/chat/");

    socket.addEventListener('open',function () {
        attempts = 1; 

    });
    
    socket.addEventListener('close', function () {
        var time = generateInterval(attempts);
        
        setTimeout(function () {
            attempts++;
            
            createWebSocket(); 
        }, time);
    });

    socket.addEventListener('message',function(e) {
        console.log(e);
        var $nextMessage = $('<div/>');
        $nextMessage.text(e.data);
        $chatLog.append($nextMessage);
    });
    socket.addEventListener('open',function() {
        var guid = getId();
        socket.send(JSON.stringify(['login', guid]));
    });

}
createWebSocket();



var $chatSend = $('#chatsend');
var $chatInput = $('#chatinput');
var $chatLog = $('#chatlog');

function sendMessage(message){
    socket.send(JSON.stringify(['message', message]));
    var $nextMessage = $('<div/>');
    $nextMessage.text(message);
    $chatLog.append($nextMessage);
}

function processMessageSubmit(){
    var message = $chatInput.val();

    sendMessage(message);
    $chatInput.val('');
}


$chatSend.on('click', processMessageSubmit);
$chatInput.on('keydown', function (event){
    if (event.which == 13 || event.keyCode == 13) {
        event.preventDefault();
        processMessageSubmit();
        return false;
    }
    return true;
});
