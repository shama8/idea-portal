const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

app.use(express.json());
console.log("Serving static files from:", path.join(__dirname, '../frontend'));
app.use(express.static(path.join(__dirname, '../frontend')));

const dataFile = path.join(__dirname, 'data', 'ideas.json');

app.post('/submit', (req, res) => {
    const idea = req.body;
    let ideas = [];
    if (fs.existsSync(dataFile)) {
        ideas = JSON.parse(fs.readFileSync(dataFile));
    }
    ideas.push(idea);
    fs.writeFileSync(dataFile, JSON.stringify(ideas, null, 2));
    res.sendStatus(200);
});

app.get('/ideas', (req, res) => {
    let ideas = [];
    if (fs.existsSync(dataFile)) {
        ideas = JSON.parse(fs.readFileSync(dataFile));
    }
    res.json(ideas);
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
