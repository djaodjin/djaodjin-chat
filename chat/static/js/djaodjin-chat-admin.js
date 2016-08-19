
var chatApi = new ChatApi();
chatApi.on('connect', function(){
    chatApi.whoami();
    chatApi.subscribe_active();
    chatApi.subscribe_claims();
});
var $root = $('#root');

var $messages = $('#messages');

function displayMessage(message){
    var $message = $('<div/>');
    $message.text((message.from || 'anonymous') + (message.t ? '('+message.t+')': '' )+ ': '+  message.text);
    $messages.append($message);

}

var myId = null;
var $chat_title = $('#chat_title');
var $chat_claim = $('#chat_claim');
var currentActive = null;
function setChatWindow(active){
    

    currentActive = active;
    $chat_title.text(active);
    var claimText;
    if ( claims[active]){
        if ( claims[active] == myId ){
            claimText  = 'you';
        }else{
            claimText = claim[active];
        }
    }else{
        claimText = '';
    }
    $chat_claim.text(claimText);
    chatApi.subscribe_to( active );

    $messages.empty();

    chatApi.get_messages(active);
}

var $claim_button = $('#claim');
$claim_button.on('click', function(){
    chatApi.add_claim(currentActive)
});
var $unclaim_button = $('#unclaim');
$unclaim_button.on('click', function(){
    chatApi.remove_claim(currentActive)
});

chatApi.on('message_from', function(message){
    if ( !active_set[message.from] || message.from == currentActive ){
        displayMessage(message);
    }
});

chatApi.on('get_messages_reply', function(reply){
    messages = reply['messages'];
    for (var i = messages.length-1; i >= 0; i --){
        m = messages[i];
        displayMessage(m);
    }
})

chatApi.on('youare', function(id){
    myId = id;
    updateActive();
});

var claims = {};
chatApi.on('claimed', function(new_claims){
    for ( var k in new_claims){
        claims[k] = new_claims[k];
    }
    updateActive();
});
chatApi.on('unclaimed', function(new_claims){
    for ( var k in new_claims){
        delete claims[k];
    }
    updateActive();
});

var $active_list = $('#active_list');
var active_set = {};
function updateActive(){
    $active_list.empty();
    for ( active in active_set){
        var $member_container = $('<div/>');
        var $member = $('<span/>');
        $member.css({
            'cursor': 'pointer',
            'color': 'blue',
            'text-decoration': 'underline'
        });
        $member.on('click', function(active){
            setChatWindow(active);
        }.bind(null, active));
        $member.text(active);
        
        $member_container.append($member);

        if ( claims[active] ){
            
            var $claim = $('<span/>');
            var claimText;
            if ( claims[active] == myId ){
                claimText = 'you';
            }else{
                claimText = claims[active];
            }
            $claim.text(claimText);
            $member_container.append(document.createTextNode(' '));
            $member_container.append($claim);
        }

        $active_list.append($member_container);
    }
    
}
chatApi.on('became_active', function(new_active){
    for ( var i =0 ; i < new_active.length; i ++){
        active_set[new_active[i]] = true;
    }
    updateActive();
});

chatApi.on('became_inactive', function(new_active){
    for ( var i =0 ; i < new_active.length; i ++){
        delete active_set[new_active[i]];
    }
    updateActive();
});

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



var $message = $('#message');
var $to = $('#to');

$('#message').on('keydown', function (event){
    if (currentActive && (event.which == 13 || event.keyCode == 13)) {
        event.preventDefault();

        var messageText = $message.val();
        $message.val('');
        chatApi.send_to(currentActive, messageText);

        return false;
    }
    return true;
});

var $thread = $('#thread');
var $subscribe = $('#subscribe');

$subscribe.on('click', function(){
    chatApi.subscribe_to( $thread.val())
});

var $getActive = $('#getActive');
$getActive.on('click', function(){

    chatApi.subscribe_active();

});
