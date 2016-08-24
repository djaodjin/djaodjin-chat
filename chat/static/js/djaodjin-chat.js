// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers

var chatApi = new ChatApi();
chatApi.on('connect', function(){
    chatApi.subscribe();
});

var $chatSend = $('#chatsend');
var $chatInput = $('#chatinput');
var $chatLog = $('#chatlog');

chatApi.on('message_from', function(message){
    var $message = $('<div/>');
    $message.text(message.from + ': ' + message.text);

    $chatLog.append($message);
});
chatApi.on('message', function(message){
    var $message = $('<div/>');
    $message.text('me: ' + message);

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
