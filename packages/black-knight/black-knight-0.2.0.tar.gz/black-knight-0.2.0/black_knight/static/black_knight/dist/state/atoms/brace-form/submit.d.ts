import { SubmitOptions } from 'state';
interface TArgs extends Omit<SubmitOptions, 'data'> {
    [k: `F_${string}`]: string | Blob;
}
declare const BFSData: import("jotai").WritableAtom<SubmitOptions, TArgs, void>;
export { BFSData };
//# sourceMappingURL=submit.d.ts.map