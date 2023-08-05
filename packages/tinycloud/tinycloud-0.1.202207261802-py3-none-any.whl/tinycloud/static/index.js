/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t$1=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e$2=Symbol(),n$3=new Map;class s$3{constructor(t,n){if(this._$cssResult$=!0,n!==e$2)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t;}get styleSheet(){let e=n$3.get(this.cssText);return t$1&&void 0===e&&(n$3.set(this.cssText,e=new CSSStyleSheet),e.replaceSync(this.cssText)),e}toString(){return this.cssText}}const o$4=t=>new s$3("string"==typeof t?t:t+"",e$2),r$2=(t,...n)=>{const o=1===t.length?t[0]:n.reduce(((e,n,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(n)+t[s+1]),t[0]);return new s$3(o,e$2)},i$1=(e,n)=>{t$1?e.adoptedStyleSheets=n.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):n.forEach((t=>{const n=document.createElement("style"),s=window.litNonce;void 0!==s&&n.setAttribute("nonce",s),n.textContent=t.cssText,e.appendChild(n);}));},S$1=t$1?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const n of t.cssRules)e+=n.cssText;return o$4(e)})(t):t;

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var s$2;const e$1=window.trustedTypes,r$1=e$1?e$1.emptyScript:"",h$1=window.reactiveElementPolyfillSupport,o$3={toAttribute(t,i){switch(i){case Boolean:t=t?r$1:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t);}return t},fromAttribute(t,i){let s=t;switch(i){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t);}catch(t){s=null;}}return s}},n$2=(t,i)=>i!==t&&(i==i||t==t),l$2={attribute:!0,type:String,converter:o$3,reflect:!1,hasChanged:n$2};class a$1 extends HTMLElement{constructor(){super(),this._$Et=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Ei=null,this.o();}static addInitializer(t){var i;null!==(i=this.l)&&void 0!==i||(this.l=[]),this.l.push(t);}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((i,s)=>{const e=this._$Eh(s,i);void 0!==e&&(this._$Eu.set(e,s),t.push(e));})),t}static createProperty(t,i=l$2){if(i.state&&(i.attribute=!1),this.finalize(),this.elementProperties.set(t,i),!i.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,e=this.getPropertyDescriptor(t,s,i);void 0!==e&&Object.defineProperty(this.prototype,t,e);}}static getPropertyDescriptor(t,i,s){return {get(){return this[i]},set(e){const r=this[t];this[i]=e,this.requestUpdate(t,r,s);},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||l$2}static finalize(){if(this.hasOwnProperty("finalized"))return !1;this.finalized=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),this.elementProperties=new Map(t.elementProperties),this._$Eu=new Map,this.hasOwnProperty("properties")){const t=this.properties,i=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of i)this.createProperty(s,t[s]);}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(i){const s=[];if(Array.isArray(i)){const e=new Set(i.flat(1/0).reverse());for(const i of e)s.unshift(S$1(i));}else void 0!==i&&s.push(S$1(i));return s}static _$Eh(t,i){const s=i.attribute;return !1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}o(){var t;this._$Ep=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Em(),this.requestUpdate(),null===(t=this.constructor.l)||void 0===t||t.forEach((t=>t(this)));}addController(t){var i,s;(null!==(i=this._$Eg)&&void 0!==i?i:this._$Eg=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t));}removeController(t){var i;null===(i=this._$Eg)||void 0===i||i.splice(this._$Eg.indexOf(t)>>>0,1);}_$Em(){this.constructor.elementProperties.forEach(((t,i)=>{this.hasOwnProperty(i)&&(this._$Et.set(i,this[i]),delete this[i]);}));}createRenderRoot(){var t;const s=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return i$1(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostConnected)||void 0===i?void 0:i.call(t)}));}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostDisconnected)||void 0===i?void 0:i.call(t)}));}attributeChangedCallback(t,i,s){this._$AK(t,s);}_$ES(t,i,s=l$2){var e,r;const h=this.constructor._$Eh(t,s);if(void 0!==h&&!0===s.reflect){const n=(null!==(r=null===(e=s.converter)||void 0===e?void 0:e.toAttribute)&&void 0!==r?r:o$3.toAttribute)(i,s.type);this._$Ei=t,null==n?this.removeAttribute(h):this.setAttribute(h,n),this._$Ei=null;}}_$AK(t,i){var s,e,r;const h=this.constructor,n=h._$Eu.get(t);if(void 0!==n&&this._$Ei!==n){const t=h.getPropertyOptions(n),l=t.converter,a=null!==(r=null!==(e=null===(s=l)||void 0===s?void 0:s.fromAttribute)&&void 0!==e?e:"function"==typeof l?l:null)&&void 0!==r?r:o$3.fromAttribute;this._$Ei=n,this[n]=a(i,t.type),this._$Ei=null;}}requestUpdate(t,i,s){let e=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||n$2)(this[t],i)?(this._$AL.has(t)||this._$AL.set(t,i),!0===s.reflect&&this._$Ei!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,s))):e=!1),!this.isUpdatePending&&e&&(this._$Ep=this._$E_());}async _$E_(){this.isUpdatePending=!0;try{await this._$Ep;}catch(t){Promise.reject(t);}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Et&&(this._$Et.forEach(((t,i)=>this[i]=t)),this._$Et=void 0);let i=!1;const s=this._$AL;try{i=this.shouldUpdate(s),i?(this.willUpdate(s),null===(t=this._$Eg)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostUpdate)||void 0===i?void 0:i.call(t)})),this.update(s)):this._$EU();}catch(t){throw i=!1,this._$EU(),t}i&&this._$AE(s);}willUpdate(t){}_$AE(t){var i;null===(i=this._$Eg)||void 0===i||i.forEach((t=>{var i;return null===(i=t.hostUpdated)||void 0===i?void 0:i.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t);}_$EU(){this._$AL=new Map,this.isUpdatePending=!1;}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$Ep}shouldUpdate(t){return !0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,i)=>this._$ES(i,this[i],t))),this._$EC=void 0),this._$EU();}updated(t){}firstUpdated(t){}}a$1.finalized=!0,a$1.elementProperties=new Map,a$1.elementStyles=[],a$1.shadowRootOptions={mode:"open"},null==h$1||h$1({ReactiveElement:a$1}),(null!==(s$2=globalThis.reactiveElementVersions)&&void 0!==s$2?s$2:globalThis.reactiveElementVersions=[]).push("1.3.2");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t;const i=globalThis.trustedTypes,s$1=i?i.createPolicy("lit-html",{createHTML:t=>t}):void 0,e=`lit$${(Math.random()+"").slice(9)}$`,o$2="?"+e,n$1=`<${o$2}>`,l$1=document,h=(t="")=>l$1.createComment(t),r=t=>null===t||"object"!=typeof t&&"function"!=typeof t,d=Array.isArray,u=t=>{var i;return d(t)||"function"==typeof(null===(i=t)||void 0===i?void 0:i[Symbol.iterator])},c=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,v=/-->/g,a=/>/g,f=/>|[ 	\n\r](?:([^\s"'>=/]+)([ 	\n\r]*=[ 	\n\r]*(?:[^ 	\n\r"'`<>=]|("|')|))|$)/g,_=/'/g,m=/"/g,g=/^(?:script|style|textarea|title)$/i,p=t=>(i,...s)=>({_$litType$:t,strings:i,values:s}),$=p(1),b=Symbol.for("lit-noChange"),w=Symbol.for("lit-nothing"),T=new WeakMap,x=(t,i,s)=>{var e,o;const n=null!==(e=null==s?void 0:s.renderBefore)&&void 0!==e?e:i;let l=n._$litPart$;if(void 0===l){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;n._$litPart$=l=new N(i.insertBefore(h(),t),t,void 0,null!=s?s:{});}return l._$AI(t),l},A=l$1.createTreeWalker(l$1,129,null,!1),C=(t,i)=>{const o=t.length-1,l=[];let h,r=2===i?"<svg>":"",d=c;for(let i=0;i<o;i++){const s=t[i];let o,u,p=-1,$=0;for(;$<s.length&&(d.lastIndex=$,u=d.exec(s),null!==u);)$=d.lastIndex,d===c?"!--"===u[1]?d=v:void 0!==u[1]?d=a:void 0!==u[2]?(g.test(u[2])&&(h=RegExp("</"+u[2],"g")),d=f):void 0!==u[3]&&(d=f):d===f?">"===u[0]?(d=null!=h?h:c,p=-1):void 0===u[1]?p=-2:(p=d.lastIndex-u[2].length,o=u[1],d=void 0===u[3]?f:'"'===u[3]?m:_):d===m||d===_?d=f:d===v||d===a?d=c:(d=f,h=void 0);const y=d===f&&t[i+1].startsWith("/>")?" ":"";r+=d===c?s+n$1:p>=0?(l.push(o),s.slice(0,p)+"$lit$"+s.slice(p)+e+y):s+e+(-2===p?(l.push(void 0),i):y);}const u=r+(t[o]||"<?>")+(2===i?"</svg>":"");if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return [void 0!==s$1?s$1.createHTML(u):u,l]};class E{constructor({strings:t,_$litType$:s},n){let l;this.parts=[];let r=0,d=0;const u=t.length-1,c=this.parts,[v,a]=C(t,s);if(this.el=E.createElement(v,n),A.currentNode=this.el.content,2===s){const t=this.el.content,i=t.firstChild;i.remove(),t.append(...i.childNodes);}for(;null!==(l=A.nextNode())&&c.length<u;){if(1===l.nodeType){if(l.hasAttributes()){const t=[];for(const i of l.getAttributeNames())if(i.endsWith("$lit$")||i.startsWith(e)){const s=a[d++];if(t.push(i),void 0!==s){const t=l.getAttribute(s.toLowerCase()+"$lit$").split(e),i=/([.?@])?(.*)/.exec(s);c.push({type:1,index:r,name:i[2],strings:t,ctor:"."===i[1]?M:"?"===i[1]?H:"@"===i[1]?I:S});}else c.push({type:6,index:r});}for(const i of t)l.removeAttribute(i);}if(g.test(l.tagName)){const t=l.textContent.split(e),s=t.length-1;if(s>0){l.textContent=i?i.emptyScript:"";for(let i=0;i<s;i++)l.append(t[i],h()),A.nextNode(),c.push({type:2,index:++r});l.append(t[s],h());}}}else if(8===l.nodeType)if(l.data===o$2)c.push({type:2,index:r});else {let t=-1;for(;-1!==(t=l.data.indexOf(e,t+1));)c.push({type:7,index:r}),t+=e.length-1;}r++;}}static createElement(t,i){const s=l$1.createElement("template");return s.innerHTML=t,s}}function P(t,i,s=t,e){var o,n,l,h;if(i===b)return i;let d=void 0!==e?null===(o=s._$Cl)||void 0===o?void 0:o[e]:s._$Cu;const u=r(i)?void 0:i._$litDirective$;return (null==d?void 0:d.constructor)!==u&&(null===(n=null==d?void 0:d._$AO)||void 0===n||n.call(d,!1),void 0===u?d=void 0:(d=new u(t),d._$AT(t,s,e)),void 0!==e?(null!==(l=(h=s)._$Cl)&&void 0!==l?l:h._$Cl=[])[e]=d:s._$Cu=d),void 0!==d&&(i=P(t,d._$AS(t,i.values),d,e)),i}class V{constructor(t,i){this.v=[],this._$AN=void 0,this._$AD=t,this._$AM=i;}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}p(t){var i;const{el:{content:s},parts:e}=this._$AD,o=(null!==(i=null==t?void 0:t.creationScope)&&void 0!==i?i:l$1).importNode(s,!0);A.currentNode=o;let n=A.nextNode(),h=0,r=0,d=e[0];for(;void 0!==d;){if(h===d.index){let i;2===d.type?i=new N(n,n.nextSibling,this,t):1===d.type?i=new d.ctor(n,d.name,d.strings,this,t):6===d.type&&(i=new L(n,this,t)),this.v.push(i),d=e[++r];}h!==(null==d?void 0:d.index)&&(n=A.nextNode(),h++);}return o}m(t){let i=0;for(const s of this.v)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,i),i+=s.strings.length-2):s._$AI(t[i])),i++;}}class N{constructor(t,i,s,e){var o;this.type=2,this._$AH=w,this._$AN=void 0,this._$AA=t,this._$AB=i,this._$AM=s,this.options=e,this._$Cg=null===(o=null==e?void 0:e.isConnected)||void 0===o||o;}get _$AU(){var t,i;return null!==(i=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==i?i:this._$Cg}get parentNode(){let t=this._$AA.parentNode;const i=this._$AM;return void 0!==i&&11===t.nodeType&&(t=i.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,i=this){t=P(this,t,i),r(t)?t===w||null==t||""===t?(this._$AH!==w&&this._$AR(),this._$AH=w):t!==this._$AH&&t!==b&&this.$(t):void 0!==t._$litType$?this.T(t):void 0!==t.nodeType?this.k(t):u(t)?this.S(t):this.$(t);}M(t,i=this._$AB){return this._$AA.parentNode.insertBefore(t,i)}k(t){this._$AH!==t&&(this._$AR(),this._$AH=this.M(t));}$(t){this._$AH!==w&&r(this._$AH)?this._$AA.nextSibling.data=t:this.k(l$1.createTextNode(t)),this._$AH=t;}T(t){var i;const{values:s,_$litType$:e}=t,o="number"==typeof e?this._$AC(t):(void 0===e.el&&(e.el=E.createElement(e.h,this.options)),e);if((null===(i=this._$AH)||void 0===i?void 0:i._$AD)===o)this._$AH.m(s);else {const t=new V(o,this),i=t.p(this.options);t.m(s),this.k(i),this._$AH=t;}}_$AC(t){let i=T.get(t.strings);return void 0===i&&T.set(t.strings,i=new E(t)),i}S(t){d(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,e=0;for(const o of t)e===i.length?i.push(s=new N(this.M(h()),this.M(h()),this,this.options)):s=i[e],s._$AI(o),e++;e<i.length&&(this._$AR(s&&s._$AB.nextSibling,e),i.length=e);}_$AR(t=this._$AA.nextSibling,i){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,i);t&&t!==this._$AB;){const i=t.nextSibling;t.remove(),t=i;}}setConnected(t){var i;void 0===this._$AM&&(this._$Cg=t,null===(i=this._$AP)||void 0===i||i.call(this,t));}}class S{constructor(t,i,s,e,o){this.type=1,this._$AH=w,this._$AN=void 0,this.element=t,this.name=i,this._$AM=e,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=w;}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,i=this,s,e){const o=this.strings;let n=!1;if(void 0===o)t=P(this,t,i,0),n=!r(t)||t!==this._$AH&&t!==b,n&&(this._$AH=t);else {const e=t;let l,h;for(t=o[0],l=0;l<o.length-1;l++)h=P(this,e[s+l],i,l),h===b&&(h=this._$AH[l]),n||(n=!r(h)||h!==this._$AH[l]),h===w?t=w:t!==w&&(t+=(null!=h?h:"")+o[l+1]),this._$AH[l]=h;}n&&!e&&this.C(t);}C(t){t===w?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"");}}class M extends S{constructor(){super(...arguments),this.type=3;}C(t){this.element[this.name]=t===w?void 0:t;}}const k=i?i.emptyScript:"";class H extends S{constructor(){super(...arguments),this.type=4;}C(t){t&&t!==w?this.element.setAttribute(this.name,k):this.element.removeAttribute(this.name);}}class I extends S{constructor(t,i,s,e,o){super(t,i,s,e,o),this.type=5;}_$AI(t,i=this){var s;if((t=null!==(s=P(this,t,i,0))&&void 0!==s?s:w)===b)return;const e=this._$AH,o=t===w&&e!==w||t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive,n=t!==w&&(e===w||o);o&&this.element.removeEventListener(this.name,this,e),n&&this.element.addEventListener(this.name,this,t),this._$AH=t;}handleEvent(t){var i,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(i=this.options)||void 0===i?void 0:i.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t);}}class L{constructor(t,i,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=i,this.options=s;}get _$AU(){return this._$AM._$AU}_$AI(t){P(this,t);}}const z=window.litHtmlPolyfillSupport;null==z||z(E,N),(null!==(t=globalThis.litHtmlVersions)&&void 0!==t?t:globalThis.litHtmlVersions=[]).push("2.2.6");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var l,o$1;class s extends a$1{constructor(){super(...arguments),this.renderOptions={host:this},this._$Dt=void 0;}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const i=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Dt=x(i,this.renderRoot,this.renderOptions);}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!0);}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Dt)||void 0===t||t.setConnected(!1);}render(){return b}}s.finalized=!0,s._$litElement$=!0,null===(l=globalThis.litElementHydrateSupport)||void 0===l||l.call(globalThis,{LitElement:s});const n=globalThis.litElementPolyfillSupport;null==n||n({LitElement:s});(null!==(o$1=globalThis.litElementVersions)&&void 0!==o$1?o$1:globalThis.litElementVersions=[]).push("3.2.0");

/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const o=(o,r,n)=>{for(const n of r)if(n[0]===o)return (0, n[1])();return null==n?void 0:n()};

class tinycloud extends s {
  static properties = { url: {} };
  constructor() {
    super();
    this.url = location.hash.split("#")[1];
    window.addEventListener(
      "hashchange",
      () => {
        this.hashchange();
      },
      false
    );
  }
  hashchange() {
    this.url = location.hash.split("#")[1];
  }
  content() {
    var filelist = new tc_filelist();
    if (this.url) {
      filelist.url = this.url;
    }
    var fileupload = new tc_fileupload();
    fileupload.url = this.url;
    fileupload.uploadFinishedCallback = filelist.uploadFinishedCallback;
    fileupload.uploadProgressCallback = filelist.uploadProgressCallback;
    filelist.file_upload = fileupload;
    filelist.load_data();
    return $`${filelist}${fileupload}`;
  }
  // Render the UI as a function of component state
  render() {
    return $`<body><div id="header"><p>Tinycloud0.1</p><hr></div><div id="content">${this.content()}</div></body>`;
  }
}

class tc_filelist extends s {
  static properties = {
    files: {},
    url: {},
    menu: {},
    file_upload: {},
    showHidden: {},
  };
  static styles = r$2`a{color:var(--tc-link-color,#00f)}.mountpoint{color:green}.broken{color:red}`;

  load_data = () => {
    this.file_upload.style.display = "none";
    return fetch("/dav" + this.url + "?json_mode=1", {
      method: "PROPFIND",
    }).then((res) => {
      if (res.ok) {
        this.file_upload.style.display = "block";
        res.json().then((res) => {
          var files = res.files.sort((a, b) => {
            return a["name"] > b["name"];
          });
          var mountPoint = [];
          files.forEach((item, index) => {
            if (item.type === "mountpoint") {
              mountPoint.push(item);
              files.splice(index, 1);
              return;
            }
          });
          if (mountPoint.length) {
            var i;
            for (i in mountPoint) {
              files.unshift(mountPoint[i]);
            }
          }
          this.files = files;
        });
      } else {
        location.href = "#" + this.url.split("/").slice(0, -2).join("/");
        switch (res.status) {
          case 404:
            alert("文件夹不存在");
            break;
          case 403:
            alert("无权访问");
            break;
        }
      }
    });
  };
  delete_file = (filename) => {
    if (!confirm("删除文件")) {
      return 0;
    }
    fetch("/dav" + this.url + filename + "?json_mode=1", {
      method: "DELETE",
    }).then((res) => {
      if (res.ok) {
        this.load_data();
      }
    });
  };
  mkdir = (dirname) => {
    fetch("/dav" + this.url + dirname + "?json_mode=1", {
      method: "MKCOL",
    }).then((res) => {
      if (res.ok) {
        this.load_data();
      }
    });
  };
  contextmenu = (e) => {
    if (e.target.getAttribute("tc-filename")) {
      e.preventDefault();
      var filename = e.target.getAttribute("tc-filename");
      this.menu.menu = {
        打开: () => {
          window.open("/dav" + this.url + filename);
        },
        下载文件: () => {
          var m = document.createEvent("MouseEvents");
          m.initEvent("click", true, true);
          e.originalTarget.dispatchEvent(m);
        },
        删除: () => {
          this.delete_file(filename);
        },
      };
      this.menu.show(e);
    } else {
      this.menu.menu = {
        新建文件夹: () => {
          name = prompt("文件夹名");
          this.mkdir(name);
        },
        上传文件: () => {
          this.file_upload.input_form.click();
        },
        显示隐藏文件: () => {
          this.showHidden = !this.showHidden;
          localStorage.setItem("showHidden", this.showHidden);
        },
      };
      this.menu.show(e);
    }
  };
  constructor() {
    super();
    if (localStorage.getItem("showHidden") != null) {
      this.showHidden = localStorage.getItem("showHidden");
    } else {
      this.showHidden = false;
    }
    this.menu = new tc_contextmenu();
    this.url = "/";

    //this.load_data(); //fetch("/dav/"+"/"+"?json_mode=1",{  method: 'PROPFIND'}).then(res=>{res.json().then(res=>this.files=res.files)})
    //    this.renderRoot.addEventListener("contextmenu",this.contextmenu)
  }
  hasFile(filename) {
    var i;
    for (i in this.files) {
      if (this.files[i].name == filename) {
        return Number(i);
      }
    }
  }
  scrollToFile(file) {
    var fileElement = this.shadowRoot.getElementById("file-" + file);
    fileElement.scrollIntoView({ behavior: "smooth" });
    fileElement.style.background = "gray";
    setTimeout(() => {
      fileElement.style.background = "";
    }, 1000);
  }
  uploadProgressCallback = (filename, finished,speed) => {
    var idx = this.hasFile(filename);
    if (!idx) {
      this.files.push({
        name: filename,
        type: "uploading",
        finished: finished,
        speed:speed
      });
      return 0;
    }
    this.files[idx].finished = finished;
    this.files[idx].speed=speed;
    this.update();
  };
  uploadFinishedCallback = (filename) => {
    var idx = this.hasFile(filename);
    if (idx != -1) {
      this.files.pop(idx);
      this.files.push({
        name: filename,
        path: this.url + filename,
        type: "file",
      });
    }
    this.update();
    this.scrollToFile(filename);
  };
  // Render the UI as a function of component stat
  render() {
    this.renderRoot.removeEventListener("contextmenu", this.contextmenu);
    this.renderRoot.addEventListener("contextmenu", this.contextmenu);
    this.onclick = this.menu.close;
    if (!this.files) {
      return;
    }
    if (!this.showHidden) {
      var files = this.files.filter((file) => {
        if (file.name.startsWith(".")) {
          return false;
        }

        return true;
      });
    } else {
      var files = this.files;
    }

    var prev = this.url.split("/").slice(0, -2).join("/");
    if (this.url != "/") {
      prev = $`<a class="dir" href="#${prev}">../</a><br>`;
    } else {
      prev = $``;
    }
    return $`${this.menu} <strong>Path:${decodeURIComponent(this.url)}</strong><br><div>${prev} ${files.map(
        (file) =>
          $`${o(file.type, [
            [
              "dir",
              () =>
                $`<a id="file-${file.name}" tc-filename="${file.name}" class="dir" href="#${this.url}/${file.name}/">${file.name}/</a>`,
            ],
            [
              "broken",
              () =>
                $`<a id="file-${file.name}" tc-filename="${file.name}" class="broken" href="#${this.url}/${file.name}/">${file.name}/</a>`,
            ],
            [
              "file",
              () =>
                $`<a class="file" id="file-${file.name}" tc-filename="${file.name}" href="/dav/${this.url}/${file.name}" download="${file.name}">${file.name}</a>`,
            ],
            [
              "uploading",
              () =>
                $`<a class="file" id="file-${file.name}" tc-filename="${file.name}" style="background-image:linear-gradient(to right,gray ${file.finished}%,var(--tc-background) ${file.finished}%)">${file.name}</a> - ${file.speed}`,
            ],
            [
              "mountpoint",
              () =>
                $`<a class="mountpoint" id="file-${file.name}" tc-filename="${file.name}" href="#${this.url}/${file.name}">${file.name}</a>`,
            ],
          ])}<br>`
      )}</div>`;
  }
}

class tc_fileupload extends s {
  static properties = {
    url: {},
    uploadFinishedCallback: {},
    uploadProgressCallback: {},
    ol:{}
  };
  static styles = r$2`div{width:20rem;height:10rem;border-style:solid}p{margin:4rem}`;
  constructor() {
    super();
  }

  upload_file(file) {
    var xhr = new XMLHttpRequest();
    xhr.open("PUT", "/dav" + this.url + "/" + file.name + "/");
    xhr.onload = () => {
      if (xhr.status == 200) {
        this.uploadFinishedCallback(file.name);
      }
    };
    xhr.upload.onprogress = (e) => {
      var nt = new Date().getTime();//获取当前时间
      var pertime = (nt-ot)/1000; //计算出上次调用该方法时到现在的时间差，单位为s
      ot = new Date().getTime(); //重新赋值时间，用于下次计算
      var perload = e.loaded - this.ol; //计算该分段上传的文件大小，单位b
      this.ol = e.loaded; //重新赋值已上传文件大小，用以下次计算

      //上传速度计算
      var speed = perload / pertime; //单位b/s
      var units = "b/s"; //单位名称
      if (speed / 1024 > 1) {
        speed = speed / 1024;
        units = "k/s";
      }
      if (speed / 1024 > 1) {
        speed = speed / 1024;
        units = "M/s";
      }
      speed = speed.toFixed(1);
      this.uploadProgressCallback(
        file.name,
        Math.round((e.loaded / e.total) * 100),speed+units
      );
      console.log(speed);
    };
    this.ol = 0; //设置上传开始时间
    var ot = new Date().getTime();
    xhr.send(file);
    //    fetch("/dav" + this.url + "/" + file.name, {
    //     method: "PUT",
    //    body: file,
    // }).then(() => this.uploadCallback(file.name));
  }

  render() {
    this.drop = document.createElement("div");
    this.drop.innerHTML = "<p align='center'>Drop file in<p>";
    /*    this.drop.addEventListener(
      "dragenter",
      (e) => {
        e.preventDefault();
      },
      false
    );
    this.drop.addEventListener(
      "dragover",
      (e) => {
        e.preventDefault();
      },
      false
    ); */
    this.drop.addEventListener(
      "drop",
      (e) => {
        e.preventDefault();
        this.upload_file(e.dataTransfer.files[0]);
      },
      false
    );
    this.drop.addEventListener("click", () => this.input_form.click());
    this.input_form = document.createElement("input");
    this.input_form.type = "file";
    this.input_form.style.display = "none";
    this.input_form.onchange = (e) => {
      this.upload_file(this.input_form.files[0]);
    };
    return $`${this.drop}${this.input_form}`;
  }
}

class tc_contextmenu extends s {
  static properties = { menu: {} };
  static styles = r$2`div{width:200px;border:1px solid #999;background-color:var(--tc-ctxmenu-color,gray);position:absolute;top:10px;left:10px;display:none;z-index:9999999}ul{list-style:none}a:hover{background:var(--tc-link-color,#fff)}`;

  show = (ev) => {
    ev.preventDefault();
    var e = ev || window.event;

    var context = this.shadowRoot.getElementById("context");
    context.style.display = "block";

    var x = e.pageX;
    var y = e.pageY;

    context.style.left = x + "px";
    context.style.top = y + "px";

    return false;
  };
  close = () => {
    this.shadowRoot.getElementById("context").style.display = "none";
  };
  constructor() {
    super();
  }
  render() {
    var res = [];
    var item;
    for (item in this.menu) {
      res.push($`<li><a @click="${this.menu[item]}">${item}</a></li>`);
    }
    return $`<div id="context"><ul>${res}</ul></div>`;
  }
}

customElements.define("tc-main", tinycloud);
customElements.define("tc-filelist", tc_filelist);
customElements.define("tc-fileupload", tc_fileupload);
customElements.define("tc-contextmenu", tc_contextmenu);

export { tc_contextmenu, tc_filelist, tc_fileupload, tinycloud };
