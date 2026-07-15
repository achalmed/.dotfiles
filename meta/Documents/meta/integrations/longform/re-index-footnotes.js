/**
 * re-index-footnotes.js — Paso de compilación de Longform.
 *
 * Renumera secuencialmente las notas al pie del manuscrito compilado
 * (definiciones `[^x]:` y llamadas `[^x]`), útil al unir escenas cuyas
 * notas al pie se numeraron por separado.
 *
 * Nombre de archivo fijo: Longform carga los pasos desde meta/longform
 * (userScriptFolder) — no renombrar.
 */
module.exports = {
	description: {
		name: "Re-Index Footnotes",
		description: "Renumera las notas al pie del manuscrito",
		availableKinds: ["Manuscript"],
		options: []
	},

	compile (input, context) {
		let text = input.contents;

		// Renumera las definiciones: [^x]: → [^1]:, [^2]:, …
		let indice = 0;
		text = text.replace(/^\[\^\S+?]: /gm, () => `[^${++indice}]: `);

		// Renumera las llamadas en el texto (excluye las definiciones,
		// que empiezan la línea). Truco de lookahead: https://stackoverflow.com/a/43232659
		indice = 0;
		text = text.replace(/(?!^)\[\^\S+?]/gm, () => `[^${++indice}]`);

		input.contents = text;
		return input;
	}
};
