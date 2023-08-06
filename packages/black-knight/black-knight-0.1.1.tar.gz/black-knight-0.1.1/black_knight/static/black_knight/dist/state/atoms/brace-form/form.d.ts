interface BraceFormArgs {
    app_label?: string;
    model_name?: string;
    end_url: 'add/' | string;
}
declare const BraceFormAtom: import("jotai").WritableAtom<Promise<import("../../models/BraceForm").BraceFormModel | "loading">, BraceFormArgs, Promise<void>>;
export { BraceFormAtom };
//# sourceMappingURL=form.d.ts.map