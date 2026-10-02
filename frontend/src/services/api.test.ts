import { describe, expect, it } from "vitest";
import { ApiError } from "./api";

describe("ApiError", () => {
  it("stores status and detail properly", () => {
    const err = new ApiError(403, "Forbidden resource");
    expect(err).toBeInstanceOf(Error);
    expect(err.status).toBe(403);
    expect(err.detail).toBe("Forbidden resource");
    expect(err.message).toBe("Forbidden resource");
  });
});
