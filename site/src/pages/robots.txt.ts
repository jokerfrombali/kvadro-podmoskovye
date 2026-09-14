import type { APIRoute } from 'astro';
import { site } from '../data/site';
export const GET: APIRoute = ({ site: s }) => {
  const b = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');
  const host = ((s ?? new URL(site.domain)).origin) + b;
  return new Response(
`User-agent: *
Allow: /
Disallow: /cart/
Disallow: /checkout/
Disallow: /my-account/
Disallow: /search/
Disallow: /*?
Clean-param: utm_source&utm_medium&utm_campaign&utm_term&utm_content&yclid&gclid

Sitemap: ${host}/sitemap-index.xml
`, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
