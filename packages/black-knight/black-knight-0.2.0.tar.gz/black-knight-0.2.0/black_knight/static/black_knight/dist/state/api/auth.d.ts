declare const Logout: () => Promise<void>;
interface LoginData {
    username: string;
    password: string;
}
declare const Login: (body: LoginData) => Promise<boolean>;
export { Logout, Login };
//# sourceMappingURL=auth.d.ts.map