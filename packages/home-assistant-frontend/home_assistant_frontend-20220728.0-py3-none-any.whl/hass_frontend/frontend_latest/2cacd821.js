/*! For license information please see 2cacd821.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[99137],{54040:(e,t,i)=>{var s=i(87480),o=i(33310),n=i(58417),r=i(39274);let a=class extends n.A{};a.styles=[r.W],a=(0,s.__decorate)([(0,o.Mo)("mwc-checkbox")],a)},56887:(e,t,i)=>{i.d(t,{F:()=>c});var s=i(87480),o=(i(54040),i(37500)),n=i(33310),r=i(8636),a=i(61092);class c extends a.K{constructor(){super(...arguments),this.left=!1,this.graphic="control"}render(){const e={"mdc-deprecated-list-item__graphic":this.left,"mdc-deprecated-list-item__meta":!this.left},t=this.renderText(),i=this.graphic&&"control"!==this.graphic&&!this.left?this.renderGraphic():o.dy``,s=this.hasMeta&&this.left?this.renderMeta():o.dy``,n=this.renderRipple();return o.dy`
      ${n}
      ${i}
      ${this.left?"":t}
      <span class=${(0,r.$)(e)}>
        <mwc-checkbox
            reducedTouchTarget
            tabindex=${this.tabindex}
            .checked=${this.selected}
            ?disabled=${this.disabled}
            @change=${this.onChange}>
        </mwc-checkbox>
      </span>
      ${this.left?t:""}
      ${s}`}async onChange(e){const t=e.target;this.selected===t.checked||(this._skipPropRequest=!0,this.selected=t.checked,await this.updateComplete,this._skipPropRequest=!1)}}(0,s.__decorate)([(0,n.IO)("slot")],c.prototype,"slotElement",void 0),(0,s.__decorate)([(0,n.IO)("mwc-checkbox")],c.prototype,"checkboxElement",void 0),(0,s.__decorate)([(0,n.Cb)({type:Boolean})],c.prototype,"left",void 0),(0,s.__decorate)([(0,n.Cb)({type:String,reflect:!0})],c.prototype,"graphic",void 0)},21270:(e,t,i)=>{i.d(t,{W:()=>s});const s=i(37500).iv`:host(:not([twoline])){height:56px}:host(:not([left])) .mdc-deprecated-list-item__meta{height:40px;width:40px}`},63207:(e,t,i)=>{i(65660),i(15112);var s=i(9672),o=i(87156),n=i(50856),r=i(48175);(0,s.k)({_template:n.d`
    <style>
      :host {
        @apply --layout-inline;
        @apply --layout-center-center;
        position: relative;

        vertical-align: middle;

        fill: var(--iron-icon-fill-color, currentcolor);
        stroke: var(--iron-icon-stroke-color, none);

        width: var(--iron-icon-width, 24px);
        height: var(--iron-icon-height, 24px);
        @apply --iron-icon;
      }

      :host([hidden]) {
        display: none;
      }
    </style>
`,is:"iron-icon",properties:{icon:{type:String},theme:{type:String},src:{type:String},_meta:{value:r.XY.create("iron-meta",{type:"iconset"})}},observers:["_updateIcon(_meta, isAttached)","_updateIcon(theme, isAttached)","_srcChanged(src, isAttached)","_iconChanged(icon, isAttached)"],_DEFAULT_ICONSET:"icons",_iconChanged:function(e){var t=(e||"").split(":");this._iconName=t.pop(),this._iconsetName=t.pop()||this._DEFAULT_ICONSET,this._updateIcon()},_srcChanged:function(e){this._updateIcon()},_usesIconset:function(){return this.icon||!this.src},_updateIcon:function(){this._usesIconset()?(this._img&&this._img.parentNode&&(0,o.vz)(this.root).removeChild(this._img),""===this._iconName?this._iconset&&this._iconset.removeIcon(this):this._iconsetName&&this._meta&&(this._iconset=this._meta.byKey(this._iconsetName),this._iconset?(this._iconset.applyIcon(this,this._iconName,this.theme),this.unlisten(window,"iron-iconset-added","_updateIcon")):this.listen(window,"iron-iconset-added","_updateIcon"))):(this._iconset&&this._iconset.removeIcon(this),this._img||(this._img=document.createElement("img"),this._img.style.width="100%",this._img.style.height="100%",this._img.draggable=!1),this._img.src=this.src,(0,o.vz)(this.root).appendChild(this._img))}})},15112:(e,t,i)=>{i.d(t,{P:()=>o});i(48175);var s=i(9672);class o{constructor(e){o[" "](e),this.type=e&&e.type||"default",this.key=e&&e.key,e&&"value"in e&&(this.value=e.value)}get value(){var e=this.type,t=this.key;if(e&&t)return o.types[e]&&o.types[e][t]}set value(e){var t=this.type,i=this.key;t&&i&&(t=o.types[t]=o.types[t]||{},null==e?delete t[i]:t[i]=e)}get list(){if(this.type){var e=o.types[this.type];return e?Object.keys(e).map((function(e){return n[this.type][e]}),this):[]}}byKey(e){return this.key=e,this.value}}o[" "]=function(){},o.types={};var n=o.types;(0,s.k)({is:"iron-meta",properties:{type:{type:String,value:"default"},key:{type:String},value:{type:String,notify:!0},self:{type:Boolean,observer:"_selfChanged"},__meta:{type:Boolean,computed:"__computeMeta(type, key, value)"}},hostAttributes:{hidden:!0},__computeMeta:function(e,t,i){var s=new o({type:e,key:t});return void 0!==i&&i!==s.value?s.value=i:this.value!==s.value&&(this.value=s.value),s},get list(){return this.__meta&&this.__meta.list},_selfChanged:function(e){e&&(this.value=this)},byKey:function(e){return new o({type:this.type,key:e}).value}})},89194:(e,t,i)=>{i(48175),i(65660),i(70019);var s=i(9672),o=i(50856);(0,s.k)({_template:o.d`
    <style>
      :host {
        overflow: hidden; /* needed for text-overflow: ellipsis to work on ff */
        @apply --layout-vertical;
        @apply --layout-center-justified;
        @apply --layout-flex;
      }

      :host([two-line]) {
        min-height: var(--paper-item-body-two-line-min-height, 72px);
      }

      :host([three-line]) {
        min-height: var(--paper-item-body-three-line-min-height, 88px);
      }

      :host > ::slotted(*) {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      :host > ::slotted([secondary]) {
        @apply --paper-font-body1;

        color: var(--paper-item-body-secondary-color, var(--secondary-text-color));

        @apply --paper-item-body-secondary;
      }
    </style>

    <slot></slot>
`,is:"paper-item-body"})},21560:(e,t,i)=>{i.d(t,{ZH:()=>l,MT:()=>n,U2:()=>c,RV:()=>o,t8:()=>h});const s=function(){if(!(!navigator.userAgentData&&/Safari\//.test(navigator.userAgent)&&!/Chrom(e|ium)\//.test(navigator.userAgent))||!indexedDB.databases)return Promise.resolve();let e;return new Promise((t=>{const i=()=>indexedDB.databases().finally(t);e=setInterval(i,100),i()})).finally((()=>clearInterval(e)))};function o(e){return new Promise(((t,i)=>{e.oncomplete=e.onsuccess=()=>t(e.result),e.onabort=e.onerror=()=>i(e.error)}))}function n(e,t){const i=s().then((()=>{const i=indexedDB.open(e);return i.onupgradeneeded=()=>i.result.createObjectStore(t),o(i)}));return(e,s)=>i.then((i=>s(i.transaction(t,e).objectStore(t))))}let r;function a(){return r||(r=n("keyval-store","keyval")),r}function c(e,t=a()){return t("readonly",(t=>o(t.get(e))))}function h(e,t,i=a()){return i("readwrite",(i=>(i.put(t,e),o(i.transaction))))}function l(e=a()){return e("readwrite",(e=>(e.clear(),o(e.transaction))))}}}]);
//# sourceMappingURL=2cacd821.js.map