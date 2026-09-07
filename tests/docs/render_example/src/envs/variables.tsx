/**
 * Environmental variables of this side.
 * Yuchen Jin, mailto:cainmagi@gmail.com
 */

import React from "react";
import Link from "@docusaurus/Link";
import {useDocsVersion} from "@docusaurus/plugin-content-docs/client";

import InlineIcon from "../components/InlineIcon";
import mdiDot from "@iconify-icons/mdi/dot";

const docsPluginId = undefined; // Default docs plugin instance

interface EnvVariables {
  repoURL: string;
  rawURL: string;
  sourceVersion: {
    "main": string;
    [key: string]: any; 
  }
  sourceURIs: {
    "main": {[key: string]: string};
    [key: string]: any; 
  }
  [key: string]: any; 
}

const variables: EnvVariables = {
  repoURL: "https://github.com/cainmagi/render_example",
  rawURL: "https://raw.githubusercontent.com/cainmagi/render_example",
  sourceVersion: {
    "main": "main",
  },
  sourceURIs: {
    "main": {
      ".": "./__init__.py",
      "ExampleRootClass": "./__init__.py#L43",
      "classes": "classes.py",
      "classes.ExampleClass": "classes.py#L34",
      "classes.ExampleEnum": "classes.py#L232",
      "classes.ExampleModel": "classes.py#L189",
      "example_root_func": "./__init__.py#L47",
      "funcs": "funcs.py",
      "funcs.example_complicated_func": "funcs.py#L32",
      "funcs.example_iterator_func": "funcs.py#L62",
      "funcs.example_overload_func": "funcs.py#L131",
      "subpackage": "subpackage/__init__.py",
      "subpackage.ExampleAnno": "subpackage/__init__.py#L26",
      "subpackage.empty_function": "subpackage/__init__.py#L30",
      "typecls": "typecls.py",
      "typecls.ComplicatedList": "typecls.py#L41",
      "typecls.CustomType": "typecls.py#L35",
      "typecls.ExampleDict": "typecls.py#L51",
      "typecls.ExampleProtocol": "typecls.py#L70",
      "typecls.SpecifiedList": "typecls.py#L38"
    }
  },
};

const useCurrentSourceVersion = (): string => {
  const versionHook = useDocsVersion();
  const versionLabel = versionHook?.label;
  return (
    variables.sourceVersion[versionLabel] || variables.sourceVersion["main"]
  );
};

export const rawURL = (url: string): string => {
  return variables.rawURL + "/" + url;
};

export const repoURL = (url: string | undefined = undefined): string => {
  return url ? variables.repoURL + "/" + url : variables.repoURL;
};

export const releaseURL = (ver: string | undefined = undefined): string => {
  const _ver = ver?.toLowerCase() === "next" ? "main" : (ver || "");
  const version = variables.sourceVersion[_ver] || useCurrentSourceVersion();
  if (version === "main" || _ver === "main") {
    return variables.repoURL + "/releases/latest";
  }
  return variables.repoURL + "/releases/tag/" + version;
};

export const rootURL = (url: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  return variables.repoURL + "/blob/" + currentSourceVersion + "/" + url;
};

const getURIByVersionPath = (path: string, ver: string): string => {
  const routes = typeof path === "string" ? path.trim() : "";
  if (routes.length === 0) {
    return path;
  }
  const currentURI = variables.sourceURIs[ver] || variables.sourceURIs["main"];
  return currentURI[path] || path;
};

export const sourceURL = (url: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  return (
    variables.repoURL +
    "/blob/" +
    currentSourceVersion +
    "/render_example/" +
    getURIByVersionPath(url, currentSourceVersion)
  );
};

export const demoURL = (url?: string): string => {
  const currentSourceVersion = useCurrentSourceVersion();
  if (!url) {
    return variables.repoURL + "/blob/" + currentSourceVersion + "/usage.py";
  }
  return (
    variables.repoURL + "/blob/" + currentSourceVersion + "/examples/" + url
  );
};

export type SourceLinkProps = {
  url: string;
  children: React.ReactNode;
};

export const SourceLink = ({url, children}: SourceLinkProps): React.JSX.Element => {
  return (
    <Link to={sourceURL(url)} className="noline">
      {children}
    </Link>
  );
};

export type SplitterProps = {
  padx?: string;
};

export const Splitter = ({padx = "0"}: SplitterProps): React.JSX.Element => {
  return (
    <span style={{padding: "0 " + padx}}>
      <InlineIcon icon={mdiDot} />
    </span>
  );
};
