import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

const FeatureList = [
  {
    title: 'Full Domain Management',
    description: (
      <>
        Register, renew, transfer, and manage domains with support for WHOIS
        privacy, DNSSEC, and multi-year registrations.
      </>
    ),
  },
  {
    title: 'AI-Powered Agent',
    description: (
      <>
        Natural language control with Claude AI agent that can search,
        register, configure DNS, and perform all platform actions.
      </>
    ),
  },
  {
    title: 'REST API & CLI',
    description: (
      <>
        Comprehensive REST API and command-line interface for automation and
        integration with your workflows.
      </>
    ),
  },
  {
    title: 'Self-Hosted or Cloud',
    description: (
      <>
        Run locally for development, deploy to your own infrastructure, or use
        our managed service. Full control over your domain data.
      </>
    ),
  },
  {
    title: 'Open Source',
    description: (
      <>
        MIT licensed. Contribute features, fix bugs, and customize for your
        needs. No vendor lock-in.
      </>
    ),
  },
  {
    title: 'Production Ready',
    description: (
      <>
        Docker-based deployment, PostgreSQL/Redis, async architecture, and
        production-grade security features.
      </>
    ),
  },
];

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}