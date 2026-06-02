const express = require("express");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({ message: "Hello from Express!", version: "1.0.0" });
});

app.get("/api/items", (req, res) => {
  res.json([
    { id: 1, name: "Item A" },
    { id: 2, name: "Item B" },
  ]);
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
