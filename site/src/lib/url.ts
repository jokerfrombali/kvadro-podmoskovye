/** Базовый путь сборки. На GitHub Pages сайт живёт в подпапке /<repo>/,
 *  на своём домене — в корне. Один helper закрывает оба случая. */
const RAW = import.meta.env.BASE_URL || '/';
export const BASE = RAW.endsWith('/') ? RAW.slice(0, -1) : RAW;
/** Абсолютный путь внутри сайта с учётом базового пути. */
export const u = (p: string): string => {
  if (!p) return BASE + '/';
  if (/^(https?:|mailto:|tel:|#)/.test(p)) return p;
  return BASE + (p.startsWith('/') ? p : '/' + p);
};
