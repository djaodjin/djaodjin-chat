// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers

var chatApi = new ChatApi();
chatApi.on('connect', function(){
    chatApi.subscribe();
});

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


var $chatSend = $('#chatsend');
var $chatInput = $('#chatinput');
var $chatLog = $('#chatlog');

chatApi.on('message', function(message){
    var $message = $('<div/>');
    $message.text(message);
    $chatLog.append($message);
});


function sendMessage(message){
    // var $nextMessage = $('<div/>');
    // $nextMessage.text(message);
    // $chatLog.append($nextMessage);
}

function processMessageSubmit(){
    var message = $chatInput.val();

    chatApi.send(message)
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
