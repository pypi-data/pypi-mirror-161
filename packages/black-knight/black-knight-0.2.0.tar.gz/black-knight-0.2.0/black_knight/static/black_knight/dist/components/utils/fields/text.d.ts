import { FC } from 'react';
import { FieldProps } from '.';
import { CharFieldModel, TextFieldModel } from 'state';
declare type TChar = FC<FieldProps<CharFieldModel>>;
declare const CharField: TChar;
declare type TText = FC<FieldProps<TextFieldModel>>;
declare const TextField: TText;
export { CharField, TextField };
//# sourceMappingURL=text.d.ts.map