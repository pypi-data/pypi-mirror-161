import { PKMap } from './store';
interface Options {
    app_model?: string;
    search?: string;
    page?: string | number;
    orders?: string[];
}
declare const ResultOptionsAtom: import("jotai").WritableAtom<Options, Options, void>;
declare const BraceResultAtom: import("jotai").WritableAtom<Promise<import("../../models/BraceList").BL_ResultModel | "loading">, unknown, Promise<void>>;
export { BraceResultAtom, ResultOptionsAtom };
export { PKMap as PKMapAtom };
//# sourceMappingURL=result.d.ts.map