import { useMemo } from 'react';

const modules = [
  {
    name: 'Social Automation',
    description: 'Planung, Freigabe und automatisiertes Posting über alle angebundenen Netzwerke.',
  },
  {
    name: 'KI Content Engine',
    description: 'Erstellt Entwürfe für Newsletter und Social Posts, abgestimmt auf deine Marke.',
  },
  {
    name: 'CRM & Projekte',
    description: 'Verwalte Leads, Kunden, Aufgaben und Zeiterfassung zentral.',
  },
  {
    name: 'E-Commerce & Wawi',
    description: 'Synchronisiere Lagerbestände mit Shopware und buche Zahlungen automatisch.',
  },
  {
    name: 'OSINT Radar',
    description: 'Aggregiert SpiderFoot- und Ozen-Erkenntnisse in Echtzeit-Dashboards.',
  },
];

function App() {
  const upcoming = useMemo(
    () => [
      'Personalisierbares Theme-System',
      'Workflow-Automationen mit n8n/Temporal',
      'Mandantenfähige Benutzer- und Rechteverwaltung',
    ],
    []
  );

  return (
    <div className="app">
      <header>
        <h1>Central Control Center</h1>
        <p>
          Starte deinen Stack lokal per <code>docker compose up</code> und verwalte Social Media, CRM, Automatisierung und OSINT in
          einer Oberfläche.
        </p>
      </header>

      <section>
        <h2>Aktive Module</h2>
        <div className="grid">
          {modules.map((module) => (
            <article key={module.name}>
              <h3>{module.name}</h3>
              <p>{module.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2>In Vorbereitung</h2>
        <ul>
          {upcoming.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default App;
