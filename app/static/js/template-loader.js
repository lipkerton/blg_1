class TempateLoader {
    constructor() {
        this.templates = new Map();
    }

    async loadTemplate(name, path) {
        try {
            const response = await fetch(path);
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const template = doc.getElementById(name)

            if (!template) {
                throw new Error(`template "${name} not found in ${path}"`);
            }
            this.templates.set(name, template);
            return template;
        } catch(error) {
            console.error(`Failed to load template "${name}":`, error);
            throw error;
        }

    }
    getTemplate(name) {
        const template = this.templates.get(name);
        if (!template) {
            throw new Error(`template "${name}" not loaded `)
        }
        return template.content.cloneNode(true);
    }
}
export const templateLoader = new TempateLoader();