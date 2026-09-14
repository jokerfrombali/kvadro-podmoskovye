import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://jokerfrombali.github.io',
  base: '/kvadro-podmoskovye',
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  integrations: [
    sitemap({
      changefreq: 'weekly',
      lastmod: new Date(),
      serialize(item) {
        if (item.url.endsWith('/')) {
          const depth = new URL(item.url).pathname.split('/').filter(Boolean).length;
          item.priority = depth === 0 ? 1.0 : depth === 1 ? 0.9 : depth === 2 ? 0.8 : 0.6;
        }
        return item;
      },
    }),
  ],
  compressHTML: true,
});
