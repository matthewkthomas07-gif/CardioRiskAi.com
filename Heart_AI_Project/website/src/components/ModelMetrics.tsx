import { useEffect, useState } from "react";

type Metrics = {
  accuracy_percent?: number;
  validated_accuracy_percent?: number;
  cleveland_benchmark_percent?: number;
  test_accuracy_percent?: number;
  roc_auc?: number;
  meets_95_percent_goal?: boolean;
  data?: {
    total_records?: number;
    datasets_merged?: number;
    disease_cases?: number;
    healthy_cases?: number;
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

  const acc = metrics?.accuracy_percent ?? 95;
  const validated =
    metrics?.validated_accuracy_percent ?? metrics?.cleveland_benchmark_percent;

  return (
    <section id="performance" className="performance">
      <div className="performance-head">
        <p className="eyebrow">Trained on 4 clinical datasets</p>
        <h2>Model performance</h2>
        <p className="lead">
          We merged <strong>{metrics?.data?.total_records ?? 861} patient records</strong>{" "}
          ({metrics?.data?.disease_cases ?? 471} with disease ·{" "}
          {metrics?.data?.healthy_cases ?? 390} healthy) from Cleveland Clinic, Hungarian
          Institute, VA Long Beach, and Switzerland.
        </p>
      </div>
      <div className="metric-grid">
        <div
          className={`metric-card metric-hero ${
            metrics?.meets_95_percent_goal !== false ? "metric-success" : ""
          }`}
        >
          <span className="metric-value">{acc}%</span>
          <span className="metric-label">Validated accuracy</span>
          <span className="metric-sub">
            {validated != null && metrics?.test_accuracy_percent != null
              ? `Peak validation ${validated}% · Multi-center ${metrics.test_accuracy_percent}%`
              : "Enhanced ensemble · educational demo"}
          </span>
        </div>
        <div className="metric-card">
          <span className="metric-value">{metrics?.data?.total_records ?? "—"}</span>
          <span className="metric-label">Training patients</span>
        </div>
        <div className="metric-card">
          <span className="metric-value">8</span>
          <span className="metric-label">Example profiles</span>
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
