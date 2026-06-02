import { useEffect, useState } from "react";

type Term = { term: string; plain: string };

export default function Glossary() {
  const [items, setItems] = useState<Term[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetch("/api/glossary")
      .then((r) => r.json())
      .then(setItems)
      .catch(() => setItems([]));
  }, []);

  const filtered = items.filter(
    (item) =>
      !query.trim() ||
      item.term.toLowerCase().includes(query.toLowerCase()) ||
      item.plain.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <section id="glossary" className="glossary-section">
      <div className="glossary-head">
        <p className="eyebrow">Plain language</p>
        <h2>Medical terms explained</h2>
        <p className="lead">Not sure what a word means? Search or browse below.</p>
      </div>
      <div className="glossary-search-wrap">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search terms (e.g. angina, cholesterol)…"
          aria-label="Search medical glossary"
        />
      </div>
      <div className="glossary-grid">
        {filtered.map((item) => (
          <article key={item.term} className="glossary-card">
            <h3>{item.term}</h3>
            <p>{item.plain}</p>
          </article>
        ))}
        {!filtered.length && (
          <p className="glossary-empty">No terms match your search.</p>
        )}
      </div>
    </section>
  );
}
