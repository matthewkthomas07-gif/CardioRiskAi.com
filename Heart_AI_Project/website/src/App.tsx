import ChatBot from "./components/ChatBot";
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
            <h2>Talk to your AI heart-risk assistant</h2>
            <p className="lead">
              The bot collects 13 health measurements, then runs them through our ensemble
              model trained on four clinical databases.
            </p>
            <ul className="hero-stats">
              <li>
                <strong>13</strong>
                <span>health signals</span>
              </li>
              <li>
                <strong>90%+</strong>
                <span>validated accuracy</span>
              </li>
              <li>
                <strong>Live</strong>
                <span>inference</span>
              </li>
            </ul>
          </div>
          <div id="assistant" className="hero-chat">
            <ChatBot />
          </div>
        </section>

        <Glossary />

        <section id="how" className="features">
          <article>
            <h3>1 · Four datasets</h3>
            <p>More diverse training data than a single-hospital study alone.</p>
          </article>
          <article>
            <h3>2 · Ensemble AI</h3>
            <p>Random Forest and gradient boosting vote together for stability.</p>
          </article>
          <article>
            <h3>3 · Plain language</h3>
            <p>Glossary and chat guidance so jargon does not block you.</p>
          </article>
        </section>

        <section id="safety" className="disclaimer">
          <h3>Important safety notice</h3>
          <p>
            CardioRisk AI is for learning and research demos only. It does not diagnose
            disease. If you have chest pain or an emergency, call emergency services.
          </p>
        </section>
      </main>

      <footer className="site-footer">
        <p>© {new Date().getFullYear()} CardioRisk AI · Educational use only</p>
      </footer>
    </div>
  );
}
