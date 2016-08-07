// Note that the path doesn't matter for routing; any WebSocket
// connection gets bumped over to WebSocket consumers

var $root = $('#root');

var threadRoots ={};
function displayMessage(message){
    var $threadRoot;
    if (threadRoots[message.thread]){
        $threadRoot = threadRoots[message.thread]
    }else{
        $threadRoot = $('<div/>');
        threadRoots[message.thread] = $threadRoot;

        $threadRoot.messages = $('<div/>');
        $threadRoot.append($threadRoot.messages);

        $threadRoot.input = $('<input/>');
        $threadRoot.append($threadRoot.input);

        $threadRoot.append($('<hr/>'));

        $threadRoot.input.on('keydown', function (event){
            if (event.which == 13 || event.keyCode == 13) {
                event.preventDefault();
                var messageText = $threadRoot.input.val();
                $threadRoot.input.val('');
                displayMessage({
                    'text': messageText,
                    'thread': message.thread,
                    't': new Date().toString(),
                    'from': 'me'
                })
                
                socket.send(JSON.stringify(['message_admin', message.thread, messageText]));
                return false;
            }
            return true;
        });


        $root.append($threadRoot);

    }

    var $message = $('<div/>');
    $message.text((message.from || 'anonymous') + ': '+  message.text);
    

    $threadRoot.messages.append($message);

}

function handleMessage(m){

    var parsed;
    try{
        var parsed = JSON.parse(m);
    }catch(e){
        parsed = null;
    }
    console.log(parsed);

    if (parsed){
        var command = parsed[0];

        if (command == 'broadcastmessage' ){
            var message = parsed[1];
            
            displayMessage(message);
        }
    }
}


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
    socket = new WebSocket("ws://" + window.location.host + "/chat-admin/");

    socket.addEventListener('open',function () {
        // reset the tries back to 1 since we have a new socket opened.
        attempts = 1; 

        var guid = getId();
        socket.send(JSON.stringify(['login', guid]));


        // ...Your app's logic...
    });
    
    socket.addEventListener('close', function () {
        var time = generateInterval(attempts);
        
        setTimeout(function () {
            // We've tried to reconnect so increment the attempts by 1
            attempts++;
            
            // Socket has closed so try to reconnect every 10 seconds.
            createWebSocket(); 
        }, time);
    });

    socket.addEventListener('message',function(e) {
        console.log(e);
        var $nextMessage = $('<div/>');
        // $nextMessage.text(e.data);
        // $chatLog.append($nextMessage);
        console.log(e.data);
        handleMessage(e.data)
        
    });
    socket.addEventListener('open',function() {
        var guid = 'asdf';
        socket.send(JSON.stringify(['login', guid]));
        socket.send(JSON.stringify(['get_recent']));
    });

}
createWebSocket();





// <div id="chatlog">
// </div>
// <div>
//   <input id="chatto" type="text" value="asdf"></input>
// </div>
// <div>
//   <input id="chatinput" type="text"></input>
// </div>
// <div>
//   <button id="chatsend">Send</button>
// </div>


