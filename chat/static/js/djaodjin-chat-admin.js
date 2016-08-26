(function ($) {
    "use strict";


    function DjChatAdmin(el, options){
        this.$root = $(el);
        this.options = options;
        this.init();

    }

    DjChatAdmin.prototype = {
        init: function(){
            var self = this;


            self.myId = null;
            self.currentActive = null;
            self.active_set = {};

            self.$chat_title = self.findPrefixed('chat_title');
            self.$chat_claim = self.findPrefixed('chat_claim');
            self.$messages = self.findPrefixed('messages');
            self.$active_list = self.findPrefixed('active_list');

            self.chatApi = new ChatApi();

            self.chatApi.on('connect', function(){
                self.chatApi.whoami();
                self.chatApi.subscribe_active();
                self.chatApi.subscribe_claims();
            });


            self.$claim_button = self.findPrefixed('claim');
            self.$claim_button.on('click', function(){
                self.chatApi.add_claim(self.currentActive)
            });
            self.$unclaim_button = self.findPrefixed('unclaim');
            self.$unclaim_button.on('click', function(){
                self.chatApi.remove_claim(self.currentActive)
            });

            self.chatApi.on('message_from', function(message){
                if ( !self.active_set[message.from] || message.from == self.currentActive ){
                    self.displayMessage(message);
                }
            });

            self.chatApi.on('get_messages_reply', function(reply){
                var messages = reply['messages'];
                for (var i = messages.length-1; i >= 0; i --){
                    var m = messages[i];
                    self.displayMessage(m);
                }
            })

            self.chatApi.on('youare', function(id){
                self.myId = id;
                self.updateActive();
            });


            self.claims = {};
            self.chatApi.on('claimed', function(new_claims){
                for ( var k in new_claims){
                    self.claims[k] = new_claims[k];
                }
                self.updateActive();
            });
            self.chatApi.on('unclaimed', function(new_claims){
                for ( var k in new_claims){
                    delete self.claims[k];
                }
                self.updateActive();
            });



            self.chatApi.on('became_active', function(new_active){
                for ( var i =0 ; i < new_active.length; i ++){
                    self.active_set[new_active[i]] = true;
                }
                self.updateActive();
            });

            self.chatApi.on('became_inactive', function(new_active){
                for ( var i =0 ; i < new_active.length; i ++){
                    delete active_set[new_active[i]];
                }
                self.updateActive();
            });


            self.$message = self.findPrefixed('message');
            self.$to = self.findPrefixed('to');

            self.$message.on('keydown', function (event){
                if (self.currentActive && (event.which == 13 || event.keyCode == 13)) {
                    event.preventDefault();

                    var messageText = self.$message.val();
                    self.$message.val('');
                    self.chatApi.send_to(self.currentActive, messageText);

                    return false;
                }
                return true;
            });


            self.$thread = self.findPrefixed('thread');
            self.$subscribe = self.findPrefixed('subscribe');

            self.$subscribe.on('click', function(){
                self.chatApi.subscribe_to( $thread.val())
            });

            self.$getActive = self.findPrefixed('getActive');
            self.$getActive.on('click', function(){

                self.chatApi.subscribe_active();

            });



        },
        setChatWindow: function(active){
            var self = this;

            self.currentActive = active;
            self.$chat_title.text(active);
            var claimText;
            if ( self.claims[active]){
                if ( self.claims[active] == self.myId ){
                    claimText  = 'you';
                }else{
                    claimText = claim[active];
                }
            }else{
                claimText = '';
            }
            self.$chat_claim.text(claimText);
            self.chatApi.subscribe_to( active );

            self.$messages.empty();

            self.chatApi.get_messages(active);

        },

        displayMessage: function(message){
            var self = this;

            var $message = $('<div/>');
            $message.text((message.from || 'anonymous') + (message.t ? '('+message.t+')': '' )+ ': '+  message.text);
            self.$messages.append($message);

        },
        updateActive: function(){
            var self = this;

            self.$active_list.empty();
            for ( var active in self.active_set){
                var $member_container = $('<div/>');
                var $member = $('<span/>');
                $member.css({
                    'cursor': 'pointer',
                    'color': 'blue',
                    'text-decoration': 'underline'
                });
                $member.on('click', function(active){
                    self.setChatWindow(active);
                }.bind(null, active));
                $member.text(active);

                $member_container.append($member);

                if ( self.claims[active] ){

                    var $claim = $('<span/>');
                    var claimText;
                    if ( self.claims[active] == self.myId ){
                        claimText = 'you';
                    }else{
                        claimText = self.claims[active];
                    }
                    $claim.text(claimText);
                    $member_container.append(document.createTextNode(' '));
                    $member_container.append($claim);
                }

                self.$active_list.append($member_container);
            }

        },
        findPrefixed: function(name){
            var self = this;

            var selector = '.' + this.options.cssPrefix + name;
            console.log(selector)
            console.log(this.$root);
            return this.$root.find(selector);
        }
    }

    $.fn.djchatadmin = function(options) {
        var opts = $.extend( {}, $.fn.djchatadmin.defaults, options );
        return new DjChatAdmin($(this), opts);
    };

    $.fn.djchatadmin.defaults = {
        cssPrefix: 'djaodjin-chat-',
    };
})(jQuery);
