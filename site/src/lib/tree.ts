import pages from '../data/pages.json';
import hubs from '../data/hubs.json';
import articles from '../data/articles.json';

export type Pg = (typeof pages)[number];
export const PAGES = pages as Pg[];
export const HUBS = hubs as any[];
export const ARTICLES = articles as any[];

export const byId = new Map(PAGES.map(p => [p.id, p]));
export const byUrl = new Map(PAGES.map(p => [p.url, p]));

export const childrenOf = (id: string) => PAGES.filter(p => p.parent === id);
export const articlesOf = (hubId: string) => ARTICLES.filter(a => a.hub === hubId);

export function crumbs(p: Pg) {
  const out: { t: string; u?: string }[] = [];
  let cur: Pg | undefined = p;
  const seen = new Set<string>();
  while (cur && cur.parent && cur.parent !== '—' && !seen.has(cur.id)) {
    seen.add(cur.id);
    const par = byId.get(cur.parent);
    if (!par || par.id === 'P001') break;
    out.unshift({ t: par.h1, u: par.url });
    cur = par;
  }
  out.push({ t: p.h1 });
  return out;
}

/** Соседние страницы того же родителя — для блока перелинковки */
export const siblingsOf = (p: Pg) => PAGES.filter(x => x.parent === p.parent && x.id !== p.id).slice(0, 8);

/** Статьи, релевантные коммерческой странице: по совпадению кластера в ключах */
export function relatedArticles(p: Pg, n = 4) {
  const words = new Set(
    (p.h1 + ' ' + p.description).toLowerCase().replace(/ё/g, 'е')
      .split(/[^а-яa-z0-9]+/).filter(w => w.length > 4)
  );
  return ARTICLES
    .map(a => {
      const t = (a.h1 + ' ' + a.primary).toLowerCase().replace(/ё/g, 'е');
      let s = 0; words.forEach(w => { if (t.includes(w)) s++; });
      return { a, s };
    })
    .filter(x => x.s > 0)
    .sort((x, y) => y.s - x.s || (y.a.freq - x.a.freq))
    .slice(0, n).map(x => x.a);
}
