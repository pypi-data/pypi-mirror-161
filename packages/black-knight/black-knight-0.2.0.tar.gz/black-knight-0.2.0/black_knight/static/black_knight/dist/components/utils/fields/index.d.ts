import { FC, HTMLAttributes, ReactNode } from 'react';
import { FieldModel } from 'state';
interface FieldProps<TF> extends HTMLAttributes<HTMLElement> {
    change: (v: string | Blob) => void;
    field: TF;
}
declare type TRenderField = FC<Omit<FieldProps<FieldModel>, 'change'>>;
declare const RenderField: TRenderField;
interface SelectProps<choice> extends HTMLAttributes<HTMLSelectElement> {
    choices: choice[];
    get_label: (c: choice, i: number) => ReactNode;
    get_value: (c: choice, i: number) => string | number;
}
declare function ChoicesField<choice>(props: SelectProps<choice>): JSX.Element;
export * from './text';
export { FieldProps, RenderField, ChoicesField };
//# sourceMappingURL=index.d.ts.map