const users = [
    {
        id: 1,
        email: "demo@example.com",
        passwordHash: "$2b$10$exampleHashValue"
    }
];

async function findUserByEmail(email) {
    return users.find((user) => user.email === email);
}

module.exports = {
    findUserByEmail
};