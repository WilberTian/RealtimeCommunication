var app = require("express")();
var http = require("http").Server(app);
var io = require("socket.io")(http);

// get the static files
app.get("/", function(req, res){
    res.sendFile(__dirname + "/index.html");
});

app.get("/static/jquery-1.11.3.js", function(req, res){
    res.sendFile(__dirname + "/static/jquery-1.11.3.js");
});

app.get("/static/json2.js", function(req, res){
    res.sendFile(__dirname + "/static/json2.js");
});

app.get("/static/style.css", function(req, res){
    res.sendFile(__dirname + "/static/style.css");
});


// save all the client {"sid": socket.id, "clientName": client}
var clients = []

io.on("connection", function(socket){

    socket.on("add_client", function(client){
        console.log(client+" jion the chat");
        
        var clientObj = {};
        clientObj["sid"] = socket.id;
        clientObj["clientName"] = client;
        
        clients.push(clientObj);
        io.emit("user_status", clients)
    });
    
    socket.on("new_message", function(msg){
        console.log("Server got message: "+msg);
        console.log("Send message using: "+socket.conn.transport.name);
        io.emit("new_message", msg);
    });
      
    socket.on("disconnect", function(){
        for(var i = 0; i<clients.length; i++){
            if(clients[i]["sid"] == socket.id){
                console.log(clients[i]["clientName"]+" leave the chat");
                clients.splice(i, 1);
                break;
            }
        }
        io.emit("user_status", clients);
    });
  
});

http.listen(8080, function(){
    console.log("listening on *:8080");
});
