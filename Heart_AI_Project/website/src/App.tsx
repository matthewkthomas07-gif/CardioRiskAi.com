import ChatBot from "./components/ChatBot";
import ExampleCases from "./components/ExampleCases";
import Glossary from "./components/Glossary";
import ModelMetrics from "./components/ModelMetrics";

export default function App() {
  return (
    <div className="page">
      <header className="site-header">
        <div className="brand">
          <div className="logo" aria-hidden>
            ♥
          </div>
          <div>
            <h1>CardioRisk AI</h1>
            <p className="tagline">cardioriskai.com</p>
          </div>
        </div>
        <nav>
          <a href="#performance">Accuracy</a>
          <a href="#examples">Examples</a>
          <a href="#glossary">Medical terms</a>
          <a href="#assistant">Assistant</a>
          <a href="#safety">Safety</a>
        </nav>
      </header>

      <main>
        <ModelMetrics />

        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Guided assessment</p>
            <h2>Talk to your heart-risk assistant in plain language</h2>
            <p className="lead">
              No medical codes required. The bot walks you through questions you can
              mostly answer at home, then runs our ensemble model trained on four
              clinical databases.
            </p>
            <ul className="hero-stats">
              <li>
                <strong>8+</strong>
                <span>example profiles</span>
              </li>
              <li>
                <strong>95%</strong>
                <span>validated accuracy</span>
              </li>
              <li>
                <strong>Skip</strong>
                <span>clinic-only tests if needed</span>
              </li>
            </ul>
          </div>
          <div id="assistant" className="hero-chat">
            <ChatBot />
          </div>
        </section>

        <ExampleCases />

        <Glossary />

        <section id="how" className="features">
          <article>
            <h3>1 · Four datasets</h3>
            <p>861 patient records merged from Cleveland, Hungarian, VA, and Swiss cohorts.</p>
          </article>
          <article>
            <h3>2 · Ensemble AI</h3>
            <p>Random Forest and gradient boosting vote together for stable estimates.</p>
          </article>
          <article>
            <h3>3 · How-to guidance</h3>
            <p>Every term explains how to count it at home, or when to use a doctor’s test.</p>
          </article>
        </section>

        <section id="safety" className="disclaimer">
          <h3>Important safety notice</h3>
          <p>
            CardioRisk AI is for learning and research demos only. It does not diagnose
            disease. If you have chest pain or an emergency, call emergency services.
            See a doctor when you need tests you cannot do at home.
          </p>
        </section>
      </main>

      <footer className="site-footer">
        <p>© {new Date().getFullYear()} CardioRisk AI · Educational use only</p>
      </footer>
    </div>
  );
}
