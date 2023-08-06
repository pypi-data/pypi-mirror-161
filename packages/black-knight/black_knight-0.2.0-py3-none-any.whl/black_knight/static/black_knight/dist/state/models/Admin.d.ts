interface AdminModel {
    apps: AppModel[];
}
interface AppModel {
    name: string;
    app_label: string;
    models: AppModelModel[];
}
interface AppModelModel {
    name: string;
    object_name: string;
    plural_name: string;
    icon: string | null;
    perms: PermsModel;
}
interface PermsModel {
    add: boolean;
    change: boolean;
    delete: boolean;
    view: boolean;
}
export { AdminModel, AppModel, AppModelModel, PermsModel };
declare const DefaultAdmin: AdminModel;
export { DefaultAdmin };
//# sourceMappingURL=Admin.d.ts.map