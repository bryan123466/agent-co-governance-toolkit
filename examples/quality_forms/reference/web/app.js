"use strict";

(() => {
  const required = ["id", "date", "area", "severity", "description", "owner", "status"];
  const fields = [...required, "resolution", "reviewer"];
  const statuses = new Set(["open", "investigating", "resolved", "closed"]);
  const severities = new Set(["minor", "major", "critical"]);
  const present = (value) => typeof value === "string" && value.trim().length > 0;

  function validDate(value) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const [year, month, day] = value.split("-").map(Number);
    if (year < 1 || month < 1 || month > 12 || day < 1 || day > 31) return false;
    const calendar = new Date(0);
    calendar.setUTCHours(0, 0, 0, 0);
    calendar.setUTCFullYear(year, month - 1, day);
    return calendar.getUTCFullYear() === year && calendar.getUTCMonth() === month - 1 && calendar.getUTCDate() === day;
  }

  function validateRecord(record) {
    if (record === null || typeof record !== "object" || Array.isArray(record)) {
      return [{ field: "record", message: "Record must be an object." }];
    }
    const errors = [];
    required.forEach((field) => {
      if (!present(record[field])) errors.push({ field, message: `${field} is required and must contain text.` });
    });
    if (present(record.date) && !validDate(record.date)) errors.push({ field: "date", message: "date must be a real calendar date in YYYY-MM-DD format." });
    if (present(record.severity) && !severities.has(record.severity)) errors.push({ field: "severity", message: "severity must be minor, major, or critical." });
    if (present(record.status) && !statuses.has(record.status)) errors.push({ field: "status", message: "status must be open, investigating, resolved, or closed." });
    ["resolution", "reviewer"].forEach((field) => {
      if (record[field] !== undefined && typeof record[field] !== "string") errors.push({ field, message: `${field} must be text when supplied.` });
    });
    Object.keys(record).sort().forEach((field) => {
      if (!fields.includes(field)) errors.push({ field, message: `Unknown field: ${field}.` });
    });
    if (["resolved", "closed"].includes(record.status) && !present(record.resolution)) errors.push({ field: "resolution", message: `${record.status} records require a resolution.` });
    if (record.status === "closed" && !present(record.reviewer)) errors.push({ field: "reviewer", message: "closed records require a reviewer." });
    return errors;
  }

  globalThis.QualityForm = Object.freeze({ validateRecord, validDate });
  if (typeof document === "undefined") return;
  const form = document.getElementById("quality-form");
  const errorBox = document.getElementById("errors");
  const preview = document.getElementById("record-preview");
  const feedback = document.getElementById("feedback");

  function clearFeedback() {
    errorBox.replaceChildren();
    errorBox.hidden = true;
    fields.forEach((field) => form.elements.namedItem(field).removeAttribute("aria-invalid"));
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearFeedback();
    const record = Object.fromEntries(fields.map((field) => [field, form.elements.namedItem(field).value.trim()]));
    const errors = validateRecord(record);
    if (errors.length) {
      const heading = document.createElement("strong");
      heading.textContent = "Please correct the following fields:";
      const list = document.createElement("ul");
      errors.forEach((error) => {
        const item = document.createElement("li");
        item.textContent = error.message;
        list.append(item);
        const input = form.elements.namedItem(error.field);
        if (input) input.setAttribute("aria-invalid", "true");
      });
      errorBox.append(heading, list);
      errorBox.hidden = false;
      preview.textContent = "{}";
      feedback.textContent = `Validation failed: ${errors.length} issue${errors.length === 1 ? "" : "s"}. No valid preview is retained.`;
      errorBox.focus();
      return;
    }
    preview.textContent = JSON.stringify(record, null, 2);
    feedback.textContent = "Form fields are valid. This preview has not been saved or approved.";
  });

  form.addEventListener("reset", () => {
    clearFeedback();
    preview.textContent = "{}";
    feedback.textContent = "Form cleared. No record has been validated.";
  });
})();
