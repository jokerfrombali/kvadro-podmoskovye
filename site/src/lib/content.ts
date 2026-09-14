/** Тексты страниц: src/content/articles/{id}.md и src/content/pages/{id}.md */
const ART = import.meta.glob('../content/articles/*.md', { eager: true }) as Record<string, any>;
const PGS = import.meta.glob('../content/pages/*.md', { eager: true }) as Record<string, any>;
const idOf = (p: string) => p.split('/').pop()!.replace(/\.md$/, '');
const map = (o: Record<string, any>) =>
  Object.fromEntries(Object.entries(o).map(([k, v]) => [idOf(k), v]));
export const ARTICLE_MD = map(ART);
export const PAGE_MD = map(PGS);
export const hasArticle = (id: string) => id in ARTICLE_MD;
export const hasPage = (id: string) => id in PAGE_MD;
/** Доля готовых текстов — для отчёта */
export const stats = () => ({ articles: Object.keys(ARTICLE_MD).length, pages: Object.keys(PAGE_MD).length });
