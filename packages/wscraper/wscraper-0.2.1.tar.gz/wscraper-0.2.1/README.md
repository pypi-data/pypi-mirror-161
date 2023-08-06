# Wikipedia Scraper

Parsing, tokenizing text using a Wikipedia dump XML file.

## Author

- Name: T.Furukawa
- Email: tfurukawa.mail@gmail.com

## Installation

```shell
pip install wscraper
```

## Support

### language

- japanese
  - Japanese Wikipedia
- english
  - English Wikipedia

## How to Work (Command)

### Check Console Commands

Please run this command.

```shell
wscraper --help
```

Executable commands to be listed.

### Initialize

For start, you have to execute this command.  
It creates necessary directory and files.

```shell
wscraper initialize
```

wscraper root directory is created at `$HOME/.wscraper`.  
If you change this path, please set environment `WSCRAPER_ROOT`.

### Set Global Parameters

```shell
wscraper root set --language japanese --page_chunk 1000
```

- `language`
  - Default language. If you do not set the parameter `language` for each corpus, this default language is used.
- `page_chunk`
  - A Wikipedia dump XML file has large text data as many pages. For analysis, it is separated to several small files because of memory efficiency.

See `wscraper root set -h`

### Import a Wikipedia XML File

A file wikipedia.xml assumes like `(lang)wiki-(date)-pages-articles-multistream.xml`

```shell
wscraper import /path/to/sample.xml
wscraper import /path/to/wikipedia.xml --name my_wp
```

See `wscraper import -h`.

### Check Wikipedia Resources

It can check Wikipedia corpus resources.

```shell
wscraper list
```

output
```text
Available wikipedia:
  - sample
  - my_wp
```

### Switch Current Corpus

```shell
wscraper switch my_wp
```

### Check the Status of Current Corpus

```shell
wscraper status
```

output
```text
current: my_wp

language [default]: japanese
```

### Set Parameters for Current Corpus

Required parameters should be set for current corpus.

```shell
wscraper set --language english
```

parameters:
- `language`

### Unset Parameters

You can delete parameters by running following command.

```shell
wscraper unset --language
```

### Rename a Corpus Name

You can rename a corpus name from `$source` to `$target`.

```shell
wscraper rename $source $target
```

### Delete a Corpus

When a corpus (example: `$target`) is unnecessary, it can be removed.

```shell
wscraper delete $target
```

## How to Work (Python)

Importing iterator classes.

```python
from wscraper.analysis import *
```

You can iterate pages of a corpus by writing this.

```python
# entry
entry_iterator = EntryIterator()
# You can specify corpus name and language.
# If parameter is not given, current Wikipedia corpus is used.
# >>> EntryIterator(name = "sample", language = "japanese")
both_iterator = BothIterator()
redirection_iterator = RedirectionIterator()

for i, b in enumerate(both_iterator):
    print(f"both: {i}: {type(b)}")

for i, e in enumerate(entry_iterator):
    print(f"entry {i}: {e.title} {len(e.mediawiki)}")

for i, r in enumerate(redirection_iterator):
    print(f"redirection: {i}: {r.source} -> {r.target}")
```

For example, you can give iterator a ML model.

```python
def to_words(x):
    return x.split()

# return word list for each iteration
iterator = ArticleIterator(tagger = to_words)
# If you set `type = dict`, you can get records as dictionary
# ex: { "title", "ABC...", "article": "eval(to_words(article))" }

# Iterators:
#   ArticleIterator
#     - 1 page / record
#     - dict keys: ["title", "article"]
#   ParagraphIterator:
#     - N page / record
#     - Description like "== A ==" is delimiter of paragraphs.
#     - dict keys: ["page_title", "paragraph_title", "paragraph"]

# For example, gensim word2vec can interpret this iterator

# from gensim.models.word2vec import Word2Vec
Word2Vec(iterator)

# You can concatenate iterators to train ML model using CombinedIterator.
Word2Vec(CombinedIterator(iterator, another_iterator))
```


## License

The source code is licensed MIT.

Please check the file LICENSE.
