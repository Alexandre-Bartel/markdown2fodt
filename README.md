# markdown2fodt
Markdown to FODT (Flat XML Open Document)

Code conçu en suivant la méthodologie de La RACHE (http://www.la-rache.com/) 
pour faciliter l'écriture collaborative d'articles dans MISCMAG (https://www.miscmag.com/).

# Dépendances

```
# apt-get install pandoc python3-pandocfilters
```

# Utilisation

```
$ bash /path/to/md2fodt.sh /path/to/article.txt
```

# Exemple

```
$ bash md2fodt.sh ./test/article.txt
$ libreoffice ./test/article.txt.fodt
```
