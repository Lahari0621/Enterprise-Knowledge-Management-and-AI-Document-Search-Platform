import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank(q, docs):
    if not docs:
        return []

    query = q.strip().lower()

    if not query:
        return []

    # -----------------------------------------
    # Build document text
    # -----------------------------------------
    corpus = []

    for d in docs:
        title = d.title or ""
        content = d.content or ""

        corpus.append(
            title + " " + content
        )

    # -----------------------------------------
    # TF-IDF similarity
    # -----------------------------------------
    try:
        vectorizer = TfidfVectorizer(
            stop_words=None
        )

        matrix = vectorizer.fit_transform(
            corpus + [query]
        )

        tfidf_scores = cosine_similarity(
            matrix[-1],
            matrix[:-1]
        ).flatten()

    except ValueError:
        tfidf_scores = [0.0] * len(docs)

    results = []

    query_words = set(
        re.findall(r'\b\w+\b', query)
    )

    # -----------------------------------------
    # Calculate improved relevance
    # -----------------------------------------
    for i, d in enumerate(docs):

        title = (d.title or "").lower()
        filename = (d.filename or "").lower()
        content = (d.content or "").lower()

        score = float(tfidf_scores[i])

        # -------------------------------------
        # Exact title match
        # -------------------------------------
        if query == title:
            score = max(score, 0.95)

        # -------------------------------------
        # Query appears inside title
        # -------------------------------------
        elif query in title:
            score = max(score, 0.85)

        # -------------------------------------
        # Query appears in filename
        # -------------------------------------
        if query in filename:
            score = max(score, 0.90)

        # -------------------------------------
        # Exact phrase appears in content
        # -------------------------------------
        if query in content:
            score = max(score, 0.80)

        # -------------------------------------
        # Individual word matching
        # -------------------------------------
        content_words = set(
            re.findall(r'\b\w+\b', content)
        )

        all_document_words = (
            content_words |
            set(re.findall(r'\b\w+\b', title))
        )

        if query_words:
            matched_words = (
                query_words.intersection(
                    all_document_words
                )
            )

            word_ratio = (
                len(matched_words)
                / len(query_words)
            )

            score = max(
                score,
                word_ratio * 0.75
            )

        # Never allow score above 100%
        score = min(score, 1.0)

        results.append(
            (d, score)
        )

    # -----------------------------------------
    # Highest relevance first
    # -----------------------------------------
    results.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return results


rank_documents = rank