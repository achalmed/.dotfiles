/**
 * workspace-load-work-with-notes.js — Macro de QuickAdd.
 * Carga el workspace "Work-with-notes" mediante Advanced URI.
 *
 * Nombre de archivo fijo: referenciado por QuickAdd — no renombrar.
 */
module.exports = async () => {
    window.open("obsidian://advanced-uri?workspace=Work-with-notes");
};
