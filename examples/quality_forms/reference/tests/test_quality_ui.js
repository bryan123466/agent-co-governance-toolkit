"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
require("../web/app.js");
const { validateRecord } = globalThis.QualityForm;
let checks = 0;

for (const [filename, expectedValid] of [["valid.json", true], ["invalid.json", false]]) {
  const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, "../samples", filename), "utf8"));
  for (const sample of fixture.cases) {
    assert.equal(validateRecord(sample.record).length === 0, expectedValid, sample.name);
    checks += 1;
  }
}

const base = {
  id: "SYNTHETIC-UI-REGRESSION", date: "2026-10-22", area: "Fictional workshop",
  severity: "minor", description: "Generated field-contract test", owner: "Demo operator", status: "open",
};
for (const status of ["open", "investigating", "resolved", "closed"]) {
  const record = { ...base, status, resolution: "Synthetic correction", reviewer: "Demo reviewer", extra_note: "Unexpected field" };
  const before = JSON.stringify(record);
  const errors = validateRecord(record);
  assert.ok(errors.some((error) => error.field === "extra_note" && /unknown/i.test(error.message)), `Unknown field must be rejected for ${status}`);
  assert.equal(JSON.stringify(record), before, "Validation must not alter input data");
  checks += 1;
}
const multiple = validateRecord({ ...base, z_extra: "z", a_extra: "a" });
assert.deepEqual(multiple.map((error) => error.field), ["a_extra", "z_extra"], "Unknown field errors have deterministic ordering");
checks += 1;
const prototypeNamed = JSON.parse(JSON.stringify(base).replace(/}$/, ',"__proto__":{"polluted":true}}'));
assert.ok(validateRecord(prototypeNamed).some((error) => error.field === "__proto__"));
assert.equal({}.polluted, undefined);
checks += 1;
assert.deepEqual(validateRecord({ ...base, resolution: "", reviewer: "" }), [], "Known optional text fields remain valid for open records");
checks += 1;
console.log(JSON.stringify({ checks, passed: checks, fixture: "synthetic quality UI" }));
