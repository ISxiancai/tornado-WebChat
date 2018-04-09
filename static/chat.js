

$(document).ready(function() {


    $("#messageform").bind("submit", function() {
        newMessage($(this));
        return false;
    });
    $("#messageform").bind("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });
    //$("#message").select();
    updater.start();
});

function newMessage(form) {
    var message = form.formToDict();
    //stringify  js中将 js值转为 json 格式
    updater.socket.send(JSON.stringify(message));
    //form.find("input[type=text]").val().select();
}

jQuery.fn.formToDict = function() {
    //serializeArray 通过 序列化form 表单的值 返回 json 数据格式
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

function add(id,txt) {    
    var ul=$('#user_list');    
    var li= document.createElement("li");    
    li.innerHTML=txt;  
    li.id=id;  
    ul.append(li);    
} 

function del(id){
    $('#'+id).remove();
}

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/chatsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            // console.log(event)
            // console.log(event.data)
            updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
	del(message.client_id);
        if (message.type!="offline"){
	    add(message.client_id, message.username);
	if (message.body=="") return;
        // var existing = $("#m" + message.id);
        // console.log(existing)
        // console.log(existing.length)
        //if (existing.length > 0) return;
        var node = $(message.html);
        node.hide();
        $("#inbox").append(node);
        node.slideDown();
        }
    }
};
