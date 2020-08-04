
// AUTHOR : Soham De
// Make a chat app prototype using web-sockets. A chatroom kinda thing works for now.
// No idea how any of this will work, but lets find out.  

const chatForm = document.getElementById('chat-form');
const socket = io();
const chatMessages = document.getElementById('chat-messages');
const roomName = document.getElementById('room-name');
const userList = document.getElementById('users');


// Get username and room from URL using QsCDN
const { username, room } = Qs.parse(location.search, {
	ignoreQueryPrefix : true
});

// console.log(username, room);

// Join Chatroom
socket.emit('joinRoom', {username, room});

// Get Room and Users info
socket.on('roomUsers', ({ room, users }) => {
	outputRoomName(room);
	outputUsers(users);
});

// Message from server
socket.on('message', message =>{ // catches message emmitted by server through a web socket
	console.log(message);
	outputMessage(message);

	// Scroll down to current message automatically
	chatMessages.scrollTop = chatMessages.scrollHeight;

});

// Event listener for chat-form submit
chatForm.addEventListener('submit', (e) => {
	e.preventDefault();

	// Get message from form
	const msg = e.target.elements.msg.value;
	//console.log(msg);

	// Emit message from client to server
	socket.emit('chatMessage', msg);

	// Clear input
	e.target.elements.msg.value = "";
	e.target.elements.msg.focus();

});

// DOM functions:

// Output message into DOM

function outputMessage(message){
	const div = document.createElement('div');
	var type = "";
	if (message.username == "ForumBot"){
		type = "bot";
	}
	else if (message.username == username){
		type = "outgoing";
	}
	else{
		type = "incoming";
	}
	div.classList.add('message');
	//console.log(type);
	div.classList.add(type);
	div.innerHTML = `<p class="meta"> ${message.username} <span> ${message.time} </span></p>
            <p class="text">
              ${message.text}
            </p>`;
    chatMessages.appendChild(div);

}

// Output Room name into DOM

function outputRoomName(room){
	roomName.innerText = room;
}

// Update Users List into DOM

function outputUsers(users){
	userList.innerHTML = `${users.map(user => `<li>${user.username}</li>`).join('')}`;

}