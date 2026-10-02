import { describe, expect, it } from "vitest";
import { difficultyTone } from "./Badge";

describe("difficultyTone", () => {
  it("maps EASY to emerald", () => {
    expect(difficultyTone("EASY")).toBe("emerald");
  });

  it("maps MEDIUM to amber", () => {
    expect(difficultyTone("MEDIUM")).toBe("amber");
  });

  it("maps HARD to rose", () => {
    expect(difficultyTone("HARD")).toBe("rose");
  });

  it("maps EXPERT to insane", () => {
    expect(difficultyTone("EXPERT")).toBe("insane");
  });

  it("defaults unknown difficulty to slate", () => {
    expect(difficultyTone("UNKNOWN")).toBe("slate");
  });
});
