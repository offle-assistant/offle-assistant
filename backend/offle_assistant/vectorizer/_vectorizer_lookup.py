from ._sentence_transformer import SentenceTransformerVectorizer


"""
    This table is used to get the correct vectorizer from a string stored
    in the collection's metadata.
"""
vectorizer_lookup_table: dict = {
    "sentence-transformer": SentenceTransformerVectorizer
}
