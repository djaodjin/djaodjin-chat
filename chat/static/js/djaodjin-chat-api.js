function ChatApi(){
    this.base = '/chat-api';
    this.handlers = {};
    this.watchDogTimeout = 9000;

    this.socket = new ReconnectingSocket("ws://" + window.location.host + "/chat/");

    var self = this;
    this.socket.addEventListener('message', function (e){
        console.log(e.data);
        
        
        var decoded = JSON.parse(e.data);
        var event = decoded[0];
        var args = [];
        for ( var i = 1; i < decoded.length; i ++){
            args.push(decoded[i]);
        }
        self._broadcast(event, args);
    });

    this.on('connect', function(){
        this.runWatchDog();
    }.bind(this));

}

ChatApi.prototype.runWatchDog = function(){
    this._apiCall('/ping', []);
    this.scheduleWatchDog();
}

ChatApi.prototype.scheduleWatchDog = function(){
    if (this.watchDogHandle){
        clearTimeout(this.watchDogHandle);
    }
    this.watchDogHandle = setTimeout(this.runWatchDog.bind(this), this.watchDogTimeout);
}

ChatApi.prototype._broadcast = function(event, args){
    if ( this.handlers[event] ){
        for ( var i = 0; i < this.handlers[event].length;i ++){
            this.handlers[event][i].apply(null, args);
        }
    }
}



ChatApi.prototype._apiCall = function(endpoint, args){
    
    var full_endpoint = this.base + endpoint;
    var message = [full_endpoint].concat(args);

    this.socket.send(JSON.stringify(message));
}

ChatApi.prototype.whoami = function(){
    this._apiCall('/whoami', []);
}
ChatApi.prototype.send = function(text){
    this._apiCall('/send', [ text ]);
}
ChatApi.prototype.subscribe = function(){
    this._apiCall('/subscribe', []);
}
ChatApi.prototype.subscribe_active = function(){
    this._apiCall('/subscribe_active', []);
}
ChatApi.prototype.subscribe_claims = function(){
    this._apiCall('/subscribe_claims', []);
}

// ChatApi.prototype.list_recent = function(){
//     this._apiCall('/list_recent', []);
// }
ChatApi.prototype.subscribe_to = function(thread_id){
    this._apiCall('/subscribe_to', [ thread_id ]);
}
ChatApi.prototype.unsubscribe_to = function(thread_id){
    this._apiCall('/unsubscribe_to', [ thread_id ]);
}
ChatApi.prototype.add_claim = function(thread_id, claimer){
    this._apiCall('/add_claim', [ thread_id, claimer ]);
}
ChatApi.prototype.remove_claim = function(thread_id, claimer){
    this._apiCall('/remove_claim', [ thread_id, claimer ]);
}
// ChatApi.prototype.set_claims = function(thread_id, claimers){
//     this._apiCall('/set_claims', [ thread_id, claimers ]);
// }
ChatApi.prototype.send_to = function(thread_id, text){
    this._apiCall('/send_to', [ thread_id, text ]);
}
ChatApi.prototype.get_messages = function(thread_id, cursor){
    this._apiCall('/get_messages', [ thread_id, cursor ]);
}

ChatApi.prototype.on = function(event, f){

    if (event == 'connect'){
        this.socket.addEventListener('open', f);
    }else{

        if (!this.handlers[event]){
            this.handlers[event] = [];
        }
        
        this.handlers[event].push(f);
    }
}
