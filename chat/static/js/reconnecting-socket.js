function ReconnectingSocket(url){
    this.attempts = 1;
    this.url = url
    this.handlers = [];

    this.connect();
}

ReconnectingSocket.prototype.generateInterval = function (k) {
    return Math.min(5, (Math.pow(2, k) - 1)) * 1000;
}


ReconnectingSocket.prototype.connect = function(){

    var self = this;
    
    this.socket = new WebSocket(this.url);

    this.socket.addEventListener('open',function () {
        // reset the tries back to 1 since we have a new this.socket opened.
        self.attempts = 1; 
    });
    
    this.socket.addEventListener('close', function () {
        var time = self.generateInterval(self.attempts);
        
        setTimeout(function () {
            // We've tried to reconnect so increment the this.attempts by 1
            self.attempts++;
            
            self.connect();
        }, time);
    });

    for( var i = 0; i < this.handlers.length; i ++){
        var event = this.handlers[i][0];
        var handler = this.handlers[i][1];
        this.socket.addEventListener(event, handler);
    }

}

ReconnectingSocket.prototype.addEventListener = function(event, handler){
    
    this.handlers.push([event,handler]);
    this.socket.addEventListener(event, handler);
}

ReconnectingSocket.prototype.send = function(msg){
    this.socket.send(msg);
}
