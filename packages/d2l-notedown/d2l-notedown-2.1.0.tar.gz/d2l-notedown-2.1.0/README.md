This is a fork of [notedown](https://github.com/aaren/notedown) with the
following two changes

1. Don't force hard breaks for long lines. Such breaks will add additional
   spaces that are not suitable for some languages such as Chinese
1. In default use strict match instead of fenced, so we can write some other
   code blocks (e.g. bash) and notedown will not put it as python code blocks.

Since these two modifications change the default behavior, so I make a fork
instead of merging back.
