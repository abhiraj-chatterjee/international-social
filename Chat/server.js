
// AUTHOR : Soham De
// Make a chat app prototype using web-sockets. A chatroom kinda thing works for now.
// No idea how any of this will work, but lets find out.  

const path = require('path');
const http = require('http');
const express = require('express');
const app = express();
const socketio = require('socket.io');
const formatMessage = require('./utils/messages')
const { userJoin, getCurrentUser, userLeave, getRoomUsers } = require('./utils/users')


const server = http.createServer(app);
const io = socketio(server);

// Set static folder
app.use(express.static(path.join(__dirname, 'public')));

// Run when client is connected
io.on('connection', socket =>{

	//console.log("New Web Socket connection established."); // Logs on server's console

	socket.on('joinRoom', ({username, room}) => {

		const user = userJoin(socket.id ,username, room);
		socket.join(user.room);

		// Welcome current user
		socket.emit('message', formatMessage("ForumBot", "Welcome to Student Forum!", "bot")); // emits from server to clien, catched in main.js by client

		// Broadcast when user emits
		socket.broadcast.to(user.room).emit('message', formatMessage("ForumBot", ` ${user.username} has joined chat`,"bot")); // emits to all clients except the current user

		// Send Users and Room info
		io.to(user.room).emit('roomUsers', {
			room : user.room,
			users : getRoomUsers(user.room)
		});

	});

	// Listen for chatMessage
	socket.on('chatMessage', (msg) => {
		//console.log(msg);
		const user = getCurrentUser(socket.id);

		// Emit back to all clients
		io.to(user.room).emit('message', formatMessage(user.username, msg, "outgoing"));
	});

	// Emit to everyone when user leaves room
	socket.on('disconnect', ()=>{
		const user = userLeave(socket.id);

		if (user){

			io.to(user.room).emit('message', formatMessage("ForumBot", `${user.username} has left the chat`, "bot"));
			
			// Send Users and Room info
			io.to(user.room).emit('roomUsers', {
			room : user.room,
			users : getRoomUsers(user.room)
		});
		}


	
	});

});

const PORT =  process.env.PORT || 3000; // search for a PORT env variable, or just use 3000 localhost
//app.listen(PORT, ()=> console.log(`Server running on PORT ${PORT}`)); // sets up the express server
server.listen(PORT, ()=> console.log(`Server running on PORT ${PORT}`));




