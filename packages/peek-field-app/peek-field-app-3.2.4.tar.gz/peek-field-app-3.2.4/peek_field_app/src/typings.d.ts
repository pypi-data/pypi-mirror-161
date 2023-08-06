/* SystemJS module definition */
declare let module: {
    id: string;
};

declare let require: any;

declare module "worker-loader!*" {
    const content: any;
    export = content;
}
