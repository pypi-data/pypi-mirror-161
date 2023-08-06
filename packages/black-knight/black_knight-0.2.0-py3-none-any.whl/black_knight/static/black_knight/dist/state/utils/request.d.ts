interface ResponseOk {
    ok: true;
    data: any;
}
interface ResponseError {
    ok: false;
    message: string;
    code: number;
}
declare type Response = ResponseOk | ResponseError;
interface RequestBase {
    url: string;
    method?: 'POST' | 'GET';
    signal?: AbortSignal;
}
interface RequestJson extends RequestBase {
    method: 'POST';
    body: Object;
}
interface RequestFormData extends RequestBase {
    method: 'POST';
    body: FormData;
}
declare type RequestProps = RequestJson | RequestFormData | RequestBase;
declare type TRequest = (props: RequestProps) => Promise<Response>;
declare const REQUEST: TRequest;
export { REQUEST };
//# sourceMappingURL=request.d.ts.map