import React from "react";
import clsx from "clsx";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import {HeadingSafe as Heading} from "@site/src/components/utils";
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Translate, {translate} from "@docusaurus/Translate";

import styles from "./index.module.scss";

import DarkButton from "@site/src/components/DarkButton";

import LogoSVG from "@site/static/img/logo-full.svg";

function HomepageHeader(): React.JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <div>
          <LogoSVG className={styles["title-logo"]} />
        </div>
        <Heading as="h1" className={clsx("hero__title", styles.leftAdjusted)}>
          {siteConfig.title}
        </Heading>
        <p className={clsx("hero__subtitle", styles.leftAligned)}>
          <Translate
            id="index.sub-title"
            description="Sub-title text in the cover."
            values={{
              py: <code>Python</code>,
              sph: <code>Sphinx</code>,
            }}
          >
            {
              "Let {py} package developers to generate modern documentation site from docstrings, like {sph} does."
            }
          </Translate>
        </p>
        <div className={styles.buttons}>
          <DarkButton index={true} to="/docs">
            <Translate
              id="index.button.start"
              description="Text of the index button: Get started"
            >
              Getting started
            </Translate>
          </DarkButton>
          <DarkButton
            index={true}
            href="https://pypi.org/project/pydocusaurus/"
          >
            <Translate
              id="index.button.pypi"
              description="Text of the index button: PYPI Project"
            >
              PyPI Project
            </Translate>
          </DarkButton>
        </div>
      </div>
    </header>
  );
}

export default function Home(): React.JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={translate(
        {
          id: "index.layout.title",
          description: "The title displayed in the website head.",
          message: "Hello from {title}",
        },
        {title: siteConfig.title}
      )}
      description={translate(
        {
          id: "index.layout.descr",
          description: "The description displayed in the website head.",
          message: "{descr}",
        },
        {descr: siteConfig.tagline}
      )}
    >
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
