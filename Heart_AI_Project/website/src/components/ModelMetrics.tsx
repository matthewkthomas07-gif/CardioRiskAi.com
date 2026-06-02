import { useEffect, useState } from "react";

type Metrics = {
  accuracy_percent?: number;
  cleveland_benchmark_percent?: number;
  test_accuracy_percent?: number;
  roc_auc?: number;
  meets_90_percent_goal?: boolean;
  data?: {
    total_records?: number;
    datasets_merged?: number;
    sources?: Record<string, number>;
  };
  note?: string;
};

export default function ModelMetrics() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  useEffect(() => {
    fetch("/api/metrics")
      .then((r) => r.json())
      .then(setMetrics)
      .catch(() => setMetrics(null));
  }, []);

  const acc = metrics?.accuracy_percent ?? metrics?.cleveland_benchmark_percent;

  return (
    <section id="performance" className="performance">
      <div className="performance-head">
        <p className="eyebrow">Trained on 4 clinical datasets</p>
        <h2>Model performance</h2>
        <p className="lead">
          We merged <strong>{metrics?.data?.total_records ?? 861} patient records</strong> from
          Cleveland Clinic, Hungarian Institute, VA Long Beach, and Switzerland.
        </p>
      </div>
      <div className="metric-grid">
        <div className={`metric-card metric-hero ${metrics?.meets_90_percent_goal ? "metric-success" : ""}`}>
          <span className="metric-value">{acc != null ? `${acc}%` : "—"}</span>
          <span className="metric-label">Validated accuracy</span>
          <span className="metric-sub">
            {metrics?.cleveland_benchmark_percent != null &&
            metrics?.test_accuracy_percent != null
              ? `Cleveland ${metrics.cleveland_benchmark_percent}% · Multi-center ${metrics.test_accuracy_percent}%`
              : "Loading…"}
          </span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics?.data?.total_records ?? "—"}</span>
          <span className="metric-label">Training patients</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics?.data?.datasets_merged ?? 4}</span>
          <span className="metric-label">Merged datasets</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics?.roc_auc ?? "—"}</span>
          <span className="metric-label">ROC AUC score</span>
        </div>
      </div>
      {metrics?.data?.sources && (
        <ul className="dataset-list">
          {Object.entries(metrics.data.sources).map(([name, count]) => (
            <li key={name}>
              <strong>{name}</strong>
              <span>{count} patients</span>
            </li>
          ))}
        </ul>
      )}
      {metrics?.note && <p className="metrics-note">{metrics.note}</p>}
    </section>
  );
}
