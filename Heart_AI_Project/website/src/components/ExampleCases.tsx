type ExampleCase = {
  title: string;
  profile: string;
  signals: string[];
  outcome: string;
  risk: string;
};

const CASES: ExampleCase[] = [
  {
    title: "Active adult, normal vitals",
    profile: "42-year-old woman, no chest pain, walks daily",
    signals: [
      "Blood pressure 118/76 (home cuff)",
      "No chest pain with stairs",
      "Fasting sugar normal",
    ],
    outcome: "Model estimate in training-like profiles: lower risk band",
    risk: "~12–22%",
  },
  {
    title: "Older adult with high blood pressure",
    profile: "67-year-old man, treated hypertension, no exercise chest pain",
    signals: [
      "Systolic BP often 155–165",
      "Cholesterol 286 mg/dL on last lab",
      "Max heart rate 108 on stress test",
    ],
    outcome: "Several risk factors raise the score",
    risk: "~55–75%",
  },
  {
    title: "Chest pain with exertion",
    profile: "58-year-old man, tight chest when climbing hills",
    signals: [
      "Typical angina pattern",
      "Exercise-induced chest pain: yes",
      "Blood pressure 140, cholesterol 240",
    ],
    outcome: "Symptoms plus vitals push risk up",
    risk: "~45–65%",
  },
  {
    title: "Diabetes signal, otherwise stable",
    profile: "54-year-old woman, fasting glucose over 120",
    signals: [
      "Fasting blood sugar yes on lab",
      "Non-anginal chest discomfort",
      "Resting ECG normal",
    ],
    outcome: "Sugar and pain type matter in the model",
    risk: "~35–50%",
  },
  {
    title: "Younger adult, skipped clinic tests",
    profile: "35-year-old man, only home measurements",
    signals: [
      "Home BP 125, no chest pain",
      "Skipped cholesterol & stress-test fields",
      "Uses pulse estimate for max heart rate",
    ],
    outcome: "Estimate is less precise when clinic values are skipped",
    risk: "Varies — re-run when labs available",
  },
  {
    title: "Post-stress-test profile",
    profile: "62-year-old woman, full cardiology workup",
    signals: [
      "Flat ST slope, Oldpeak 2.0",
      "One vessel narrowed on imaging",
      "Reversible defect on blood-flow scan",
    ],
    outcome: "Hospital test results heavily influence score",
    risk: "~70–90%",
  },
  {
    title: "Senior with multiple vessel findings",
    profile: "70-year-old man, prior angiography",
    signals: [
      "Three vessels flagged on imaging",
      "Exercise angina yes",
      "Max HR 120",
    ],
    outcome: "High-impact clinical features",
    risk: "~80–95%",
  },
  {
    title: "Borderline cholesterol, good activity",
    profile: "49-year-old woman, jogs 3× weekly",
    signals: [
      "Cholesterol 245 mg/dL",
      "Max HR 175 with running",
      "No fasting sugar issues",
    ],
    outcome: "Mixed signals — lifestyle helps, labs matter",
    risk: "~25–40%",
  },
];

export default function ExampleCases() {
  return (
    <section id="examples" className="examples-section">
      <div className="examples-head">
        <p className="eyebrow">Learn by example</p>
        <h2>Sample risk profiles</h2>
        <p className="lead">
          These anonymized scenarios show how different answers change the estimate.
          Run the assistant with your own numbers for a personal result.
        </p>
      </div>
      <div className="examples-grid">
        {CASES.map((c) => (
          <article key={c.title} className="example-card">
            <h3>{c.title}</h3>
            <p className="example-profile">{c.profile}</p>
            <ul>
              {c.signals.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
            <p className="example-outcome">{c.outcome}</p>
            <span className="example-risk">Typical model range: {c.risk}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
