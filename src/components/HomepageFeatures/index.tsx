import type {ReactNode} from "react";
import clsx from "clsx";
import Heading from "@theme/Heading";

import Link from "@docusaurus/Link";
import IconExternalLink from "@theme/Icon/ExternalLink";
import Translate, {translate} from "@docusaurus/Translate";

import styles from "./styles.module.scss";

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<"svg">>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: translate({
      id: "index.feat.python.title",
      description: "Feature title for Python Docstring.",
      message: "Start with Python Docstrings",
    }),
    Svg: require("@site/static/img/undraw_pydoc.svg").default,
    description: (
      <>
        <Translate
          id="index.feat.python.descr"
          description="Feature description for Python Docstring."
          values={{
            python: (
              <Link
                href="https://docs.python.org/3/index.html"
                aria-label="Python"
              >
                Python
                <IconExternalLink />
              </Link>
            ),
            docusaurus: (
              <Link href="https://docusaurus.io/" aria-label="docusaurus">
                Docusaurus
                <IconExternalLink />
              </Link>
            ),
          }}
        >
          {
            "pyDocusaurus allows users to start with an existing package with full docstrings. Developers can focus on their own {python} docstrings, and we will do the chores. Go ahead and move your docstrings into the {docusaurus} documentation."
          }
        </Translate>
      </>
    ),
  },
  {
    title: translate({
      id: "index.feat.pydocu.title",
      description: "Feature title for pyDocusaurus.",
      message: "Powered by pyDocusaurus",
    }),
    Svg: require("@site/static/img/undraw_pydocusaurus.svg").default,
    description: (
      <>
        <Translate
          id="index.feat.pydocu.descr"
          description="Feature description for pyDocusaurus."
          values={{
            anno: (
              <Link
                href={translate({
                  id: "index.feat.pydocu.typeanno.link",
                  description: "The link to the type annotation documentation.",
                  message: "https://docs.python.org/3.14/library/typing.html",
                })}
                aria-label="Type Annotations"
              >
                {translate({
                  id: "index.feat.pydocu.typeanno.name",
                  description: "The name of the type annotation.",
                  message: "type annotations",
                })}
                <IconExternalLink />
              </Link>
            ),
          }}
        >
          {
            "pyDocusaurus will analyze the docstring structures and {anno}. The information will be integrated and synthesized into comprehensive documentation pages."
          }
        </Translate>
      </>
    ),
  },
  {
    title: translate({
      id: "index.feat.docu.title",
      description: "Feature title for Docusaurus.",
      message: "Easy to Use",
    }),
    Svg: require("@site/static/img/undraw_docusaurus.svg").default,
    description: (
      <>
        <Translate
          id="index.feat.docu.descr"
          description="Feature description for Docusaurus."
          values={{
            sphinx: (
              <Link
                href="https://www.sphinx-doc.org/en/master/"
                aria-label="Sphinx"
              >
                Sphinx
                <IconExternalLink />
              </Link>
            ),
            docu: (
              <Link href="https://docusaurus.io/" aria-label="docusaurus">
                Docusaurus
                <IconExternalLink />
              </Link>
            ),
          }}
        >
          {
            "Unlike the old-school {sphinx}, the generated {docu} documentation is powered by advanced, modern React features. pyDocusaurus connects the modern type annotation system with instant-loading sites."
          }
        </Translate>
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
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
