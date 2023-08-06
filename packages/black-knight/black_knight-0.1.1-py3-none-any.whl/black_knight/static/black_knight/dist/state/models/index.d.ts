export * from './User';
export * from './Admin';
export * from './Log';
export * from './BraceList';
export * from './BraceForm';
export * from './Fields';
declare type PK = string | number;
declare type TLoading = ['loading', string];
declare type VImage = ['image', string | null];
declare type VDate = ['date', string];
declare type VDatetime = ['datetime', string];
declare type VLink = ['link', string];
declare type VForeignKey = ['foreign_key', PK, string];
declare type TBaseValue = string | number | boolean | null;
declare type TypedValues = VImage | VDate | VDatetime | VLink | VForeignKey;
declare type TValue = TBaseValue | TypedValues;
export { PK, TLoading, TValue, TBaseValue, TypedValues };
export { VImage, VDate, VDatetime, VLink, VForeignKey };
//# sourceMappingURL=index.d.ts.map