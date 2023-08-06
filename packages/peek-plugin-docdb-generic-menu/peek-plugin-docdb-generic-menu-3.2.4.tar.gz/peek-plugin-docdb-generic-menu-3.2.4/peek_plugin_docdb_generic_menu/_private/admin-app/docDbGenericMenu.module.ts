import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditDocDbGenericMenuComponent } from "./edit-docdb-generic-menu-table/edit.component";
import { EditSettingComponent } from "./edit-setting-table/edit.component";

// Import our components
import { DocDbGenericMenuComponent } from "./docDbGenericMenu.component";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DocDbGenericMenuComponent,
    },
];

// Define the module
@NgModule({
    imports: [CommonModule, RouterModule.forChild(pluginRoutes), FormsModule],
    exports: [],
    providers: [],
    declarations: [
        DocDbGenericMenuComponent,
        EditDocDbGenericMenuComponent,
        EditSettingComponent,
    ],
})
export class DocDbGenericMenuModule {}
