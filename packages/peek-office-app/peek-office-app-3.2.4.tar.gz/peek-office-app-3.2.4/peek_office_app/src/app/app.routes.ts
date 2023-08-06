import { pluginAppRoutes } from "@_peek/plugin-app-routes";
import { pluginCfgRoutes } from "@_peek/plugin-cfg-routes";
import { DeviceEnrolledGuard } from "@peek/peek_core_device";
import { LoggedInGuard } from "@peek/peek_core_user";
import { ConfigPage, HomePage, UnknownRoutePage } from "./pages";

export const staticRoutes = [
    {
        path: "peek_core_device",
        loadChildren: "@_peek/peek_core_device/device.module#DeviceModule",
    },
    {
        path: "peek_core_user",
        canActivate: [DeviceEnrolledGuard],
        loadChildren:
            "@_peek/peek_core_user/plugin-user.module#PluginUserModule",
    },
    // All routes require the device to be enrolled
    {
        path: "",
        canActivate: [DeviceEnrolledGuard, LoggedInGuard],
        children: [
            {
                path: "",
                component: HomePage,
            },
            ...pluginAppRoutes,
            ...pluginCfgRoutes,
        ],
    },
    {
        path: "config",
        component: ConfigPage,
    },
    {
        path: "**",
        component: UnknownRoutePage,
    },
];
