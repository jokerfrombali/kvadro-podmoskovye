#!/bin/bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
mkdir -p raw/competitors
for d in "$@"; do
  safe=$(echo "$d" | tr '.' '_')
  rb=$(curl -sL --max-time 20 -A "$UA" "https://$d/robots.txt")
  sm=$(echo "$rb" | grep -io 'sitemap:.*' | sed 's/[Ss]itemap:[[:space:]]*//' | tr -d '\r')
  if [ -z "$sm" ]; then sm="https://$d/sitemap.xml"; fi
  : > "raw/competitors/${safe}.urls"
  for s in $sm; do
    body=$(curl -sL --max-time 25 -A "$UA" "$s")
    # if sitemap index, expand one level
    subs=$(echo "$body" | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g')
    if echo "$body" | grep -qi '<sitemapindex'; then
      for sub in $subs; do
        curl -sL --max-time 25 -A "$UA" "$sub" | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g' >> "raw/competitors/${safe}.urls"
      done
    else
      echo "$subs" >> "raw/competitors/${safe}.urls"
    fi
  done
  sort -u "raw/competitors/${safe}.urls" -o "raw/competitors/${safe}.urls"
  printf '%-24s %s\n' "$d" "$(grep -c . "raw/competitors/${safe}.urls")"
done
