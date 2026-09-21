import { describe, expect, it } from "vitest";
import { formatDate, cn } from "./utils";

describe("workspace utilities", () => {
  it("formats persisted timestamps consistently", () => {
    expect(formatDate("2026-09-21T00:00:00.000Z")).toMatch(/2026/);
    expect(formatDate(null)).toBe("—");
  });
  it("merges utility classes", () => {
    expect(cn("rounded-lg", "rounded-xl")).toContain("rounded-xl");
  });
});
