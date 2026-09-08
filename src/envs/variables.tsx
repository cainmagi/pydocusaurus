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
    "v1.0.0": string;
    [key: string]: any; 
  }
  sourceURIs: {
    "main": {[key: string]: string};
    "v1.0.0": {[key: string]: string};
    [key: string]: any; 
  }
  [key: string]: any; 
}

const variables: EnvVariables = {
  repoURL: "https://github.com/cainmagi/pydocusaurus",
  rawURL: "https://raw.githubusercontent.com/cainmagi/pydocusaurus",
  sourceVersion: {
    "main": "main",
    "v1.0.0": "v1.0.0",
  },
  sourceURIs: {
    "v1.0.0": {
      ".": "./__init__.py",
      "components": "components/__init__.py",
      "components.apibar": "components/apibar.py",
      "components.apibar.ComponentAPIBar": "components/apibar.py#L28",
      "components.comprotocol": "components/comprotocol.py",
      "components.comprotocol.ProtocolComponent": "components/comprotocol.py#L28",
      "core": "core/__init__.py",
      "core.analyzer": "core/analyzer.py",
      "core.analyzer.is_single_paragraph": "core/analyzer.py#L43",
      "core.attree": "core/attree.py",
      "core.attree.AttributeTreeNode": "core/attree.py#L28",
      "core.attree.ModuleAttributeTree": "core/attree.py#L70",
      "core.attree.build_sidebar": "core/attree.py#L169",
      "core.classes": "core/classes.py",
      "core.classes.AbstractAttrs": "core/classes.py#L93",
      "core.classes.ClassProfile": "core/classes.py#L114",
      "core.classes.DocClass": "core/classes.py#L563",
      "core.classes.DocProp": "core/classes.py#L245",
      "core.classes.parse_class_docs": "core/classes.py#L623",
      "core.classes.parse_prop_docs": "core/classes.py#L574",
      "core.datacls": "core/datacls.py",
      "core.datacls.DocDataClass": "core/datacls.py#L70",
      "core.datacls.DocField": "core/datacls.py#L47",
      "core.datacls.parse_dataclass_docs": "core/datacls.py#L448",
      "core.enums": "core/enums.py",
      "core.enums.DocEnum": "core/enums.py#L62",
      "core.enums.DocEnumItem": "core/enums.py#L46",
      "core.enums.parse_enum_docs": "core/enums.py#L258",
      "core.functions": "core/functions.py",
      "core.functions.DocArgument": "core/functions.py#L165",
      "core.functions.DocFunction": "core/functions.py#L711",
      "core.functions.FunctionType": "core/functions.py#L107",
      "core.functions.ParameterKind": "core/functions.py#L60",
      "core.functions.parse_argument_docs": "core/functions.py#L989",
      "core.functions.parse_func_docs": "core/functions.py#L1293",
      "core.functions.parse_return_docs": "core/functions.py#L1109",
      "core.inspectors": "core/inspectors.py",
      "core.inspectors.get_arg_default_name": "core/inspectors.py#L520",
      "core.inspectors.get_field_default": "core/inspectors.py#L622",
      "core.inspectors.get_field_docstrings": "core/inspectors.py#L489",
      "core.inspectors.get_func_signature": "core/inspectors.py#L597",
      "core.inspectors.get_lambda_source": "core/inspectors.py#L559",
      "core.inspectors.get_members_defined_in_class": "core/inspectors.py#L252",
      "core.inspectors.get_members_defined_in_enum": "core/inspectors.py#L292",
      "core.inspectors.get_mro": "core/inspectors.py#L118",
      "core.inspectors.get_obj_slang": "core/inspectors.py#L158",
      "core.inspectors.get_short_descr": "core/inspectors.py#L856",
      "core.inspectors.get_slug": "core/inspectors.py#L878",
      "core.inspectors.is_func_yield": "core/inspectors.py#L737",
      "core.inspectors.is_member_abstract": "core/inspectors.py#L706",
      "core.inspectors.is_multival_tuple": "core/inspectors.py#L669",
      "core.inspectors.is_user_defined_method": "core/inspectors.py#L217",
      "core.inspectors.relative_url_path": "core/inspectors.py#L895",
      "core.inspectors.strip_annotation_name": "core/inspectors.py#L826",
      "core.inspectors.unpack_annotation": "core/inspectors.py#L782",
      "core.inspectors.unwrap_annotated_annotation": "core/inspectors.py#L760",
      "core.modules": "core/modules.py",
      "core.modules.DocModule": "core/modules.py#L121",
      "core.modules.DocModuleMetadata": "core/modules.py#L64",
      "core.modules.DocModuleProp": "core/modules.py#L48",
      "core.modules.parse_module_doc": "core/modules.py#L375",
      "core.ops": "core/ops.py",
      "core.ops.DocOpTemplate": "core/ops.py#L73",
      "core.ops.unwrap_top_level_typehint": "core/ops.py#L37",
      "core.protocols": "core/protocols.py",
      "core.protocols.DocProtocol": "core/protocols.py#L32",
      "core.protocols.parse_protocol_docs": "core/protocols.py#L83",
      "core.texts": "core/texts.py",
      "core.texts.Section": "core/texts.py#L65",
      "core.texts.Table": "core/texts.py#L197",
      "core.texts.santize_doc_cell": "core/texts.py#L36",
      "core.typealiases": "core/typealiases.py",
      "core.typealiases.DocTypeAlias": "core/typealiases.py#L51",
      "core.typealiases.is_generic_type_alias_call": "core/typealiases.py#L220",
      "core.typealiases.is_possibly_type_expression": "core/typealiases.py#L265",
      "core.typealiases.is_runtime_root": "core/typealiases.py#L245",
      "core.typealiases.parse_type_aliases_doc": "core/typealiases.py#L343",
      "core.typeddicts": "core/typeddicts.py",
      "core.typeddicts.DocTypedDict": "core/typeddicts.py#L65",
      "core.typeddicts.DocTypedDictItem": "core/typeddicts.py#L48",
      "core.typeddicts.parse_typeddict_doc": "core/typeddicts.py#L257",
      "core.walker": "core/walker.py",
      "core.walker.PackageWalker": "core/walker.py#L418",
      "core.walker.ParserAbstract": "core/walker.py#L280",
      "core.walker.analyze_module_ast": "core/walker.py#L63",
      "core.walker.fast_import": "core/walker.py#L259",
      "core.walker.get_direct_submodules": "core/walker.py#L123",
      "core.walker.is_direct_member": "core/walker.py#L214",
      "core.walker.is_direct_module": "core/walker.py#L187",
      "core.walker.is_direct_nonmodule": "core/walker.py#L167",
      "core.walker.is_main_module": "core/walker.py#L237",
      "renderer": "renderer/__init__.py",
      "renderer.components": "renderer/components.py",
      "renderer.components.CompModule": "renderer/components.py#L30",
      "renderer.components.Components": "renderer/components.py#L64",
      "renderer.package": "renderer/package.py",
      "renderer.package.PackageInformation": "renderer/package.py#L47",
      "renderer.package.PackageRenderer": "renderer/package.py#L247",
      "renderer.package.URIHolder": "renderer/package.py#L180",
      "renderer.package.render_package_as_mdx": "renderer/package.py#L411",
      "renderer.page": "renderer/page.py",
      "renderer.page.RendererPage": "renderer/page.py#L45",
      "renderer.page.render_obj": "renderer/page.py#L138",
      "renderer.resources": "renderer/resources.py",
      "renderer.resources.as_pypi_name": "renderer/resources.py#L124",
      "renderer.resources.get_jinja_template_out_name": "renderer/resources.py#L68",
      "renderer.resources.is_jinja_template": "renderer/resources.py#L46",
      "renderer.resources.render_resource_tree": "renderer/resources.py#L143",
      "renderer.resources.ts_object": "renderer/resources.py#L90",
      "renderer.saver": "renderer/saver.py",
      "renderer.saver.SaverAbstract": "renderer/saver.py#L30",
      "renderer.saver.SaverDefault": "renderer/saver.py#L76"
    },
    "main": {
      ".": "./__init__.py",
      "components": "components/__init__.py",
      "components.apibar": "components/apibar.py",
      "components.apibar.ComponentAPIBar": "components/apibar.py#L28",
      "components.comprotocol": "components/comprotocol.py",
      "components.comprotocol.ProtocolComponent": "components/comprotocol.py#L28",
      "core": "core/__init__.py",
      "core.analyzer": "core/analyzer.py",
      "core.analyzer.is_single_paragraph": "core/analyzer.py#L43",
      "core.attree": "core/attree.py",
      "core.attree.AttributeTreeNode": "core/attree.py#L28",
      "core.attree.ModuleAttributeTree": "core/attree.py#L70",
      "core.attree.build_sidebar": "core/attree.py#L169",
      "core.classes": "core/classes.py",
      "core.classes.AbstractAttrs": "core/classes.py#L93",
      "core.classes.ClassProfile": "core/classes.py#L114",
      "core.classes.DocClass": "core/classes.py#L563",
      "core.classes.DocProp": "core/classes.py#L245",
      "core.classes.parse_class_docs": "core/classes.py#L623",
      "core.classes.parse_prop_docs": "core/classes.py#L574",
      "core.datacls": "core/datacls.py",
      "core.datacls.DocDataClass": "core/datacls.py#L70",
      "core.datacls.DocField": "core/datacls.py#L47",
      "core.datacls.parse_dataclass_docs": "core/datacls.py#L448",
      "core.enums": "core/enums.py",
      "core.enums.DocEnum": "core/enums.py#L62",
      "core.enums.DocEnumItem": "core/enums.py#L46",
      "core.enums.parse_enum_docs": "core/enums.py#L258",
      "core.functions": "core/functions.py",
      "core.functions.DocArgument": "core/functions.py#L165",
      "core.functions.DocFunction": "core/functions.py#L711",
      "core.functions.FunctionType": "core/functions.py#L107",
      "core.functions.ParameterKind": "core/functions.py#L60",
      "core.functions.parse_argument_docs": "core/functions.py#L989",
      "core.functions.parse_func_docs": "core/functions.py#L1293",
      "core.functions.parse_return_docs": "core/functions.py#L1109",
      "core.inspectors": "core/inspectors.py",
      "core.inspectors.get_arg_default_name": "core/inspectors.py#L520",
      "core.inspectors.get_field_default": "core/inspectors.py#L622",
      "core.inspectors.get_field_docstrings": "core/inspectors.py#L489",
      "core.inspectors.get_func_signature": "core/inspectors.py#L597",
      "core.inspectors.get_lambda_source": "core/inspectors.py#L559",
      "core.inspectors.get_members_defined_in_class": "core/inspectors.py#L252",
      "core.inspectors.get_members_defined_in_enum": "core/inspectors.py#L292",
      "core.inspectors.get_mro": "core/inspectors.py#L118",
      "core.inspectors.get_obj_slang": "core/inspectors.py#L158",
      "core.inspectors.get_short_descr": "core/inspectors.py#L856",
      "core.inspectors.get_slug": "core/inspectors.py#L878",
      "core.inspectors.is_func_yield": "core/inspectors.py#L737",
      "core.inspectors.is_member_abstract": "core/inspectors.py#L706",
      "core.inspectors.is_multival_tuple": "core/inspectors.py#L669",
      "core.inspectors.is_user_defined_method": "core/inspectors.py#L217",
      "core.inspectors.relative_url_path": "core/inspectors.py#L895",
      "core.inspectors.strip_annotation_name": "core/inspectors.py#L826",
      "core.inspectors.unpack_annotation": "core/inspectors.py#L782",
      "core.inspectors.unwrap_annotated_annotation": "core/inspectors.py#L760",
      "core.modules": "core/modules.py",
      "core.modules.DocModule": "core/modules.py#L121",
      "core.modules.DocModuleMetadata": "core/modules.py#L64",
      "core.modules.DocModuleProp": "core/modules.py#L48",
      "core.modules.parse_module_doc": "core/modules.py#L375",
      "core.ops": "core/ops.py",
      "core.ops.DocOpTemplate": "core/ops.py#L73",
      "core.ops.unwrap_top_level_typehint": "core/ops.py#L37",
      "core.protocols": "core/protocols.py",
      "core.protocols.DocProtocol": "core/protocols.py#L32",
      "core.protocols.parse_protocol_docs": "core/protocols.py#L83",
      "core.texts": "core/texts.py",
      "core.texts.Section": "core/texts.py#L65",
      "core.texts.Table": "core/texts.py#L197",
      "core.texts.santize_doc_cell": "core/texts.py#L36",
      "core.typealiases": "core/typealiases.py",
      "core.typealiases.DocTypeAlias": "core/typealiases.py#L51",
      "core.typealiases.is_generic_type_alias_call": "core/typealiases.py#L220",
      "core.typealiases.is_possibly_type_expression": "core/typealiases.py#L265",
      "core.typealiases.is_runtime_root": "core/typealiases.py#L245",
      "core.typealiases.parse_type_aliases_doc": "core/typealiases.py#L343",
      "core.typeddicts": "core/typeddicts.py",
      "core.typeddicts.DocTypedDict": "core/typeddicts.py#L65",
      "core.typeddicts.DocTypedDictItem": "core/typeddicts.py#L48",
      "core.typeddicts.parse_typeddict_doc": "core/typeddicts.py#L257",
      "core.walker": "core/walker.py",
      "core.walker.PackageWalker": "core/walker.py#L418",
      "core.walker.ParserAbstract": "core/walker.py#L280",
      "core.walker.analyze_module_ast": "core/walker.py#L63",
      "core.walker.fast_import": "core/walker.py#L259",
      "core.walker.get_direct_submodules": "core/walker.py#L123",
      "core.walker.is_direct_member": "core/walker.py#L214",
      "core.walker.is_direct_module": "core/walker.py#L187",
      "core.walker.is_direct_nonmodule": "core/walker.py#L167",
      "core.walker.is_main_module": "core/walker.py#L237",
      "renderer": "renderer/__init__.py",
      "renderer.components": "renderer/components.py",
      "renderer.components.CompModule": "renderer/components.py#L30",
      "renderer.components.Components": "renderer/components.py#L64",
      "renderer.package": "renderer/package.py",
      "renderer.package.PackageInformation": "renderer/package.py#L47",
      "renderer.package.PackageRenderer": "renderer/package.py#L247",
      "renderer.package.URIHolder": "renderer/package.py#L180",
      "renderer.package.render_package_as_mdx": "renderer/package.py#L411",
      "renderer.page": "renderer/page.py",
      "renderer.page.RendererPage": "renderer/page.py#L45",
      "renderer.page.render_obj": "renderer/page.py#L138",
      "renderer.resources": "renderer/resources.py",
      "renderer.resources.as_pypi_name": "renderer/resources.py#L124",
      "renderer.resources.get_jinja_template_out_name": "renderer/resources.py#L68",
      "renderer.resources.is_jinja_template": "renderer/resources.py#L46",
      "renderer.resources.render_resource_tree": "renderer/resources.py#L143",
      "renderer.resources.ts_object": "renderer/resources.py#L90",
      "renderer.saver": "renderer/saver.py",
      "renderer.saver.SaverAbstract": "renderer/saver.py#L30",
      "renderer.saver.SaverDefault": "renderer/saver.py#L76"
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
    "/pydocusaurus/" +
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
