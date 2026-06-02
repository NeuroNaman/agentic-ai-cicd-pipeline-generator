const request = require("supertest");
const app = require("../src/index");

describe("GET /", () => {
  it("should return hello message", async () => {
    const res = await request(app).get("/");
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toBe("Hello from Express!");
  });
});

describe("GET /api/items", () => {
  it("should return items array", async () => {
    const res = await request(app).get("/api/items");
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveLength(2);
  });
});
