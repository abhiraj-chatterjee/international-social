const users = [];

// Join user to chat
function userJoin(id, username, room){
	const user = {id, username, room};
	users.push(user); // Adds new user to list of users in chat
	return user;
};

// Get Current User
function getCurrentUser(id){
	return users.find(user => user.id == id);
};

// Get Users in Room
function getRoomUsers(room){
	return users.filter(user => user.room == room);
};

// User leaves Room
function userLeave(id){
	const index = users.findIndex(user => user.id == id);

	if (index != -1){
		return users.splice(index, 1)[0]; // just return the user that is leaving
	}
};

module.exports = {
	userJoin,
	getCurrentUser,
	userLeave,
	getRoomUsers
}