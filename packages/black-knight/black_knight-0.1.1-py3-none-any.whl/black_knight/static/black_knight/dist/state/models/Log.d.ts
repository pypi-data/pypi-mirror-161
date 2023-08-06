interface LogModel {
    user: string;
    flag: LogFlag;
    time: string;
    message: string;
    repr: string;
    url: null;
    content_type: string;
}
declare enum LogFlag {
    ADDITION = 1,
    CHANGE = 2,
    DELETION = 3
}
export { LogModel, LogFlag };
//# sourceMappingURL=Log.d.ts.map