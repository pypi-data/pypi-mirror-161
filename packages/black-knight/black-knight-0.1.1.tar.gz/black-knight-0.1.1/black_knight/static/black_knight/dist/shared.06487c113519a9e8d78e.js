(self["webpackChunkblack_knight"] = self["webpackChunkblack_knight"] || []).push([[712],{

/***/ 5071:
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

!function(t,e){ true?module.exports=e(__webpack_require__(7294)):0}(self,(function(t){return(()=>{"use strict";var e={790:function(t,e,r){var n=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0}),e.Avatar=void 0;var a=n(r(156));e.Avatar=function(t){var e=t.picture,r=t.username;if(e)return a.default.createElement("img",{src:e,draggable:!1,alt:"".concat(r||"user"," avatar"),onContextMenu:function(t){return t.preventDefault()}});var n=i();return a.default.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",width:"100%",height:"100%",viewBox:"0 0 5 5"},a.default.createElement("rect",{x:"0",y:"0",width:"100%",height:"100%",rx:"0",fill:n.b}),a.default.createElement("text",{x:"50%",y:"50%",dy:".1em",fill:n.c,textAnchor:"middle",dominantBaseline:"middle",style:{fontFamily:"inherit",fontSize:"3px",lineHeight:1,textTransform:"uppercase",fontWeight:"bold"}},o(r)),a.default.createElement("defs",null,a.default.createElement("linearGradient",{id:"gradient",x1:"0%",y1:"0%",x2:"100%",y2:"0"},a.default.createElement("stop",{offset:"0%",stopColor:"#ff0000"}),a.default.createElement("stop",{offset:"10%",stopColor:"#ff9a00"}),a.default.createElement("stop",{offset:"20%",stopColor:"#d0de21"}),a.default.createElement("stop",{offset:"30%",stopColor:"#4fdc4a"}),a.default.createElement("stop",{offset:"40%",stopColor:"#3fdad8"}),a.default.createElement("stop",{offset:"50%",stopColor:"#2fc9e2"}),a.default.createElement("stop",{offset:"60%",stopColor:"#1c7fee"}),a.default.createElement("stop",{offset:"70%",stopColor:"#5f15f2"}),a.default.createElement("stop",{offset:"80%",stopColor:"#ba0cf8"}),a.default.createElement("stop",{offset:"90%",stopColor:"#fb07d9"}),a.default.createElement("stop",{offset:"100%",stopColor:"#ff0000"})),a.default.createElement("pattern",{id:"pattern",x:"0",y:"0",width:"300%",height:"100%",patternUnits:"userSpaceOnUse"},a.default.createElement("rect",{x:"0",y:"0",width:"150%",height:"100%",fill:"url(#gradient)"},a.default.createElement("animate",{attributeType:"XML",attributeName:"x",from:"0",to:"150%",dur:"3s",repeatCount:"indefinite"})),a.default.createElement("rect",{x:"-150%",y:"0",width:"150%",height:"100%",fill:"url(#gradient)"},a.default.createElement("animate",{attributeType:"XML",attributeName:"x",from:"-150%",to:"0",dur:"3s",repeatCount:"indefinite"})))))};var o=function(t){if(!t)return"G";try{return String.fromCodePoint(t.codePointAt(0))}catch(e){return t.charAt(0)}},i=function(){var t=Math.floor(16777215*Math.random()),e="#"+t.toString(16);if(7!==e.length)return i();var r="#fff";return.2126*(t>>16&255)+.7152*(t>>8&255)+.0722*(t>>0&255)>200&&(r="#000"),707===Math.floor(1e3*Math.random())?{b:"#040404",c:"url(#pattern)"}:{b:e,c:r}}},457:function(t,e,r){var n=this&&this.__assign||function(){return n=Object.assign||function(t){for(var e,r=1,n=arguments.length;r<n;r++)for(var a in e=arguments[r])Object.prototype.hasOwnProperty.call(e,a)&&(t[a]=e[a]);return t},n.apply(this,arguments)},a=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0});var o=a(r(156)),i={fill:"freeze",calcMode:"spline",keyTimes:"0; 1",keySplines:"0.35, 0.18, 0.2, 1.0"},u=function(t,e){return"OOTeamLoadingAnime".concat(t).concat(e)};e.default=function(t){var e=t.point,r=t.index,a=t.dur,l=t.points,c=l.length-1,s=r===c?l.at(0):l.at(r+1);if(!s)return o.default.createElement(o.default.Fragment,null);var f=e[0],p=e[1],d=s[0],h=s[1],m=0===r?"0;".concat(u(2,c),".end"):"".concat(u(1,r-1),".end"),v="".concat(0===r?u(1,c):u(2,r-1),".end"),y="".concat(0===r?u(2,c):u(1,r-1),".end");return o.default.createElement("line",{x1:f,y1:p,x2:f,y2:p,visibility:"hidden"},o.default.createElement("animate",{attributeName:"visibility",values:"visible",dur:"0s",begin:m,fill:"freeze"}),o.default.createElement("animate",{attributeName:"visibility",values:"hidden",dur:"0s",begin:"".concat(u(2,r),".end"),fill:"freeze"}),o.default.createElement("animate",n({id:u(1,r),attributeName:"x2",values:"".concat(f,";").concat(d),begin:m,dur:a},i)),o.default.createElement("animate",n({attributeName:"y2",values:"".concat(p,";").concat(h),begin:m,dur:a},i)),o.default.createElement("animate",n({id:u(2,r),attributeName:"x1",values:"".concat(f,";").concat(d),begin:v,dur:a},i)),o.default.createElement("animate",n({attributeName:"y1",values:"".concat(p,";").concat(h),begin:v,dur:a},i)),o.default.createElement("animate",{attributeName:"x1",values:"".concat(f),dur:"0s",begin:y}),o.default.createElement("animate",{attributeName:"y1",values:"".concat(p),dur:"0s",begin:y}))}},145:function(t,e){var r=this&&this.__assign||function(){return r=Object.assign||function(t){for(var e,r=1,n=arguments.length;r<n;r++)for(var a in e=arguments[r])Object.prototype.hasOwnProperty.call(e,a)&&(t[a]=e[a]);return t},r.apply(this,arguments)};Object.defineProperty(e,"__esModule",{value:!0}),e.GetTheShape=e.toPath=e.DataBase=void 0;var n={hexagon:{viewBox:"0 0 6 6",points:[[1.5,.4],[0,3],[1.5,5.6],[4.5,5.6],[6,3],[4.5,.4]]},triangle:{viewBox:"0 0 1 1",points:[[.5,.04],[0,.96],[1,.96]]}};e.DataBase=n;var a=function(t){return"M"+t.map((function(t){return"".concat(t[0]," ").concat(t[1])})).join(" ")};e.toPath=a,e.GetTheShape=function(t){if("string"!=typeof t)return r({path:a(t.points)},t);var e=n[t];return r({path:a(e.points)},e)}},502:function(t,e,r){var n=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};Object.defineProperty(e,"__esModule",{value:!0}),e.Loading=void 0;var a=n(r(156)),o=r(145),i=n(r(457));e.Loading=function(t){var e=t.duration,r=void 0===e?"707ms":e,n=t.shape,u=void 0===n?"hexagon":n,l=(0,o.GetTheShape)(u),c=l.path,s=l.points,f=l.viewBox;return a.default.createElement("svg",{viewBox:f},a.default.createElement("clipPath",{id:"hex"},a.default.createElement("path",{d:c})),a.default.createElement("g",{clipPath:"url(#hex)"},s.map((function(t,e){return a.default.createElement(i.default,{point:t,points:s,index:e,key:e,dur:r})}))))}},607:function(t,e,r){var n=this&&this.__createBinding||(Object.create?function(t,e,r,n){void 0===n&&(n=r);var a=Object.getOwnPropertyDescriptor(e,r);a&&!("get"in a?!e.__esModule:a.writable||a.configurable)||(a={enumerable:!0,get:function(){return e[r]}}),Object.defineProperty(t,n,a)}:function(t,e,r,n){void 0===n&&(n=r),t[n]=e[r]}),a=this&&this.__exportStar||function(t,e){for(var r in t)"default"===r||Object.prototype.hasOwnProperty.call(e,r)||n(e,t,r)};Object.defineProperty(e,"__esModule",{value:!0}),a(r(790),e),a(r(502),e),a(r(928),e)},129:function(t,e,r){var n,a=this&&this.__extends||(n=function(t,e){return n=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var r in e)Object.prototype.hasOwnProperty.call(e,r)&&(t[r]=e[r])},n(t,e)},function(t,e){if("function"!=typeof e&&null!==e)throw new TypeError("Class extends value "+String(e)+" is not a constructor or null");function r(){this.constructor=t}n(t,e),t.prototype=null===e?Object.create(e):(r.prototype=e.prototype,new r)});Object.defineProperty(e,"__esModule",{value:!0}),e.CountAnim=void 0;var o=function(t){function e(){var e=null!==t&&t.apply(this,arguments)||this;return e.state={Count:e.props.start||0,accumulator:0},e.formatter=new Intl.NumberFormat,e.UpdaterID=null,e.CheckEnd=function(t,e){return e<=t},e.Operation=function(t,e){return Math.ceil(t+e)},e.UpdateCounter=e.UpdateCounterPr.bind(e),e}return a(e,t),e.prototype.ClearUpdater=function(){this.UpdaterID&&(clearInterval(this.UpdaterID),this.UpdaterID=null)},e.prototype.UpdateCounterPr=function(){var t=this;this.setState((function(e){if(!t.CheckEnd(e.Count,t.props.end)){var r=t.Operation(e.Count,e.accumulator);return t.CheckEnd(r,t.props.end)?(t.ClearUpdater(),{Count:t.props.end}):{Count:r}}return t.ClearUpdater(),null}))},e.prototype.StartUpdate=function(){this.ClearUpdater(),this.UpdaterID=setInterval(this.UpdateCounter,this.props.speed||70)},e.prototype.GetAccumulator=function(){return Math.ceil(this.props.end/77*1e5)/1e5},e.prototype.componentDidMount=function(){this.props.CheckEnd&&(this.CheckEnd=this.props.CheckEnd),this.props.Operation&&(this.Operation=this.props.Operation),this.props.GetAccumulator&&(this.GetAccumulator=this.props.GetAccumulator),this.setState({accumulator:this.GetAccumulator()}),this.StartUpdate()},e.prototype.componentDidUpdate=function(t){t.end===this.props.end&&t.start===this.props.start||("number"==typeof this.props.start&&this.setState({Count:this.props.start}),this.setState({accumulator:this.GetAccumulator()}),this.StartUpdate())},e.prototype.render=function(){return!1===this.props.format?this.state.Count.toString():this.formatter.format(this.state.Count).toString()},e}(r(156).Component);e.CountAnim=o,e.default=o},208:(t,e)=>{Object.defineProperty(e,"__esModule",{value:!0}),e.DisplayNumbers=e.Empty=e.C=void 0,e.C=function(t,e){return t?" ".concat(e||"active"," "):""},e.Empty=function(t){return 0===Object.keys(t).length};var r=Intl.NumberFormat("en",{notation:"compact"});e.DisplayNumbers=function(t,e,n){void 0===e&&(e=1e3),n||(n=10*e);var a=r.format(n);if(n.toString().length,n<e)throw Error("max cant be smaller that min");return t<=e?t.toString():t>=n?"+"+a:r.format(t)}},928:function(t,e,r){var n=this&&this.__createBinding||(Object.create?function(t,e,r,n){void 0===n&&(n=r);var a=Object.getOwnPropertyDescriptor(e,r);a&&!("get"in a?!e.__esModule:a.writable||a.configurable)||(a={enumerable:!0,get:function(){return e[r]}}),Object.defineProperty(t,n,a)}:function(t,e,r,n){void 0===n&&(n=r),t[n]=e[r]}),a=this&&this.__exportStar||function(t,e){for(var r in t)"default"===r||Object.prototype.hasOwnProperty.call(e,r)||n(e,t,r)};Object.defineProperty(e,"__esModule",{value:!0}),a(r(208),e),a(r(405),e),a(r(129),e)},405:function(t,e,r){var n=this&&this.__assign||function(){return n=Object.assign||function(t){for(var e,r=1,n=arguments.length;r<n;r++)for(var a in e=arguments[r])Object.prototype.hasOwnProperty.call(e,a)&&(t[a]=e[a]);return t},n.apply(this,arguments)},a=this&&this.__createBinding||(Object.create?function(t,e,r,n){void 0===n&&(n=r);var a=Object.getOwnPropertyDescriptor(e,r);a&&!("get"in a?!e.__esModule:a.writable||a.configurable)||(a={enumerable:!0,get:function(){return e[r]}}),Object.defineProperty(t,n,a)}:function(t,e,r,n){void 0===n&&(n=r),t[n]=e[r]}),o=this&&this.__setModuleDefault||(Object.create?function(t,e){Object.defineProperty(t,"default",{enumerable:!0,value:e})}:function(t,e){t.default=e}),i=this&&this.__importStar||function(t){if(t&&t.__esModule)return t;var e={};if(null!=t)for(var r in t)"default"!==r&&Object.prototype.hasOwnProperty.call(t,r)&&a(e,t,r);return o(e,t),e};Object.defineProperty(e,"__esModule",{value:!0}),e.NiceDoc=void 0;var u=i(r(156));e.NiceDoc=function(t){var e=t.doc,r=t.type,a=void 0===r?"div":r,o=t.attrs;return e?u.default.createElement(u.default.Fragment,null,function(t){return t.replaceAll("\r","").split("\n").map((function(t){if(t){var e=t.split("");if(e.length>0&&e.every((function(t){return" "===t})))return""}return t}))}(e).map((function(t,e){return t?(0,u.createElement)(a,n({key:e},o),t):u.default.createElement("br",{key:e})}))):u.default.createElement(u.default.Fragment,null)}},156:e=>{e.exports=t}},r={};return function t(n){var a=r[n];if(void 0!==a)return a.exports;var o=r[n]={exports:{}};return e[n].call(o.exports,o,o.exports,t),o.exports}(607)})()}));

/***/ }),

/***/ 1131:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Provider": () => (/* binding */ Provider),
/* harmony export */   "SECRET_INTERNAL_getScopeContext": () => (/* binding */ getScopeContext),
/* harmony export */   "atom": () => (/* binding */ atom),
/* harmony export */   "unstable_createStore": () => (/* binding */ createStoreForExport),
/* harmony export */   "useAtom": () => (/* binding */ useAtom),
/* harmony export */   "useAtomValue": () => (/* binding */ useAtomValue),
/* harmony export */   "useSetAtom": () => (/* binding */ useSetAtom)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(7294);


const SUSPENSE_PROMISE = Symbol();
const isSuspensePromise = (promise) => !!promise[SUSPENSE_PROMISE];
const isSuspensePromiseAlreadyCancelled = (suspensePromise) => !suspensePromise[SUSPENSE_PROMISE].c;
const cancelSuspensePromise = (suspensePromise) => {
  var _a, _b;
  (_b = (_a = suspensePromise[SUSPENSE_PROMISE]).c) == null ? void 0 : _b.call(_a);
};
const isEqualSuspensePromise = (oldSuspensePromise, newSuspensePromise) => {
  const oldOriginalPromise = oldSuspensePromise[SUSPENSE_PROMISE].o;
  const newOriginalPromise = newSuspensePromise[SUSPENSE_PROMISE].o;
  return oldOriginalPromise === newOriginalPromise || oldSuspensePromise === newOriginalPromise || isSuspensePromise(oldOriginalPromise) && isEqualSuspensePromise(oldOriginalPromise, newSuspensePromise);
};
const createSuspensePromise = (promise) => {
  const objectToAttach = {
    o: promise,
    c: null
  };
  const suspensePromise = new Promise((resolve) => {
    objectToAttach.c = () => {
      objectToAttach.c = null;
      resolve();
    };
    promise.then(objectToAttach.c, objectToAttach.c);
  });
  suspensePromise[SUSPENSE_PROMISE] = objectToAttach;
  return suspensePromise;
};

var __defProp$1 = Object.defineProperty;
var __defProps$1 = Object.defineProperties;
var __getOwnPropDescs$1 = Object.getOwnPropertyDescriptors;
var __getOwnPropSymbols$1 = Object.getOwnPropertySymbols;
var __hasOwnProp$1 = Object.prototype.hasOwnProperty;
var __propIsEnum$1 = Object.prototype.propertyIsEnumerable;
var __defNormalProp$1 = (obj, key, value) => key in obj ? __defProp$1(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues$1 = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp$1.call(b, prop))
      __defNormalProp$1(a, prop, b[prop]);
  if (__getOwnPropSymbols$1)
    for (var prop of __getOwnPropSymbols$1(b)) {
      if (__propIsEnum$1.call(b, prop))
        __defNormalProp$1(a, prop, b[prop]);
    }
  return a;
};
var __spreadProps$1 = (a, b) => __defProps$1(a, __getOwnPropDescs$1(b));
const hasInitialValue = (atom) => "init" in atom;
const READ_ATOM = "r";
const WRITE_ATOM = "w";
const COMMIT_ATOM = "c";
const SUBSCRIBE_ATOM = "s";
const RESTORE_ATOMS = "h";
const DEV_SUBSCRIBE_STATE = "n";
const DEV_GET_MOUNTED_ATOMS = "l";
const DEV_GET_ATOM_STATE = "a";
const DEV_GET_MOUNTED = "m";
const createStore = (initialValues) => {
  const committedAtomStateMap = /* @__PURE__ */ new WeakMap();
  const mountedMap = /* @__PURE__ */ new WeakMap();
  const pendingMap = /* @__PURE__ */ new Map();
  let stateListeners;
  let mountedAtoms;
  if (true) {
    stateListeners = /* @__PURE__ */ new Set();
    mountedAtoms = /* @__PURE__ */ new Set();
  }
  if (initialValues) {
    for (const [atom, value] of initialValues) {
      const atomState = { v: value, r: 0, d: /* @__PURE__ */ new Map() };
      if (true) {
        Object.freeze(atomState);
        if (!hasInitialValue(atom)) {
          console.warn("Found initial value for derived atom which can cause unexpected behavior", atom);
        }
      }
      committedAtomStateMap.set(atom, atomState);
    }
  }
  const suspensePromiseCacheMap = /* @__PURE__ */ new WeakMap();
  const addSuspensePromiseToCache = (version, atom, suspensePromise) => {
    let cache = suspensePromiseCacheMap.get(atom);
    if (!cache) {
      cache = /* @__PURE__ */ new Map();
      suspensePromiseCacheMap.set(atom, cache);
    }
    suspensePromise.then(() => {
      if (cache.get(version) === suspensePromise) {
        cache.delete(version);
        if (!cache.size) {
          suspensePromiseCacheMap.delete(atom);
        }
      }
    });
    cache.set(version, suspensePromise);
  };
  const cancelAllSuspensePromiseInCache = (atom) => {
    const versionSet = /* @__PURE__ */ new Set();
    const cache = suspensePromiseCacheMap.get(atom);
    if (cache) {
      suspensePromiseCacheMap.delete(atom);
      cache.forEach((suspensePromise, version) => {
        cancelSuspensePromise(suspensePromise);
        versionSet.add(version);
      });
    }
    return versionSet;
  };
  const versionedAtomStateMapMap = /* @__PURE__ */ new WeakMap();
  const getVersionedAtomStateMap = (version) => {
    let versionedAtomStateMap = versionedAtomStateMapMap.get(version);
    if (!versionedAtomStateMap) {
      versionedAtomStateMap = /* @__PURE__ */ new Map();
      versionedAtomStateMapMap.set(version, versionedAtomStateMap);
    }
    return versionedAtomStateMap;
  };
  const getAtomState = (version, atom) => {
    if (version) {
      const versionedAtomStateMap = getVersionedAtomStateMap(version);
      let atomState = versionedAtomStateMap.get(atom);
      if (!atomState) {
        atomState = getAtomState(version.p, atom);
        if (atomState) {
          if ("p" in atomState) {
            atomState.p.then(() => versionedAtomStateMap.delete(atom));
          }
          versionedAtomStateMap.set(atom, atomState);
        }
      }
      return atomState;
    }
    return committedAtomStateMap.get(atom);
  };
  const setAtomState = (version, atom, atomState) => {
    if (true) {
      Object.freeze(atomState);
    }
    if (version) {
      const versionedAtomStateMap = getVersionedAtomStateMap(version);
      versionedAtomStateMap.set(atom, atomState);
    } else {
      const prevAtomState = committedAtomStateMap.get(atom);
      committedAtomStateMap.set(atom, atomState);
      if (!pendingMap.has(atom)) {
        pendingMap.set(atom, prevAtomState);
      }
    }
  };
  const createReadDependencies = (version, prevReadDependencies = /* @__PURE__ */ new Map(), dependencies) => {
    if (!dependencies) {
      return prevReadDependencies;
    }
    const readDependencies = /* @__PURE__ */ new Map();
    let changed = false;
    dependencies.forEach((atom) => {
      var _a;
      const revision = ((_a = getAtomState(version, atom)) == null ? void 0 : _a.r) || 0;
      readDependencies.set(atom, revision);
      if (prevReadDependencies.get(atom) !== revision) {
        changed = true;
      }
    });
    if (prevReadDependencies.size === readDependencies.size && !changed) {
      return prevReadDependencies;
    }
    return readDependencies;
  };
  const setAtomValue = (version, atom, value, dependencies, suspensePromise) => {
    const atomState = getAtomState(version, atom);
    if (atomState) {
      if (suspensePromise && (!("p" in atomState) || !isEqualSuspensePromise(atomState.p, suspensePromise))) {
        return atomState;
      }
      if ("p" in atomState) {
        cancelSuspensePromise(atomState.p);
      }
    }
    const nextAtomState = {
      v: value,
      r: (atomState == null ? void 0 : atomState.r) || 0,
      d: createReadDependencies(version, atomState == null ? void 0 : atomState.d, dependencies)
    };
    if (!atomState || !("v" in atomState) || !Object.is(atomState.v, value)) {
      ++nextAtomState.r;
      if (nextAtomState.d.has(atom)) {
        nextAtomState.d = new Map(nextAtomState.d).set(atom, nextAtomState.r);
      }
    } else if (nextAtomState.d !== atomState.d && (nextAtomState.d.size !== atomState.d.size || !Array.from(nextAtomState.d.keys()).every((a) => atomState.d.has(a)))) {
      Promise.resolve().then(() => {
        flushPending(version);
      });
    }
    setAtomState(version, atom, nextAtomState);
    return nextAtomState;
  };
  const setAtomReadError = (version, atom, error, dependencies, suspensePromise) => {
    const atomState = getAtomState(version, atom);
    if (atomState) {
      if (suspensePromise && (!("p" in atomState) || !isEqualSuspensePromise(atomState.p, suspensePromise))) {
        return atomState;
      }
      if ("p" in atomState) {
        cancelSuspensePromise(atomState.p);
      }
    }
    const nextAtomState = {
      e: error,
      r: (atomState == null ? void 0 : atomState.r) || 0,
      d: createReadDependencies(version, atomState == null ? void 0 : atomState.d, dependencies)
    };
    setAtomState(version, atom, nextAtomState);
    return nextAtomState;
  };
  const setAtomSuspensePromise = (version, atom, suspensePromise, dependencies) => {
    const atomState = getAtomState(version, atom);
    if (atomState && "p" in atomState) {
      if (isEqualSuspensePromise(atomState.p, suspensePromise)) {
        return atomState;
      }
      cancelSuspensePromise(atomState.p);
    }
    addSuspensePromiseToCache(version, atom, suspensePromise);
    const nextAtomState = {
      p: suspensePromise,
      r: (atomState == null ? void 0 : atomState.r) || 0,
      d: createReadDependencies(version, atomState == null ? void 0 : atomState.d, dependencies)
    };
    setAtomState(version, atom, nextAtomState);
    return nextAtomState;
  };
  const setAtomPromiseOrValue = (version, atom, promiseOrValue, dependencies) => {
    if (promiseOrValue instanceof Promise) {
      const suspensePromise = createSuspensePromise(promiseOrValue.then((value) => {
        setAtomValue(version, atom, value, dependencies, suspensePromise);
        flushPending(version);
      }).catch((e) => {
        if (e instanceof Promise) {
          if (isSuspensePromise(e)) {
            return e.then(() => {
              readAtomState(version, atom, true);
            });
          }
          return e;
        }
        setAtomReadError(version, atom, e, dependencies, suspensePromise);
        flushPending(version);
      }));
      return setAtomSuspensePromise(version, atom, suspensePromise, dependencies);
    }
    return setAtomValue(version, atom, promiseOrValue, dependencies);
  };
  const setAtomInvalidated = (version, atom) => {
    const atomState = getAtomState(version, atom);
    if (atomState) {
      const nextAtomState = __spreadProps$1(__spreadValues$1({}, atomState), {
        i: atomState.r
      });
      setAtomState(version, atom, nextAtomState);
    } else if (true) {
      console.warn("[Bug] could not invalidate non existing atom", atom);
    }
  };
  const readAtomState = (version, atom, force) => {
    if (!force) {
      const atomState = getAtomState(version, atom);
      if (atomState) {
        if (atomState.r !== atomState.i && "p" in atomState && !isSuspensePromiseAlreadyCancelled(atomState.p)) {
          return atomState;
        }
        atomState.d.forEach((_, a) => {
          if (a !== atom) {
            if (!mountedMap.has(a)) {
              readAtomState(version, a);
            } else {
              const aState = getAtomState(version, a);
              if (aState && aState.r === aState.i) {
                readAtomState(version, a);
              }
            }
          }
        });
        if (Array.from(atomState.d).every(([a, r]) => {
          const aState = getAtomState(version, a);
          return aState && "v" in aState && aState.r === r;
        })) {
          return atomState;
        }
      }
    }
    const dependencies = /* @__PURE__ */ new Set();
    try {
      const promiseOrValue = atom.read((a) => {
        dependencies.add(a);
        const aState = a === atom ? getAtomState(version, a) : readAtomState(version, a);
        if (aState) {
          if ("e" in aState) {
            throw aState.e;
          }
          if ("p" in aState) {
            throw aState.p;
          }
          return aState.v;
        }
        if (hasInitialValue(a)) {
          return a.init;
        }
        throw new Error("no atom init");
      });
      return setAtomPromiseOrValue(version, atom, promiseOrValue, dependencies);
    } catch (errorOrPromise) {
      if (errorOrPromise instanceof Promise) {
        const suspensePromise = createSuspensePromise(errorOrPromise);
        return setAtomSuspensePromise(version, atom, suspensePromise, dependencies);
      }
      return setAtomReadError(version, atom, errorOrPromise, dependencies);
    }
  };
  const readAtom = (readingAtom, version) => {
    const atomState = readAtomState(version, readingAtom);
    return atomState;
  };
  const addAtom = (addingAtom) => {
    let mounted = mountedMap.get(addingAtom);
    if (!mounted) {
      mounted = mountAtom(addingAtom);
    }
    return mounted;
  };
  const canUnmountAtom = (atom, mounted) => !mounted.l.size && (!mounted.t.size || mounted.t.size === 1 && mounted.t.has(atom));
  const delAtom = (deletingAtom) => {
    const mounted = mountedMap.get(deletingAtom);
    if (mounted && canUnmountAtom(deletingAtom, mounted)) {
      unmountAtom(deletingAtom);
    }
  };
  const invalidateDependents = (version, atom) => {
    const mounted = mountedMap.get(atom);
    mounted == null ? void 0 : mounted.t.forEach((dependent) => {
      if (dependent !== atom) {
        setAtomInvalidated(version, dependent);
        invalidateDependents(version, dependent);
      }
    });
  };
  const writeAtomState = (version, atom, update) => {
    let isSync = true;
    const writeGetter = (a, options) => {
      const aState = readAtomState(version, a);
      if ("e" in aState) {
        throw aState.e;
      }
      if ("p" in aState) {
        if (options == null ? void 0 : options.unstable_promise) {
          return aState.p.then(() => writeGetter(a, options));
        }
        if (true) {
          console.info("Reading pending atom state in write operation. We throw a promise for now.", a);
        }
        throw aState.p;
      }
      if ("v" in aState) {
        return aState.v;
      }
      if (true) {
        console.warn("[Bug] no value found while reading atom in write operation. This is probably a bug.", a);
      }
      throw new Error("no value found");
    };
    const setter = (a, v) => {
      let promiseOrVoid2;
      if (a === atom) {
        if (!hasInitialValue(a)) {
          throw new Error("atom not writable");
        }
        const versionSet = cancelAllSuspensePromiseInCache(a);
        versionSet.forEach((cancelledVersion) => {
          if (cancelledVersion !== version) {
            setAtomPromiseOrValue(cancelledVersion, a, v);
          }
        });
        setAtomPromiseOrValue(version, a, v);
        invalidateDependents(version, a);
      } else {
        promiseOrVoid2 = writeAtomState(version, a, v);
      }
      if (!isSync) {
        flushPending(version);
      }
      return promiseOrVoid2;
    };
    const promiseOrVoid = atom.write(writeGetter, setter, update);
    isSync = false;
    version = void 0;
    return promiseOrVoid;
  };
  const writeAtom = (writingAtom, update, version) => {
    const promiseOrVoid = writeAtomState(version, writingAtom, update);
    flushPending(version);
    return promiseOrVoid;
  };
  const isActuallyWritableAtom = (atom) => !!atom.write;
  const mountAtom = (atom, initialDependent) => {
    const mounted = {
      t: new Set(initialDependent && [initialDependent]),
      l: /* @__PURE__ */ new Set()
    };
    mountedMap.set(atom, mounted);
    if (true) {
      mountedAtoms.add(atom);
    }
    const atomState = readAtomState(void 0, atom);
    atomState.d.forEach((_, a) => {
      const aMounted = mountedMap.get(a);
      if (aMounted) {
        aMounted.t.add(atom);
      } else {
        if (a !== atom) {
          mountAtom(a, atom);
        }
      }
    });
    if (isActuallyWritableAtom(atom) && atom.onMount) {
      const setAtom = (update) => writeAtom(atom, update);
      const onUnmount = atom.onMount(setAtom);
      if (onUnmount) {
        mounted.u = onUnmount;
      }
    }
    return mounted;
  };
  const unmountAtom = (atom) => {
    var _a;
    const onUnmount = (_a = mountedMap.get(atom)) == null ? void 0 : _a.u;
    if (onUnmount) {
      onUnmount();
    }
    mountedMap.delete(atom);
    if (true) {
      mountedAtoms.delete(atom);
    }
    const atomState = getAtomState(void 0, atom);
    if (atomState) {
      atomState.d.forEach((_, a) => {
        if (a !== atom) {
          const mounted = mountedMap.get(a);
          if (mounted) {
            mounted.t.delete(atom);
            if (canUnmountAtom(a, mounted)) {
              unmountAtom(a);
            }
          }
        }
      });
    } else if (true) {
      console.warn("[Bug] could not find atom state to unmount", atom);
    }
  };
  const mountDependencies = (atom, atomState, prevReadDependencies) => {
    const dependencies = new Set(atomState.d.keys());
    prevReadDependencies == null ? void 0 : prevReadDependencies.forEach((_, a) => {
      if (dependencies.has(a)) {
        dependencies.delete(a);
        return;
      }
      const mounted = mountedMap.get(a);
      if (mounted) {
        mounted.t.delete(atom);
        if (canUnmountAtom(a, mounted)) {
          unmountAtom(a);
        }
      }
    });
    dependencies.forEach((a) => {
      const mounted = mountedMap.get(a);
      if (mounted) {
        mounted.t.add(atom);
      } else if (mountedMap.has(atom)) {
        mountAtom(a, atom);
      }
    });
  };
  const flushPending = (version) => {
    if (version) {
      const versionedAtomStateMap = getVersionedAtomStateMap(version);
      versionedAtomStateMap.forEach((atomState, atom) => {
        if (atomState !== committedAtomStateMap.get(atom)) {
          const mounted = mountedMap.get(atom);
          mounted == null ? void 0 : mounted.l.forEach((listener) => listener(version));
        }
      });
      return;
    }
    while (pendingMap.size) {
      const pending = Array.from(pendingMap);
      pendingMap.clear();
      pending.forEach(([atom, prevAtomState]) => {
        const atomState = getAtomState(void 0, atom);
        if (atomState && atomState.d !== (prevAtomState == null ? void 0 : prevAtomState.d)) {
          mountDependencies(atom, atomState, prevAtomState == null ? void 0 : prevAtomState.d);
        }
        const mounted = mountedMap.get(atom);
        mounted == null ? void 0 : mounted.l.forEach((listener) => listener());
      });
    }
    if (true) {
      stateListeners.forEach((l) => l());
    }
  };
  const commitVersionedAtomStateMap = (version) => {
    const versionedAtomStateMap = getVersionedAtomStateMap(version);
    versionedAtomStateMap.forEach((atomState, atom) => {
      const prevAtomState = committedAtomStateMap.get(atom);
      if (atomState.r > ((prevAtomState == null ? void 0 : prevAtomState.r) || 0) || "v" in atomState && atomState.r === (prevAtomState == null ? void 0 : prevAtomState.r) && atomState.d !== (prevAtomState == null ? void 0 : prevAtomState.d)) {
        committedAtomStateMap.set(atom, atomState);
        if (atomState.d !== (prevAtomState == null ? void 0 : prevAtomState.d)) {
          mountDependencies(atom, atomState, prevAtomState == null ? void 0 : prevAtomState.d);
        }
      }
    });
  };
  const commitAtom = (_atom, version) => {
    if (version) {
      commitVersionedAtomStateMap(version);
    }
    flushPending(void 0);
  };
  const subscribeAtom = (atom, callback) => {
    const mounted = addAtom(atom);
    const listeners = mounted.l;
    listeners.add(callback);
    return () => {
      listeners.delete(callback);
      delAtom(atom);
    };
  };
  const restoreAtoms = (values, version) => {
    for (const [atom, value] of values) {
      if (hasInitialValue(atom)) {
        setAtomPromiseOrValue(version, atom, value);
        invalidateDependents(version, atom);
      }
    }
    flushPending(version);
  };
  if (true) {
    return {
      [READ_ATOM]: readAtom,
      [WRITE_ATOM]: writeAtom,
      [COMMIT_ATOM]: commitAtom,
      [SUBSCRIBE_ATOM]: subscribeAtom,
      [RESTORE_ATOMS]: restoreAtoms,
      [DEV_SUBSCRIBE_STATE]: (l) => {
        stateListeners.add(l);
        return () => {
          stateListeners.delete(l);
        };
      },
      [DEV_GET_MOUNTED_ATOMS]: () => mountedAtoms.values(),
      [DEV_GET_ATOM_STATE]: (a) => committedAtomStateMap.get(a),
      [DEV_GET_MOUNTED]: (a) => mountedMap.get(a)
    };
  }
  return {
    [READ_ATOM]: readAtom,
    [WRITE_ATOM]: writeAtom,
    [COMMIT_ATOM]: commitAtom,
    [SUBSCRIBE_ATOM]: subscribeAtom,
    [RESTORE_ATOMS]: restoreAtoms
  };
};
const createStoreForExport = (initialValues) => {
  const store = createStore(initialValues);
  const get = (atom) => {
    const atomState = store[READ_ATOM](atom);
    if ("e" in atomState) {
      throw atomState.e;
    }
    if ("p" in atomState) {
      return void 0;
    }
    return atomState.v;
  };
  const asyncGet = (atom) => new Promise((resolve, reject) => {
    const atomState = store[READ_ATOM](atom);
    if ("e" in atomState) {
      reject(atomState.e);
    } else if ("p" in atomState) {
      resolve(atomState.p.then(() => asyncGet(atom)));
    } else {
      resolve(atomState.v);
    }
  });
  const set = (atom, update) => store[WRITE_ATOM](atom, update);
  const sub = (atom, callback) => store[SUBSCRIBE_ATOM](atom, callback);
  return {
    get,
    asyncGet,
    set,
    sub,
    SECRET_INTERNAL_store: store
  };
};

const createScopeContainer = (initialValues, unstable_createStore) => {
  const store = unstable_createStore ? unstable_createStore(initialValues).SECRET_INTERNAL_store : createStore(initialValues);
  return { s: store };
};
const ScopeContextMap = /* @__PURE__ */ new Map();
const getScopeContext = (scope) => {
  if (!ScopeContextMap.has(scope)) {
    ScopeContextMap.set(scope, (0,react__WEBPACK_IMPORTED_MODULE_0__.createContext)(createScopeContainer()));
  }
  return ScopeContextMap.get(scope);
};

var __defProp = Object.defineProperty;
var __defProps = Object.defineProperties;
var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};
var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
const atomToPrintable = (atom) => atom.debugLabel || atom.toString();
const stateToPrintable = ([store, atoms]) => Object.fromEntries(atoms.flatMap((atom) => {
  var _a, _b;
  const mounted = (_a = store[DEV_GET_MOUNTED]) == null ? void 0 : _a.call(store, atom);
  if (!mounted) {
    return [];
  }
  const dependents = mounted.t;
  const atomState = ((_b = store[DEV_GET_ATOM_STATE]) == null ? void 0 : _b.call(store, atom)) || {};
  return [
    [
      atomToPrintable(atom),
      __spreadProps(__spreadValues(__spreadValues(__spreadValues({}, "e" in atomState && { error: atomState.e }), "p" in atomState && { promise: atomState.p }), "v" in atomState && { value: atomState.v }), {
        dependents: Array.from(dependents).map(atomToPrintable)
      })
    ]
  ];
}));
const useDebugState = (scopeContainer) => {
  const { s: store } = scopeContainer;
  const [atoms, setAtoms] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)([]);
  (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
    var _a;
    const callback = () => {
      var _a2;
      setAtoms(Array.from(((_a2 = store[DEV_GET_MOUNTED_ATOMS]) == null ? void 0 : _a2.call(store)) || []));
    };
    const unsubscribe = (_a = store[DEV_SUBSCRIBE_STATE]) == null ? void 0 : _a.call(store, callback);
    callback();
    return unsubscribe;
  }, [store]);
  (0,react__WEBPACK_IMPORTED_MODULE_0__.useDebugValue)([store, atoms], stateToPrintable);
};

const Provider = ({
  children,
  initialValues,
  scope,
  unstable_createStore,
  unstable_enableVersionedWrite
}) => {
  const [version, setVersion] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)();
  (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
    if (version) {
      scopeContainerRef.current.s[COMMIT_ATOM](null, version);
      delete version.p;
    }
  }, [version]);
  const scopeContainerRef = (0,react__WEBPACK_IMPORTED_MODULE_0__.useRef)();
  if (!scopeContainerRef.current) {
    scopeContainerRef.current = createScopeContainer(initialValues, unstable_createStore);
    if (unstable_enableVersionedWrite) {
      scopeContainerRef.current.w = (write) => {
        setVersion((parentVersion) => {
          const nextVersion = parentVersion ? { p: parentVersion } : {};
          write(nextVersion);
          return nextVersion;
        });
      };
    }
  }
  if ( true && !unstable_enableVersionedWrite) {
    useDebugState(scopeContainerRef.current);
  }
  const ScopeContainerContext = getScopeContext(scope);
  return (0,react__WEBPACK_IMPORTED_MODULE_0__.createElement)(ScopeContainerContext.Provider, {
    value: scopeContainerRef.current
  }, children);
};

let keyCount = 0;
function atom(read, write) {
  const key = `atom${++keyCount}`;
  const config = {
    toString: () => key
  };
  if (typeof read === "function") {
    config.read = read;
  } else {
    config.init = read;
    config.read = (get) => get(config);
    config.write = (get, set, update) => set(config, typeof update === "function" ? update(get(config)) : update);
  }
  if (write) {
    config.write = write;
  }
  return config;
}

function useAtomValue(atom, scope) {
  const ScopeContext = getScopeContext(scope);
  const { s: store } = (0,react__WEBPACK_IMPORTED_MODULE_0__.useContext)(ScopeContext);
  const getAtomValue = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)((version2) => {
    const atomState = store[READ_ATOM](atom, version2);
    if ("e" in atomState) {
      throw atomState.e;
    }
    if ("p" in atomState) {
      throw atomState.p;
    }
    if ("v" in atomState) {
      return atomState.v;
    }
    throw new Error("no atom value");
  }, [store, atom]);
  const [[version, value, atomFromUseReducer], rerenderIfChanged] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useReducer)((0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)((prev, nextVersion) => {
    const nextValue = getAtomValue(nextVersion);
    if (Object.is(prev[1], nextValue) && prev[2] === atom) {
      return prev;
    }
    return [nextVersion, nextValue, atom];
  }, [getAtomValue, atom]), void 0, () => {
    const initialVersion = void 0;
    const initialValue = getAtomValue(initialVersion);
    return [initialVersion, initialValue, atom];
  });
  if (atomFromUseReducer !== atom) {
    rerenderIfChanged(void 0);
  }
  (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
    const unsubscribe = store[SUBSCRIBE_ATOM](atom, rerenderIfChanged);
    rerenderIfChanged(void 0);
    return unsubscribe;
  }, [store, atom]);
  (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
    store[COMMIT_ATOM](atom, version);
  });
  (0,react__WEBPACK_IMPORTED_MODULE_0__.useDebugValue)(value);
  return value;
}

function useSetAtom(atom, scope) {
  const ScopeContext = getScopeContext(scope);
  const { s: store, w: versionedWrite } = (0,react__WEBPACK_IMPORTED_MODULE_0__.useContext)(ScopeContext);
  const setAtom = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)((update) => {
    if ( true && !("write" in atom)) {
      throw new Error("not writable atom");
    }
    const write = (version) => store[WRITE_ATOM](atom, update, version);
    return versionedWrite ? versionedWrite(write) : write();
  }, [store, versionedWrite, atom]);
  return setAtom;
}

function useAtom(atom, scope) {
  if ("scope" in atom) {
    console.warn("atom.scope is deprecated. Please do useAtom(atom, scope) instead.");
    scope = atom.scope;
  }
  return [
    useAtomValue(atom, scope),
    useSetAtom(atom, scope)
  ];
}




/***/ }),

/***/ 6068:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  "BrowserRouter": () => (/* binding */ BrowserRouter),
  "HashRouter": () => (/* binding */ HashRouter),
  "Link": () => (/* binding */ Link),
  "MemoryRouter": () => (/* reexport */ MemoryRouter),
  "NavLink": () => (/* binding */ NavLink),
  "Navigate": () => (/* reexport */ Navigate),
  "NavigationType": () => (/* reexport */ Action),
  "Outlet": () => (/* reexport */ Outlet),
  "Route": () => (/* reexport */ Route),
  "Router": () => (/* reexport */ Router),
  "Routes": () => (/* reexport */ Routes),
  "UNSAFE_LocationContext": () => (/* reexport */ LocationContext),
  "UNSAFE_NavigationContext": () => (/* reexport */ NavigationContext),
  "UNSAFE_RouteContext": () => (/* reexport */ RouteContext),
  "createPath": () => (/* reexport */ createPath),
  "createRoutesFromChildren": () => (/* reexport */ createRoutesFromChildren),
  "createSearchParams": () => (/* binding */ createSearchParams),
  "generatePath": () => (/* reexport */ generatePath),
  "matchPath": () => (/* reexport */ matchPath),
  "matchRoutes": () => (/* reexport */ matchRoutes),
  "parsePath": () => (/* reexport */ parsePath),
  "renderMatches": () => (/* reexport */ renderMatches),
  "resolvePath": () => (/* reexport */ resolvePath),
  "unstable_HistoryRouter": () => (/* binding */ HistoryRouter),
  "useHref": () => (/* reexport */ useHref),
  "useInRouterContext": () => (/* reexport */ useInRouterContext),
  "useLinkClickHandler": () => (/* binding */ useLinkClickHandler),
  "useLocation": () => (/* reexport */ useLocation),
  "useMatch": () => (/* reexport */ useMatch),
  "useNavigate": () => (/* reexport */ useNavigate),
  "useNavigationType": () => (/* reexport */ useNavigationType),
  "useOutlet": () => (/* reexport */ useOutlet),
  "useOutletContext": () => (/* reexport */ useOutletContext),
  "useParams": () => (/* reexport */ useParams),
  "useResolvedPath": () => (/* reexport */ useResolvedPath),
  "useRoutes": () => (/* reexport */ useRoutes),
  "useSearchParams": () => (/* binding */ useSearchParams)
});

// EXTERNAL MODULE: ./node_modules/react/index.js
var react = __webpack_require__(7294);
// EXTERNAL MODULE: ./node_modules/@babel/runtime/helpers/esm/extends.js
var esm_extends = __webpack_require__(7462);
;// CONCATENATED MODULE: ./node_modules/history/index.js


/**
 * Actions represent the type of change to a location value.
 *
 * @see https://github.com/remix-run/history/tree/main/docs/api-reference.md#action
 */
var Action;

(function (Action) {
  /**
   * A POP indicates a change to an arbitrary index in the history stack, such
   * as a back or forward navigation. It does not describe the direction of the
   * navigation, only that the current index changed.
   *
   * Note: This is the default action for newly created history objects.
   */
  Action["Pop"] = "POP";
  /**
   * A PUSH indicates a new entry being added to the history stack, such as when
   * a link is clicked and a new page loads. When this happens, all subsequent
   * entries in the stack are lost.
   */

  Action["Push"] = "PUSH";
  /**
   * A REPLACE indicates the entry at the current index in the history stack
   * being replaced by a new one.
   */

  Action["Replace"] = "REPLACE";
})(Action || (Action = {}));

var readOnly =  false ? 0 : function (obj) {
  return obj;
};

function warning(cond, message) {
  if (!cond) {
    // eslint-disable-next-line no-console
    if (typeof console !== 'undefined') console.warn(message);

    try {
      // Welcome to debugging history!
      //
      // This error is thrown as a convenience so you can more easily
      // find the source for a warning that appears in the console by
      // enabling "pause on exceptions" in your JavaScript debugger.
      throw new Error(message); // eslint-disable-next-line no-empty
    } catch (e) {}
  }
}

var BeforeUnloadEventType = 'beforeunload';
var HashChangeEventType = 'hashchange';
var PopStateEventType = 'popstate';
/**
 * Browser history stores the location in regular URLs. This is the standard for
 * most web apps, but it requires some configuration on the server to ensure you
 * serve the same app at multiple URLs.
 *
 * @see https://github.com/remix-run/history/tree/main/docs/api-reference.md#createbrowserhistory
 */

function createBrowserHistory(options) {
  if (options === void 0) {
    options = {};
  }

  var _options = options,
      _options$window = _options.window,
      window = _options$window === void 0 ? document.defaultView : _options$window;
  var globalHistory = window.history;

  function getIndexAndLocation() {
    var _window$location = window.location,
        pathname = _window$location.pathname,
        search = _window$location.search,
        hash = _window$location.hash;
    var state = globalHistory.state || {};
    return [state.idx, readOnly({
      pathname: pathname,
      search: search,
      hash: hash,
      state: state.usr || null,
      key: state.key || 'default'
    })];
  }

  var blockedPopTx = null;

  function handlePop() {
    if (blockedPopTx) {
      blockers.call(blockedPopTx);
      blockedPopTx = null;
    } else {
      var nextAction = Action.Pop;

      var _getIndexAndLocation = getIndexAndLocation(),
          nextIndex = _getIndexAndLocation[0],
          nextLocation = _getIndexAndLocation[1];

      if (blockers.length) {
        if (nextIndex != null) {
          var delta = index - nextIndex;

          if (delta) {
            // Revert the POP
            blockedPopTx = {
              action: nextAction,
              location: nextLocation,
              retry: function retry() {
                go(delta * -1);
              }
            };
            go(delta);
          }
        } else {
          // Trying to POP to a location with no index. We did not create
          // this location, so we can't effectively block the navigation.
           false ? 0 : void 0;
        }
      } else {
        applyTx(nextAction);
      }
    }
  }

  window.addEventListener(PopStateEventType, handlePop);
  var action = Action.Pop;

  var _getIndexAndLocation2 = getIndexAndLocation(),
      index = _getIndexAndLocation2[0],
      location = _getIndexAndLocation2[1];

  var listeners = createEvents();
  var blockers = createEvents();

  if (index == null) {
    index = 0;
    globalHistory.replaceState((0,esm_extends/* default */.Z)({}, globalHistory.state, {
      idx: index
    }), '');
  }

  function createHref(to) {
    return typeof to === 'string' ? to : createPath(to);
  } // state defaults to `null` because `window.history.state` does


  function getNextLocation(to, state) {
    if (state === void 0) {
      state = null;
    }

    return readOnly((0,esm_extends/* default */.Z)({
      pathname: location.pathname,
      hash: '',
      search: ''
    }, typeof to === 'string' ? parsePath(to) : to, {
      state: state,
      key: createKey()
    }));
  }

  function getHistoryStateAndUrl(nextLocation, index) {
    return [{
      usr: nextLocation.state,
      key: nextLocation.key,
      idx: index
    }, createHref(nextLocation)];
  }

  function allowTx(action, location, retry) {
    return !blockers.length || (blockers.call({
      action: action,
      location: location,
      retry: retry
    }), false);
  }

  function applyTx(nextAction) {
    action = nextAction;

    var _getIndexAndLocation3 = getIndexAndLocation();

    index = _getIndexAndLocation3[0];
    location = _getIndexAndLocation3[1];
    listeners.call({
      action: action,
      location: location
    });
  }

  function push(to, state) {
    var nextAction = Action.Push;
    var nextLocation = getNextLocation(to, state);

    function retry() {
      push(to, state);
    }

    if (allowTx(nextAction, nextLocation, retry)) {
      var _getHistoryStateAndUr = getHistoryStateAndUrl(nextLocation, index + 1),
          historyState = _getHistoryStateAndUr[0],
          url = _getHistoryStateAndUr[1]; // TODO: Support forced reloading
      // try...catch because iOS limits us to 100 pushState calls :/


      try {
        globalHistory.pushState(historyState, '', url);
      } catch (error) {
        // They are going to lose state here, but there is no real
        // way to warn them about it since the page will refresh...
        window.location.assign(url);
      }

      applyTx(nextAction);
    }
  }

  function replace(to, state) {
    var nextAction = Action.Replace;
    var nextLocation = getNextLocation(to, state);

    function retry() {
      replace(to, state);
    }

    if (allowTx(nextAction, nextLocation, retry)) {
      var _getHistoryStateAndUr2 = getHistoryStateAndUrl(nextLocation, index),
          historyState = _getHistoryStateAndUr2[0],
          url = _getHistoryStateAndUr2[1]; // TODO: Support forced reloading


      globalHistory.replaceState(historyState, '', url);
      applyTx(nextAction);
    }
  }

  function go(delta) {
    globalHistory.go(delta);
  }

  var history = {
    get action() {
      return action;
    },

    get location() {
      return location;
    },

    createHref: createHref,
    push: push,
    replace: replace,
    go: go,
    back: function back() {
      go(-1);
    },
    forward: function forward() {
      go(1);
    },
    listen: function listen(listener) {
      return listeners.push(listener);
    },
    block: function block(blocker) {
      var unblock = blockers.push(blocker);

      if (blockers.length === 1) {
        window.addEventListener(BeforeUnloadEventType, promptBeforeUnload);
      }

      return function () {
        unblock(); // Remove the beforeunload listener so the document may
        // still be salvageable in the pagehide event.
        // See https://html.spec.whatwg.org/#unloading-documents

        if (!blockers.length) {
          window.removeEventListener(BeforeUnloadEventType, promptBeforeUnload);
        }
      };
    }
  };
  return history;
}
/**
 * Hash history stores the location in window.location.hash. This makes it ideal
 * for situations where you don't want to send the location to the server for
 * some reason, either because you do cannot configure it or the URL space is
 * reserved for something else.
 *
 * @see https://github.com/remix-run/history/tree/main/docs/api-reference.md#createhashhistory
 */

function createHashHistory(options) {
  if (options === void 0) {
    options = {};
  }

  var _options2 = options,
      _options2$window = _options2.window,
      window = _options2$window === void 0 ? document.defaultView : _options2$window;
  var globalHistory = window.history;

  function getIndexAndLocation() {
    var _parsePath = parsePath(window.location.hash.substr(1)),
        _parsePath$pathname = _parsePath.pathname,
        pathname = _parsePath$pathname === void 0 ? '/' : _parsePath$pathname,
        _parsePath$search = _parsePath.search,
        search = _parsePath$search === void 0 ? '' : _parsePath$search,
        _parsePath$hash = _parsePath.hash,
        hash = _parsePath$hash === void 0 ? '' : _parsePath$hash;

    var state = globalHistory.state || {};
    return [state.idx, readOnly({
      pathname: pathname,
      search: search,
      hash: hash,
      state: state.usr || null,
      key: state.key || 'default'
    })];
  }

  var blockedPopTx = null;

  function handlePop() {
    if (blockedPopTx) {
      blockers.call(blockedPopTx);
      blockedPopTx = null;
    } else {
      var nextAction = Action.Pop;

      var _getIndexAndLocation4 = getIndexAndLocation(),
          nextIndex = _getIndexAndLocation4[0],
          nextLocation = _getIndexAndLocation4[1];

      if (blockers.length) {
        if (nextIndex != null) {
          var delta = index - nextIndex;

          if (delta) {
            // Revert the POP
            blockedPopTx = {
              action: nextAction,
              location: nextLocation,
              retry: function retry() {
                go(delta * -1);
              }
            };
            go(delta);
          }
        } else {
          // Trying to POP to a location with no index. We did not create
          // this location, so we can't effectively block the navigation.
           false ? 0 : void 0;
        }
      } else {
        applyTx(nextAction);
      }
    }
  }

  window.addEventListener(PopStateEventType, handlePop); // popstate does not fire on hashchange in IE 11 and old (trident) Edge
  // https://developer.mozilla.org/de/docs/Web/API/Window/popstate_event

  window.addEventListener(HashChangeEventType, function () {
    var _getIndexAndLocation5 = getIndexAndLocation(),
        nextLocation = _getIndexAndLocation5[1]; // Ignore extraneous hashchange events.


    if (createPath(nextLocation) !== createPath(location)) {
      handlePop();
    }
  });
  var action = Action.Pop;

  var _getIndexAndLocation6 = getIndexAndLocation(),
      index = _getIndexAndLocation6[0],
      location = _getIndexAndLocation6[1];

  var listeners = createEvents();
  var blockers = createEvents();

  if (index == null) {
    index = 0;
    globalHistory.replaceState((0,esm_extends/* default */.Z)({}, globalHistory.state, {
      idx: index
    }), '');
  }

  function getBaseHref() {
    var base = document.querySelector('base');
    var href = '';

    if (base && base.getAttribute('href')) {
      var url = window.location.href;
      var hashIndex = url.indexOf('#');
      href = hashIndex === -1 ? url : url.slice(0, hashIndex);
    }

    return href;
  }

  function createHref(to) {
    return getBaseHref() + '#' + (typeof to === 'string' ? to : createPath(to));
  }

  function getNextLocation(to, state) {
    if (state === void 0) {
      state = null;
    }

    return readOnly((0,esm_extends/* default */.Z)({
      pathname: location.pathname,
      hash: '',
      search: ''
    }, typeof to === 'string' ? parsePath(to) : to, {
      state: state,
      key: createKey()
    }));
  }

  function getHistoryStateAndUrl(nextLocation, index) {
    return [{
      usr: nextLocation.state,
      key: nextLocation.key,
      idx: index
    }, createHref(nextLocation)];
  }

  function allowTx(action, location, retry) {
    return !blockers.length || (blockers.call({
      action: action,
      location: location,
      retry: retry
    }), false);
  }

  function applyTx(nextAction) {
    action = nextAction;

    var _getIndexAndLocation7 = getIndexAndLocation();

    index = _getIndexAndLocation7[0];
    location = _getIndexAndLocation7[1];
    listeners.call({
      action: action,
      location: location
    });
  }

  function push(to, state) {
    var nextAction = Action.Push;
    var nextLocation = getNextLocation(to, state);

    function retry() {
      push(to, state);
    }

     false ? 0 : void 0;

    if (allowTx(nextAction, nextLocation, retry)) {
      var _getHistoryStateAndUr3 = getHistoryStateAndUrl(nextLocation, index + 1),
          historyState = _getHistoryStateAndUr3[0],
          url = _getHistoryStateAndUr3[1]; // TODO: Support forced reloading
      // try...catch because iOS limits us to 100 pushState calls :/


      try {
        globalHistory.pushState(historyState, '', url);
      } catch (error) {
        // They are going to lose state here, but there is no real
        // way to warn them about it since the page will refresh...
        window.location.assign(url);
      }

      applyTx(nextAction);
    }
  }

  function replace(to, state) {
    var nextAction = Action.Replace;
    var nextLocation = getNextLocation(to, state);

    function retry() {
      replace(to, state);
    }

     false ? 0 : void 0;

    if (allowTx(nextAction, nextLocation, retry)) {
      var _getHistoryStateAndUr4 = getHistoryStateAndUrl(nextLocation, index),
          historyState = _getHistoryStateAndUr4[0],
          url = _getHistoryStateAndUr4[1]; // TODO: Support forced reloading


      globalHistory.replaceState(historyState, '', url);
      applyTx(nextAction);
    }
  }

  function go(delta) {
    globalHistory.go(delta);
  }

  var history = {
    get action() {
      return action;
    },

    get location() {
      return location;
    },

    createHref: createHref,
    push: push,
    replace: replace,
    go: go,
    back: function back() {
      go(-1);
    },
    forward: function forward() {
      go(1);
    },
    listen: function listen(listener) {
      return listeners.push(listener);
    },
    block: function block(blocker) {
      var unblock = blockers.push(blocker);

      if (blockers.length === 1) {
        window.addEventListener(BeforeUnloadEventType, promptBeforeUnload);
      }

      return function () {
        unblock(); // Remove the beforeunload listener so the document may
        // still be salvageable in the pagehide event.
        // See https://html.spec.whatwg.org/#unloading-documents

        if (!blockers.length) {
          window.removeEventListener(BeforeUnloadEventType, promptBeforeUnload);
        }
      };
    }
  };
  return history;
}
/**
 * Memory history stores the current location in memory. It is designed for use
 * in stateful non-browser environments like tests and React Native.
 *
 * @see https://github.com/remix-run/history/tree/main/docs/api-reference.md#creatememoryhistory
 */

function createMemoryHistory(options) {
  if (options === void 0) {
    options = {};
  }

  var _options3 = options,
      _options3$initialEntr = _options3.initialEntries,
      initialEntries = _options3$initialEntr === void 0 ? ['/'] : _options3$initialEntr,
      initialIndex = _options3.initialIndex;
  var entries = initialEntries.map(function (entry) {
    var location = readOnly((0,esm_extends/* default */.Z)({
      pathname: '/',
      search: '',
      hash: '',
      state: null,
      key: createKey()
    }, typeof entry === 'string' ? parsePath(entry) : entry));
     false ? 0 : void 0;
    return location;
  });
  var index = clamp(initialIndex == null ? entries.length - 1 : initialIndex, 0, entries.length - 1);
  var action = Action.Pop;
  var location = entries[index];
  var listeners = createEvents();
  var blockers = createEvents();

  function createHref(to) {
    return typeof to === 'string' ? to : createPath(to);
  }

  function getNextLocation(to, state) {
    if (state === void 0) {
      state = null;
    }

    return readOnly((0,esm_extends/* default */.Z)({
      pathname: location.pathname,
      search: '',
      hash: ''
    }, typeof to === 'string' ? parsePath(to) : to, {
      state: state,
      key: createKey()
    }));
  }

  function allowTx(action, location, retry) {
    return !blockers.length || (blockers.call({
      action: action,
      location: location,
      retry: retry
    }), false);
  }

  function applyTx(nextAction, nextLocation) {
    action = nextAction;
    location = nextLocation;
    listeners.call({
      action: action,
      location: location
    });
  }

  function push(to, state) {
    var nextAction = Action.Push;
    var nextLocation = getNextLocation(to, state);

    function retry() {
      push(to, state);
    }

     false ? 0 : void 0;

    if (allowTx(nextAction, nextLocation, retry)) {
      index += 1;
      entries.splice(index, entries.length, nextLocation);
      applyTx(nextAction, nextLocation);
    }
  }

  function replace(to, state) {
    var nextAction = Action.Replace;
    var nextLocation = getNextLocation(to, state);

    function retry() {
      replace(to, state);
    }

     false ? 0 : void 0;

    if (allowTx(nextAction, nextLocation, retry)) {
      entries[index] = nextLocation;
      applyTx(nextAction, nextLocation);
    }
  }

  function go(delta) {
    var nextIndex = clamp(index + delta, 0, entries.length - 1);
    var nextAction = Action.Pop;
    var nextLocation = entries[nextIndex];

    function retry() {
      go(delta);
    }

    if (allowTx(nextAction, nextLocation, retry)) {
      index = nextIndex;
      applyTx(nextAction, nextLocation);
    }
  }

  var history = {
    get index() {
      return index;
    },

    get action() {
      return action;
    },

    get location() {
      return location;
    },

    createHref: createHref,
    push: push,
    replace: replace,
    go: go,
    back: function back() {
      go(-1);
    },
    forward: function forward() {
      go(1);
    },
    listen: function listen(listener) {
      return listeners.push(listener);
    },
    block: function block(blocker) {
      return blockers.push(blocker);
    }
  };
  return history;
} ////////////////////////////////////////////////////////////////////////////////
// UTILS
////////////////////////////////////////////////////////////////////////////////

function clamp(n, lowerBound, upperBound) {
  return Math.min(Math.max(n, lowerBound), upperBound);
}

function promptBeforeUnload(event) {
  // Cancel the event.
  event.preventDefault(); // Chrome (and legacy IE) requires returnValue to be set.

  event.returnValue = '';
}

function createEvents() {
  var handlers = [];
  return {
    get length() {
      return handlers.length;
    },

    push: function push(fn) {
      handlers.push(fn);
      return function () {
        handlers = handlers.filter(function (handler) {
          return handler !== fn;
        });
      };
    },
    call: function call(arg) {
      handlers.forEach(function (fn) {
        return fn && fn(arg);
      });
    }
  };
}

function createKey() {
  return Math.random().toString(36).substr(2, 8);
}
/**
 * Creates a string URL path from the given pathname, search, and hash components.
 *
 * @see https://github.com/remix-run/history/tree/main/docs/api-reference.md#createpath
 */


function createPath(_ref) {
  var _ref$pathname = _ref.pathname,
      pathname = _ref$pathname === void 0 ? '/' : _ref$pathname,
      _ref$search = _ref.search,
      search = _ref$search === void 0 ? '' : _ref$search,
      _ref$hash = _ref.hash,
      hash = _ref$hash === void 0 ? '' : _ref$hash;
  if (search && search !== '?') pathname += search.charAt(0) === '?' ? search : '?' + search;
  if (hash && hash !== '#') pathname += hash.charAt(0) === '#' ? hash : '#' + hash;
  return pathname;
}
/**
 * Parses a string URL path into its separate pathname, search, and hash components.
 *
 * @see https://github.com/remix-run/history/tree/main/docs/api-reference.md#parsepath
 */

function parsePath(path) {
  var parsedPath = {};

  if (path) {
    var hashIndex = path.indexOf('#');

    if (hashIndex >= 0) {
      parsedPath.hash = path.substr(hashIndex);
      path = path.substr(0, hashIndex);
    }

    var searchIndex = path.indexOf('?');

    if (searchIndex >= 0) {
      parsedPath.search = path.substr(searchIndex);
      path = path.substr(0, searchIndex);
    }

    if (path) {
      parsedPath.pathname = path;
    }
  }

  return parsedPath;
}


//# sourceMappingURL=index.js.map

;// CONCATENATED MODULE: ./node_modules/react-router/index.js
/**
 * React Router v6.3.0
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */




const NavigationContext = /*#__PURE__*/(0,react.createContext)(null);

if (false) {}

const LocationContext = /*#__PURE__*/(0,react.createContext)(null);

if (false) {}

const RouteContext = /*#__PURE__*/(0,react.createContext)({
  outlet: null,
  matches: []
});

if (false) {}

function invariant(cond, message) {
  if (!cond) throw new Error(message);
}
function react_router_warning(cond, message) {
  if (!cond) {
    // eslint-disable-next-line no-console
    if (typeof console !== "undefined") console.warn(message);

    try {
      // Welcome to debugging React Router!
      //
      // This error is thrown as a convenience so you can more easily
      // find the source for a warning that appears in the console by
      // enabling "pause on exceptions" in your JavaScript debugger.
      throw new Error(message); // eslint-disable-next-line no-empty
    } catch (e) {}
  }
}
const alreadyWarned = {};
function warningOnce(key, cond, message) {
  if (!cond && !alreadyWarned[key]) {
    alreadyWarned[key] = true;
     false ? 0 : void 0;
  }
}

/**
 * Returns a path with params interpolated.
 *
 * @see https://reactrouter.com/docs/en/v6/api#generatepath
 */
function generatePath(path, params) {
  if (params === void 0) {
    params = {};
  }

  return path.replace(/:(\w+)/g, (_, key) => {
    !(params[key] != null) ?  false ? 0 : invariant(false) : void 0;
    return params[key];
  }).replace(/\/*\*$/, _ => params["*"] == null ? "" : params["*"].replace(/^\/*/, "/"));
}
/**
 * A RouteMatch contains info about how a route matched a URL.
 */

/**
 * Matches the given routes to a location and returns the match data.
 *
 * @see https://reactrouter.com/docs/en/v6/api#matchroutes
 */
function matchRoutes(routes, locationArg, basename) {
  if (basename === void 0) {
    basename = "/";
  }

  let location = typeof locationArg === "string" ? parsePath(locationArg) : locationArg;
  let pathname = stripBasename(location.pathname || "/", basename);

  if (pathname == null) {
    return null;
  }

  let branches = flattenRoutes(routes);
  rankRouteBranches(branches);
  let matches = null;

  for (let i = 0; matches == null && i < branches.length; ++i) {
    matches = matchRouteBranch(branches[i], pathname);
  }

  return matches;
}

function flattenRoutes(routes, branches, parentsMeta, parentPath) {
  if (branches === void 0) {
    branches = [];
  }

  if (parentsMeta === void 0) {
    parentsMeta = [];
  }

  if (parentPath === void 0) {
    parentPath = "";
  }

  routes.forEach((route, index) => {
    let meta = {
      relativePath: route.path || "",
      caseSensitive: route.caseSensitive === true,
      childrenIndex: index,
      route
    };

    if (meta.relativePath.startsWith("/")) {
      !meta.relativePath.startsWith(parentPath) ?  false ? 0 : invariant(false) : void 0;
      meta.relativePath = meta.relativePath.slice(parentPath.length);
    }

    let path = joinPaths([parentPath, meta.relativePath]);
    let routesMeta = parentsMeta.concat(meta); // Add the children before adding this route to the array so we traverse the
    // route tree depth-first and child routes appear before their parents in
    // the "flattened" version.

    if (route.children && route.children.length > 0) {
      !(route.index !== true) ?  false ? 0 : invariant(false) : void 0;
      flattenRoutes(route.children, branches, routesMeta, path);
    } // Routes without a path shouldn't ever match by themselves unless they are
    // index routes, so don't add them to the list of possible branches.


    if (route.path == null && !route.index) {
      return;
    }

    branches.push({
      path,
      score: computeScore(path, route.index),
      routesMeta
    });
  });
  return branches;
}

function rankRouteBranches(branches) {
  branches.sort((a, b) => a.score !== b.score ? b.score - a.score // Higher score first
  : compareIndexes(a.routesMeta.map(meta => meta.childrenIndex), b.routesMeta.map(meta => meta.childrenIndex)));
}

const paramRe = /^:\w+$/;
const dynamicSegmentValue = 3;
const indexRouteValue = 2;
const emptySegmentValue = 1;
const staticSegmentValue = 10;
const splatPenalty = -2;

const isSplat = s => s === "*";

function computeScore(path, index) {
  let segments = path.split("/");
  let initialScore = segments.length;

  if (segments.some(isSplat)) {
    initialScore += splatPenalty;
  }

  if (index) {
    initialScore += indexRouteValue;
  }

  return segments.filter(s => !isSplat(s)).reduce((score, segment) => score + (paramRe.test(segment) ? dynamicSegmentValue : segment === "" ? emptySegmentValue : staticSegmentValue), initialScore);
}

function compareIndexes(a, b) {
  let siblings = a.length === b.length && a.slice(0, -1).every((n, i) => n === b[i]);
  return siblings ? // If two routes are siblings, we should try to match the earlier sibling
  // first. This allows people to have fine-grained control over the matching
  // behavior by simply putting routes with identical paths in the order they
  // want them tried.
  a[a.length - 1] - b[b.length - 1] : // Otherwise, it doesn't really make sense to rank non-siblings by index,
  // so they sort equally.
  0;
}

function matchRouteBranch(branch, pathname) {
  let {
    routesMeta
  } = branch;
  let matchedParams = {};
  let matchedPathname = "/";
  let matches = [];

  for (let i = 0; i < routesMeta.length; ++i) {
    let meta = routesMeta[i];
    let end = i === routesMeta.length - 1;
    let remainingPathname = matchedPathname === "/" ? pathname : pathname.slice(matchedPathname.length) || "/";
    let match = matchPath({
      path: meta.relativePath,
      caseSensitive: meta.caseSensitive,
      end
    }, remainingPathname);
    if (!match) return null;
    Object.assign(matchedParams, match.params);
    let route = meta.route;
    matches.push({
      params: matchedParams,
      pathname: joinPaths([matchedPathname, match.pathname]),
      pathnameBase: normalizePathname(joinPaths([matchedPathname, match.pathnameBase])),
      route
    });

    if (match.pathnameBase !== "/") {
      matchedPathname = joinPaths([matchedPathname, match.pathnameBase]);
    }
  }

  return matches;
}
/**
 * A PathPattern is used to match on some portion of a URL pathname.
 */


/**
 * Performs pattern matching on a URL pathname and returns information about
 * the match.
 *
 * @see https://reactrouter.com/docs/en/v6/api#matchpath
 */
function matchPath(pattern, pathname) {
  if (typeof pattern === "string") {
    pattern = {
      path: pattern,
      caseSensitive: false,
      end: true
    };
  }

  let [matcher, paramNames] = compilePath(pattern.path, pattern.caseSensitive, pattern.end);
  let match = pathname.match(matcher);
  if (!match) return null;
  let matchedPathname = match[0];
  let pathnameBase = matchedPathname.replace(/(.)\/+$/, "$1");
  let captureGroups = match.slice(1);
  let params = paramNames.reduce((memo, paramName, index) => {
    // We need to compute the pathnameBase here using the raw splat value
    // instead of using params["*"] later because it will be decoded then
    if (paramName === "*") {
      let splatValue = captureGroups[index] || "";
      pathnameBase = matchedPathname.slice(0, matchedPathname.length - splatValue.length).replace(/(.)\/+$/, "$1");
    }

    memo[paramName] = safelyDecodeURIComponent(captureGroups[index] || "", paramName);
    return memo;
  }, {});
  return {
    params,
    pathname: matchedPathname,
    pathnameBase,
    pattern
  };
}

function compilePath(path, caseSensitive, end) {
  if (caseSensitive === void 0) {
    caseSensitive = false;
  }

  if (end === void 0) {
    end = true;
  }

   false ? 0 : void 0;
  let paramNames = [];
  let regexpSource = "^" + path.replace(/\/*\*?$/, "") // Ignore trailing / and /*, we'll handle it below
  .replace(/^\/*/, "/") // Make sure it has a leading /
  .replace(/[\\.*+^$?{}|()[\]]/g, "\\$&") // Escape special regex chars
  .replace(/:(\w+)/g, (_, paramName) => {
    paramNames.push(paramName);
    return "([^\\/]+)";
  });

  if (path.endsWith("*")) {
    paramNames.push("*");
    regexpSource += path === "*" || path === "/*" ? "(.*)$" // Already matched the initial /, just match the rest
    : "(?:\\/(.+)|\\/*)$"; // Don't include the / in params["*"]
  } else {
    regexpSource += end ? "\\/*$" // When matching to the end, ignore trailing slashes
    : // Otherwise, match a word boundary or a proceeding /. The word boundary restricts
    // parent routes to matching only their own words and nothing more, e.g. parent
    // route "/home" should not match "/home2".
    // Additionally, allow paths starting with `.`, `-`, `~`, and url-encoded entities,
    // but do not consume the character in the matched path so they can match against
    // nested paths.
    "(?:(?=[.~-]|%[0-9A-F]{2})|\\b|\\/|$)";
  }

  let matcher = new RegExp(regexpSource, caseSensitive ? undefined : "i");
  return [matcher, paramNames];
}

function safelyDecodeURIComponent(value, paramName) {
  try {
    return decodeURIComponent(value);
  } catch (error) {
     false ? 0 : void 0;
    return value;
  }
}
/**
 * Returns a resolved path object relative to the given pathname.
 *
 * @see https://reactrouter.com/docs/en/v6/api#resolvepath
 */


function resolvePath(to, fromPathname) {
  if (fromPathname === void 0) {
    fromPathname = "/";
  }

  let {
    pathname: toPathname,
    search = "",
    hash = ""
  } = typeof to === "string" ? parsePath(to) : to;
  let pathname = toPathname ? toPathname.startsWith("/") ? toPathname : resolvePathname(toPathname, fromPathname) : fromPathname;
  return {
    pathname,
    search: normalizeSearch(search),
    hash: normalizeHash(hash)
  };
}

function resolvePathname(relativePath, fromPathname) {
  let segments = fromPathname.replace(/\/+$/, "").split("/");
  let relativeSegments = relativePath.split("/");
  relativeSegments.forEach(segment => {
    if (segment === "..") {
      // Keep the root "" segment so the pathname starts at /
      if (segments.length > 1) segments.pop();
    } else if (segment !== ".") {
      segments.push(segment);
    }
  });
  return segments.length > 1 ? segments.join("/") : "/";
}

function resolveTo(toArg, routePathnames, locationPathname) {
  let to = typeof toArg === "string" ? parsePath(toArg) : toArg;
  let toPathname = toArg === "" || to.pathname === "" ? "/" : to.pathname; // If a pathname is explicitly provided in `to`, it should be relative to the
  // route context. This is explained in `Note on `<Link to>` values` in our
  // migration guide from v5 as a means of disambiguation between `to` values
  // that begin with `/` and those that do not. However, this is problematic for
  // `to` values that do not provide a pathname. `to` can simply be a search or
  // hash string, in which case we should assume that the navigation is relative
  // to the current location's pathname and *not* the route pathname.

  let from;

  if (toPathname == null) {
    from = locationPathname;
  } else {
    let routePathnameIndex = routePathnames.length - 1;

    if (toPathname.startsWith("..")) {
      let toSegments = toPathname.split("/"); // Each leading .. segment means "go up one route" instead of "go up one
      // URL segment".  This is a key difference from how <a href> works and a
      // major reason we call this a "to" value instead of a "href".

      while (toSegments[0] === "..") {
        toSegments.shift();
        routePathnameIndex -= 1;
      }

      to.pathname = toSegments.join("/");
    } // If there are more ".." segments than parent routes, resolve relative to
    // the root / URL.


    from = routePathnameIndex >= 0 ? routePathnames[routePathnameIndex] : "/";
  }

  let path = resolvePath(to, from); // Ensure the pathname has a trailing slash if the original to value had one.

  if (toPathname && toPathname !== "/" && toPathname.endsWith("/") && !path.pathname.endsWith("/")) {
    path.pathname += "/";
  }

  return path;
}
function getToPathname(to) {
  // Empty strings should be treated the same as / paths
  return to === "" || to.pathname === "" ? "/" : typeof to === "string" ? parsePath(to).pathname : to.pathname;
}
function stripBasename(pathname, basename) {
  if (basename === "/") return pathname;

  if (!pathname.toLowerCase().startsWith(basename.toLowerCase())) {
    return null;
  }

  let nextChar = pathname.charAt(basename.length);

  if (nextChar && nextChar !== "/") {
    // pathname does not start with basename/
    return null;
  }

  return pathname.slice(basename.length) || "/";
}
const joinPaths = paths => paths.join("/").replace(/\/\/+/g, "/");
const normalizePathname = pathname => pathname.replace(/\/+$/, "").replace(/^\/*/, "/");

const normalizeSearch = search => !search || search === "?" ? "" : search.startsWith("?") ? search : "?" + search;

const normalizeHash = hash => !hash || hash === "#" ? "" : hash.startsWith("#") ? hash : "#" + hash;

/**
 * Returns the full href for the given "to" value. This is useful for building
 * custom links that are also accessible and preserve right-click behavior.
 *
 * @see https://reactrouter.com/docs/en/v6/api#usehref
 */

function useHref(to) {
  !useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
  let {
    basename,
    navigator
  } = (0,react.useContext)(NavigationContext);
  let {
    hash,
    pathname,
    search
  } = useResolvedPath(to);
  let joinedPathname = pathname;

  if (basename !== "/") {
    let toPathname = getToPathname(to);
    let endsWithSlash = toPathname != null && toPathname.endsWith("/");
    joinedPathname = pathname === "/" ? basename + (endsWithSlash ? "/" : "") : joinPaths([basename, pathname]);
  }

  return navigator.createHref({
    pathname: joinedPathname,
    search,
    hash
  });
}
/**
 * Returns true if this component is a descendant of a <Router>.
 *
 * @see https://reactrouter.com/docs/en/v6/api#useinroutercontext
 */

function useInRouterContext() {
  return (0,react.useContext)(LocationContext) != null;
}
/**
 * Returns the current location object, which represents the current URL in web
 * browsers.
 *
 * Note: If you're using this it may mean you're doing some of your own
 * "routing" in your app, and we'd like to know what your use case is. We may
 * be able to provide something higher-level to better suit your needs.
 *
 * @see https://reactrouter.com/docs/en/v6/api#uselocation
 */

function useLocation() {
  !useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
  return (0,react.useContext)(LocationContext).location;
}
/**
 * Returns the current navigation action which describes how the router came to
 * the current location, either by a pop, push, or replace on the history stack.
 *
 * @see https://reactrouter.com/docs/en/v6/api#usenavigationtype
 */

function useNavigationType() {
  return (0,react.useContext)(LocationContext).navigationType;
}
/**
 * Returns true if the URL for the given "to" value matches the current URL.
 * This is useful for components that need to know "active" state, e.g.
 * <NavLink>.
 *
 * @see https://reactrouter.com/docs/en/v6/api#usematch
 */

function useMatch(pattern) {
  !useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
  let {
    pathname
  } = useLocation();
  return (0,react.useMemo)(() => matchPath(pattern, pathname), [pathname, pattern]);
}
/**
 * The interface for the navigate() function returned from useNavigate().
 */

/**
 * Returns an imperative method for changing the location. Used by <Link>s, but
 * may also be used by other elements to change the location.
 *
 * @see https://reactrouter.com/docs/en/v6/api#usenavigate
 */
function useNavigate() {
  !useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
  let {
    basename,
    navigator
  } = (0,react.useContext)(NavigationContext);
  let {
    matches
  } = (0,react.useContext)(RouteContext);
  let {
    pathname: locationPathname
  } = useLocation();
  let routePathnamesJson = JSON.stringify(matches.map(match => match.pathnameBase));
  let activeRef = (0,react.useRef)(false);
  (0,react.useEffect)(() => {
    activeRef.current = true;
  });
  let navigate = (0,react.useCallback)(function (to, options) {
    if (options === void 0) {
      options = {};
    }

     false ? 0 : void 0;
    if (!activeRef.current) return;

    if (typeof to === "number") {
      navigator.go(to);
      return;
    }

    let path = resolveTo(to, JSON.parse(routePathnamesJson), locationPathname);

    if (basename !== "/") {
      path.pathname = joinPaths([basename, path.pathname]);
    }

    (!!options.replace ? navigator.replace : navigator.push)(path, options.state);
  }, [basename, navigator, routePathnamesJson, locationPathname]);
  return navigate;
}
const OutletContext = /*#__PURE__*/(0,react.createContext)(null);
/**
 * Returns the context (if provided) for the child route at this level of the route
 * hierarchy.
 * @see https://reactrouter.com/docs/en/v6/api#useoutletcontext
 */

function useOutletContext() {
  return (0,react.useContext)(OutletContext);
}
/**
 * Returns the element for the child route at this level of the route
 * hierarchy. Used internally by <Outlet> to render child routes.
 *
 * @see https://reactrouter.com/docs/en/v6/api#useoutlet
 */

function useOutlet(context) {
  let outlet = (0,react.useContext)(RouteContext).outlet;

  if (outlet) {
    return /*#__PURE__*/(0,react.createElement)(OutletContext.Provider, {
      value: context
    }, outlet);
  }

  return outlet;
}
/**
 * Returns an object of key/value pairs of the dynamic params from the current
 * URL that were matched by the route path.
 *
 * @see https://reactrouter.com/docs/en/v6/api#useparams
 */

function useParams() {
  let {
    matches
  } = (0,react.useContext)(RouteContext);
  let routeMatch = matches[matches.length - 1];
  return routeMatch ? routeMatch.params : {};
}
/**
 * Resolves the pathname of the given `to` value against the current location.
 *
 * @see https://reactrouter.com/docs/en/v6/api#useresolvedpath
 */

function useResolvedPath(to) {
  let {
    matches
  } = (0,react.useContext)(RouteContext);
  let {
    pathname: locationPathname
  } = useLocation();
  let routePathnamesJson = JSON.stringify(matches.map(match => match.pathnameBase));
  return (0,react.useMemo)(() => resolveTo(to, JSON.parse(routePathnamesJson), locationPathname), [to, routePathnamesJson, locationPathname]);
}
/**
 * Returns the element of the route that matched the current location, prepared
 * with the correct context to render the remainder of the route tree. Route
 * elements in the tree must render an <Outlet> to render their child route's
 * element.
 *
 * @see https://reactrouter.com/docs/en/v6/api#useroutes
 */

function useRoutes(routes, locationArg) {
  !useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
  let {
    matches: parentMatches
  } = (0,react.useContext)(RouteContext);
  let routeMatch = parentMatches[parentMatches.length - 1];
  let parentParams = routeMatch ? routeMatch.params : {};
  let parentPathname = routeMatch ? routeMatch.pathname : "/";
  let parentPathnameBase = routeMatch ? routeMatch.pathnameBase : "/";
  let parentRoute = routeMatch && routeMatch.route;

  if (false) {}

  let locationFromContext = useLocation();
  let location;

  if (locationArg) {
    var _parsedLocationArg$pa;

    let parsedLocationArg = typeof locationArg === "string" ? parsePath(locationArg) : locationArg;
    !(parentPathnameBase === "/" || ((_parsedLocationArg$pa = parsedLocationArg.pathname) == null ? void 0 : _parsedLocationArg$pa.startsWith(parentPathnameBase))) ?  false ? 0 : invariant(false) : void 0;
    location = parsedLocationArg;
  } else {
    location = locationFromContext;
  }

  let pathname = location.pathname || "/";
  let remainingPathname = parentPathnameBase === "/" ? pathname : pathname.slice(parentPathnameBase.length) || "/";
  let matches = matchRoutes(routes, {
    pathname: remainingPathname
  });

  if (false) {}

  return _renderMatches(matches && matches.map(match => Object.assign({}, match, {
    params: Object.assign({}, parentParams, match.params),
    pathname: joinPaths([parentPathnameBase, match.pathname]),
    pathnameBase: match.pathnameBase === "/" ? parentPathnameBase : joinPaths([parentPathnameBase, match.pathnameBase])
  })), parentMatches);
}
function _renderMatches(matches, parentMatches) {
  if (parentMatches === void 0) {
    parentMatches = [];
  }

  if (matches == null) return null;
  return matches.reduceRight((outlet, match, index) => {
    return /*#__PURE__*/(0,react.createElement)(RouteContext.Provider, {
      children: match.route.element !== undefined ? match.route.element : outlet,
      value: {
        outlet,
        matches: parentMatches.concat(matches.slice(0, index + 1))
      }
    });
  }, null);
}

/**
 * A <Router> that stores all entries in memory.
 *
 * @see https://reactrouter.com/docs/en/v6/api#memoryrouter
 */
function MemoryRouter(_ref) {
  let {
    basename,
    children,
    initialEntries,
    initialIndex
  } = _ref;
  let historyRef = (0,react.useRef)();

  if (historyRef.current == null) {
    historyRef.current = createMemoryHistory({
      initialEntries,
      initialIndex
    });
  }

  let history = historyRef.current;
  let [state, setState] = (0,react.useState)({
    action: history.action,
    location: history.location
  });
  (0,react.useLayoutEffect)(() => history.listen(setState), [history]);
  return /*#__PURE__*/(0,react.createElement)(Router, {
    basename: basename,
    children: children,
    location: state.location,
    navigationType: state.action,
    navigator: history
  });
}

/**
 * Changes the current location.
 *
 * Note: This API is mostly useful in React.Component subclasses that are not
 * able to use hooks. In functional components, we recommend you use the
 * `useNavigate` hook instead.
 *
 * @see https://reactrouter.com/docs/en/v6/api#navigate
 */
function Navigate(_ref2) {
  let {
    to,
    replace,
    state
  } = _ref2;
  !useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
   false ? 0 : void 0;
  let navigate = useNavigate();
  (0,react.useEffect)(() => {
    navigate(to, {
      replace,
      state
    });
  });
  return null;
}

/**
 * Renders the child route's element, if there is one.
 *
 * @see https://reactrouter.com/docs/en/v6/api#outlet
 */
function Outlet(props) {
  return useOutlet(props.context);
}

/**
 * Declares an element that should be rendered at a certain URL path.
 *
 * @see https://reactrouter.com/docs/en/v6/api#route
 */
function Route(_props) {
    false ? 0 : invariant(false) ;
}

/**
 * Provides location context for the rest of the app.
 *
 * Note: You usually won't render a <Router> directly. Instead, you'll render a
 * router that is more specific to your environment such as a <BrowserRouter>
 * in web browsers or a <StaticRouter> for server rendering.
 *
 * @see https://reactrouter.com/docs/en/v6/api#router
 */
function Router(_ref3) {
  let {
    basename: basenameProp = "/",
    children = null,
    location: locationProp,
    navigationType = Action.Pop,
    navigator,
    static: staticProp = false
  } = _ref3;
  !!useInRouterContext() ?  false ? 0 : invariant(false) : void 0;
  let basename = normalizePathname(basenameProp);
  let navigationContext = (0,react.useMemo)(() => ({
    basename,
    navigator,
    static: staticProp
  }), [basename, navigator, staticProp]);

  if (typeof locationProp === "string") {
    locationProp = parsePath(locationProp);
  }

  let {
    pathname = "/",
    search = "",
    hash = "",
    state = null,
    key = "default"
  } = locationProp;
  let location = (0,react.useMemo)(() => {
    let trailingPathname = stripBasename(pathname, basename);

    if (trailingPathname == null) {
      return null;
    }

    return {
      pathname: trailingPathname,
      search,
      hash,
      state,
      key
    };
  }, [basename, pathname, search, hash, state, key]);
   false ? 0 : void 0;

  if (location == null) {
    return null;
  }

  return /*#__PURE__*/(0,react.createElement)(NavigationContext.Provider, {
    value: navigationContext
  }, /*#__PURE__*/(0,react.createElement)(LocationContext.Provider, {
    children: children,
    value: {
      location,
      navigationType
    }
  }));
}

/**
 * A container for a nested tree of <Route> elements that renders the branch
 * that best matches the current location.
 *
 * @see https://reactrouter.com/docs/en/v6/api#routes
 */
function Routes(_ref4) {
  let {
    children,
    location
  } = _ref4;
  return useRoutes(createRoutesFromChildren(children), location);
} ///////////////////////////////////////////////////////////////////////////////
// UTILS
///////////////////////////////////////////////////////////////////////////////

/**
 * Creates a route config from a React "children" object, which is usually
 * either a `<Route>` element or an array of them. Used internally by
 * `<Routes>` to create a route config from its children.
 *
 * @see https://reactrouter.com/docs/en/v6/api#createroutesfromchildren
 */

function createRoutesFromChildren(children) {
  let routes = [];
  react.Children.forEach(children, element => {
    if (! /*#__PURE__*/(0,react.isValidElement)(element)) {
      // Ignore non-elements. This allows people to more easily inline
      // conditionals in their route config.
      return;
    }

    if (element.type === react.Fragment) {
      // Transparently support React.Fragment and its children.
      routes.push.apply(routes, createRoutesFromChildren(element.props.children));
      return;
    }

    !(element.type === Route) ?  false ? 0 : invariant(false) : void 0;
    let route = {
      caseSensitive: element.props.caseSensitive,
      element: element.props.element,
      index: element.props.index,
      path: element.props.path
    };

    if (element.props.children) {
      route.children = createRoutesFromChildren(element.props.children);
    }

    routes.push(route);
  });
  return routes;
}
/**
 * Renders the result of `matchRoutes()` into a React element.
 */

function renderMatches(matches) {
  return _renderMatches(matches);
}


//# sourceMappingURL=index.js.map

;// CONCATENATED MODULE: ./node_modules/react-router-dom/index.js
/**
 * React Router DOM v6.3.0
 *
 * Copyright (c) Remix Software Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE.md file in the root directory of this source tree.
 *
 * @license MIT
 */





function _extends() {
  _extends = Object.assign || function (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];

      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }

    return target;
  };

  return _extends.apply(this, arguments);
}

function _objectWithoutPropertiesLoose(source, excluded) {
  if (source == null) return {};
  var target = {};
  var sourceKeys = Object.keys(source);
  var key, i;

  for (i = 0; i < sourceKeys.length; i++) {
    key = sourceKeys[i];
    if (excluded.indexOf(key) >= 0) continue;
    target[key] = source[key];
  }

  return target;
}

const _excluded = ["onClick", "reloadDocument", "replace", "state", "target", "to"],
      _excluded2 = ["aria-current", "caseSensitive", "className", "end", "style", "to", "children"];

function react_router_dom_warning(cond, message) {
  if (!cond) {
    // eslint-disable-next-line no-console
    if (typeof console !== "undefined") console.warn(message);

    try {
      // Welcome to debugging React Router!
      //
      // This error is thrown as a convenience so you can more easily
      // find the source for a warning that appears in the console by
      // enabling "pause on exceptions" in your JavaScript debugger.
      throw new Error(message); // eslint-disable-next-line no-empty
    } catch (e) {}
  }
} ////////////////////////////////////////////////////////////////////////////////
// COMPONENTS
////////////////////////////////////////////////////////////////////////////////

/**
 * A `<Router>` for use in web browsers. Provides the cleanest URLs.
 */
function BrowserRouter(_ref) {
  let {
    basename,
    children,
    window
  } = _ref;
  let historyRef = (0,react.useRef)();

  if (historyRef.current == null) {
    historyRef.current = createBrowserHistory({
      window
    });
  }

  let history = historyRef.current;
  let [state, setState] = (0,react.useState)({
    action: history.action,
    location: history.location
  });
  (0,react.useLayoutEffect)(() => history.listen(setState), [history]);
  return /*#__PURE__*/(0,react.createElement)(Router, {
    basename: basename,
    children: children,
    location: state.location,
    navigationType: state.action,
    navigator: history
  });
}

/**
 * A `<Router>` for use in web browsers. Stores the location in the hash
 * portion of the URL so it is not sent to the server.
 */
function HashRouter(_ref2) {
  let {
    basename,
    children,
    window
  } = _ref2;
  let historyRef = (0,react.useRef)();

  if (historyRef.current == null) {
    historyRef.current = createHashHistory({
      window
    });
  }

  let history = historyRef.current;
  let [state, setState] = (0,react.useState)({
    action: history.action,
    location: history.location
  });
  (0,react.useLayoutEffect)(() => history.listen(setState), [history]);
  return /*#__PURE__*/(0,react.createElement)(Router, {
    basename: basename,
    children: children,
    location: state.location,
    navigationType: state.action,
    navigator: history
  });
}

/**
 * A `<Router>` that accepts a pre-instantiated history object. It's important
 * to note that using your own history object is highly discouraged and may add
 * two versions of the history library to your bundles unless you use the same
 * version of the history library that React Router uses internally.
 */
function HistoryRouter(_ref3) {
  let {
    basename,
    children,
    history
  } = _ref3;
  const [state, setState] = (0,react.useState)({
    action: history.action,
    location: history.location
  });
  (0,react.useLayoutEffect)(() => history.listen(setState), [history]);
  return /*#__PURE__*/(0,react.createElement)(Router, {
    basename: basename,
    children: children,
    location: state.location,
    navigationType: state.action,
    navigator: history
  });
}

if (false) {}

function isModifiedEvent(event) {
  return !!(event.metaKey || event.altKey || event.ctrlKey || event.shiftKey);
}

/**
 * The public API for rendering a history-aware <a>.
 */
const Link = /*#__PURE__*/(0,react.forwardRef)(function LinkWithRef(_ref4, ref) {
  let {
    onClick,
    reloadDocument,
    replace = false,
    state,
    target,
    to
  } = _ref4,
      rest = _objectWithoutPropertiesLoose(_ref4, _excluded);

  let href = useHref(to);
  let internalOnClick = useLinkClickHandler(to, {
    replace,
    state,
    target
  });

  function handleClick(event) {
    if (onClick) onClick(event);

    if (!event.defaultPrevented && !reloadDocument) {
      internalOnClick(event);
    }
  }

  return (
    /*#__PURE__*/
    // eslint-disable-next-line jsx-a11y/anchor-has-content
    (0,react.createElement)("a", _extends({}, rest, {
      href: href,
      onClick: handleClick,
      ref: ref,
      target: target
    }))
  );
});

if (false) {}

/**
 * A <Link> wrapper that knows if it's "active" or not.
 */
const NavLink = /*#__PURE__*/(0,react.forwardRef)(function NavLinkWithRef(_ref5, ref) {
  let {
    "aria-current": ariaCurrentProp = "page",
    caseSensitive = false,
    className: classNameProp = "",
    end = false,
    style: styleProp,
    to,
    children
  } = _ref5,
      rest = _objectWithoutPropertiesLoose(_ref5, _excluded2);

  let location = useLocation();
  let path = useResolvedPath(to);
  let locationPathname = location.pathname;
  let toPathname = path.pathname;

  if (!caseSensitive) {
    locationPathname = locationPathname.toLowerCase();
    toPathname = toPathname.toLowerCase();
  }

  let isActive = locationPathname === toPathname || !end && locationPathname.startsWith(toPathname) && locationPathname.charAt(toPathname.length) === "/";
  let ariaCurrent = isActive ? ariaCurrentProp : undefined;
  let className;

  if (typeof classNameProp === "function") {
    className = classNameProp({
      isActive
    });
  } else {
    // If the className prop is not a function, we use a default `active`
    // class for <NavLink />s that are active. In v5 `active` was the default
    // value for `activeClassName`, but we are removing that API and can still
    // use the old default behavior for a cleaner upgrade path and keep the
    // simple styling rules working as they currently do.
    className = [classNameProp, isActive ? "active" : null].filter(Boolean).join(" ");
  }

  let style = typeof styleProp === "function" ? styleProp({
    isActive
  }) : styleProp;
  return /*#__PURE__*/(0,react.createElement)(Link, _extends({}, rest, {
    "aria-current": ariaCurrent,
    className: className,
    ref: ref,
    style: style,
    to: to
  }), typeof children === "function" ? children({
    isActive
  }) : children);
});

if (false) {} ////////////////////////////////////////////////////////////////////////////////
// HOOKS
////////////////////////////////////////////////////////////////////////////////

/**
 * Handles the click behavior for router `<Link>` components. This is useful if
 * you need to create custom `<Link>` components with the same click behavior we
 * use in our exported `<Link>`.
 */


function useLinkClickHandler(to, _temp) {
  let {
    target,
    replace: replaceProp,
    state
  } = _temp === void 0 ? {} : _temp;
  let navigate = useNavigate();
  let location = useLocation();
  let path = useResolvedPath(to);
  return (0,react.useCallback)(event => {
    if (event.button === 0 && ( // Ignore everything but left clicks
    !target || target === "_self") && // Let browser handle "target=_blank" etc.
    !isModifiedEvent(event) // Ignore clicks with modifier keys
    ) {
      event.preventDefault(); // If the URL hasn't changed, a regular <a> will do a replace instead of
      // a push, so do the same here.

      let replace = !!replaceProp || createPath(location) === createPath(path);
      navigate(to, {
        replace,
        state
      });
    }
  }, [location, navigate, path, replaceProp, state, target, to]);
}
/**
 * A convenient wrapper for reading and writing search parameters via the
 * URLSearchParams interface.
 */

function useSearchParams(defaultInit) {
   false ? 0 : void 0;
  let defaultSearchParamsRef = (0,react.useRef)(createSearchParams(defaultInit));
  let location = useLocation();
  let searchParams = (0,react.useMemo)(() => {
    let searchParams = createSearchParams(location.search);

    for (let key of defaultSearchParamsRef.current.keys()) {
      if (!searchParams.has(key)) {
        defaultSearchParamsRef.current.getAll(key).forEach(value => {
          searchParams.append(key, value);
        });
      }
    }

    return searchParams;
  }, [location.search]);
  let navigate = useNavigate();
  let setSearchParams = (0,react.useCallback)((nextInit, navigateOptions) => {
    navigate("?" + createSearchParams(nextInit), navigateOptions);
  }, [navigate]);
  return [searchParams, setSearchParams];
}

/**
 * Creates a URLSearchParams object using the given initializer.
 *
 * This is identical to `new URLSearchParams(init)` except it also
 * supports arrays as values in the object form of the initializer
 * instead of just strings. This is convenient when you need multiple
 * values for a given key, but don't want to use an array initializer.
 *
 * For example, instead of:
 *
 *   let searchParams = new URLSearchParams([
 *     ['sort', 'name'],
 *     ['sort', 'price']
 *   ]);
 *
 * you can do:
 *
 *   let searchParams = createSearchParams({
 *     sort: ['name', 'price']
 *   });
 */
function createSearchParams(init) {
  if (init === void 0) {
    init = "";
  }

  return new URLSearchParams(typeof init === "string" || Array.isArray(init) || init instanceof URLSearchParams ? init : Object.keys(init).reduce((memo, key) => {
    let value = init[key];
    return memo.concat(Array.isArray(value) ? value.map(v => [key, v]) : [[key, value]]);
  }, []));
}


//# sourceMappingURL=index.js.map


/***/ }),

/***/ 7462:
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

"use strict";
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Z": () => (/* binding */ _extends)
/* harmony export */ });
function _extends() {
  _extends = Object.assign || function (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];

      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }

    return target;
  };

  return _extends.apply(this, arguments);
}

/***/ })

},
/******/ __webpack_require__ => { // webpackRuntimeModules
/******/ var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
/******/ __webpack_require__.O(0, [394], () => (__webpack_exec__(6068), __webpack_exec__(1131), __webpack_exec__(5071)));
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=source_maps/shared.06487c113519a9e8d78e.js.map