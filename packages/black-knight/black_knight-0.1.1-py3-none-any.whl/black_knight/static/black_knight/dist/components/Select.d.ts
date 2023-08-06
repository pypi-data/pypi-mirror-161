import { FC } from 'react';
import './style/select.scss';
interface Option {
    lable: string;
    value: unknown;
}
interface SelectProps {
    options: Option[];
    defaultOpt?: Option;
    onChange?: (opt: Option) => void;
    zIndex?: number;
}
declare const Select: FC<SelectProps>;
export { Select };
//# sourceMappingURL=Select.d.ts.map