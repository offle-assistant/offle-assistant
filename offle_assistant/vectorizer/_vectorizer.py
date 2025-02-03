from ._sentence_transformer import SentenceTransformerVectorizer
# This will eventually be a parent class for vectorizer


"""
    This table is used to get the correct vectorizer from a string stored
    in the collection's metadata.
"""
vectorizer_table: dict = {
    "sentence-transformer": SentenceTransformerVectorizer
}
