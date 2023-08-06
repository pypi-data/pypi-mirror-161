import { FC, HTMLAttributes } from 'react';
import { FieldModel } from 'state';
interface FieldProps<TF> extends HTMLAttributes<HTMLElement> {
    change: (v: string | Blob) => void;
    field: TF;
}
declare type TRenderField = FC<Omit<FieldProps<FieldModel>, 'change'>>;
declare const RenderField: TRenderField;
export * from './text';
export { FieldProps, RenderField };
//# sourceMappingURL=index.d.ts.map